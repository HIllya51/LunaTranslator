"""
LunaTranslator Overlay - Decky Plugin Backend
Connects to LunaTranslator running in Wine and provides translation overlay in Gaming Mode
"""

import asyncio
import json
import logging
import os
from typing import Optional, Callable

# Decky imports
import decky

# WebSocket client
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

logging.basicConfig(
    level=logging.INFO,
    format="[LunaTranslator] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_SETTINGS = {
    "enabled": True,
    "host": "127.0.0.1",
    "port": 8080,
    "show_original": True,
    "show_translation": True,
    "position": "bottom",  # top, bottom, left, right
    "font_size": 18,
    "background_opacity": 0.8,
    "text_color": "#ffffff",
    "background_color": "#000000",
    "original_color": "#aaaaaa",
    "max_lines": 5,
    "auto_hide_seconds": 10,
    "width_percent": 80,
}


class LunaTranslatorBridge:
    """Manages WebSocket connection to LunaTranslator"""

    def __init__(self):
        self.ws_origin: Optional[object] = None
        self.ws_trans: Optional[object] = None
        self.connected = False
        self.last_original = ""
        self.last_translation = ""
        self.on_text_callback: Optional[Callable] = None
        self._tasks: list = []

    async def connect(self, host: str, port: int) -> bool:
        """Connect to LunaTranslator WebSocket endpoints"""
        if not HAS_WEBSOCKETS:
            logger.error("websockets library not available")
            return False

        try:
            uri_origin = f"ws://{host}:{port}/api/ws/text/origin"
            uri_trans = f"ws://{host}:{port}/api/ws/text/trans"

            logger.info(f"Connecting to LunaTranslator at {host}:{port}")

            self.ws_origin = await websockets.connect(uri_origin)
            self.ws_trans = await websockets.connect(uri_trans)

            self.connected = True
            logger.info("Connected to LunaTranslator successfully")

            # Start listening tasks
            task_origin = asyncio.create_task(self._listen_origin())
            task_trans = asyncio.create_task(self._listen_trans())
            self._tasks = [task_origin, task_trans]

            return True

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from LunaTranslator"""
        self.connected = False

        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._tasks = []

        if self.ws_origin:
            await self.ws_origin.close()
            self.ws_origin = None

        if self.ws_trans:
            await self.ws_trans.close()
            self.ws_trans = None

        logger.info("Disconnected from LunaTranslator")

    async def _listen_origin(self):
        """Listen for original text from LunaTranslator"""
        try:
            async for message in self.ws_origin:
                self.last_original = message
                logger.debug(f"Original: {message[:50]}...")
                if self.on_text_callback:
                    await self.on_text_callback("original", message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Origin WebSocket connection closed")
            self.connected = False
        except Exception as e:
            logger.error(f"Error in origin listener: {e}")
            self.connected = False

    async def _listen_trans(self):
        """Listen for translated text from LunaTranslator"""
        try:
            async for message in self.ws_trans:
                self.last_translation = message
                logger.debug(f"Translation: {message[:50]}...")
                if self.on_text_callback:
                    await self.on_text_callback("translation", message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Translation WebSocket connection closed")
            self.connected = False
        except Exception as e:
            logger.error(f"Error in translation listener: {e}")
            self.connected = False


class Plugin:
    """Main Decky Plugin class"""

    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.bridge = LunaTranslatorBridge()
        self.settings_path = os.path.join(decky.DECKY_PLUGIN_SETTINGS_DIR, "settings.json")
        self._pending_texts = []

    async def _main(self):
        """Plugin entry point"""
        logger.info("LunaTranslator Overlay plugin loaded")
        await self.load_settings()

        # Set callback to notify frontend
        self.bridge.on_text_callback = self._on_text_received

        # Auto-connect if enabled
        if self.settings.get("enabled", True):
            await self.connect()

    async def _unload(self):
        """Plugin cleanup"""
        logger.info("LunaTranslator Overlay plugin unloading")
        await self.bridge.disconnect()

    async def _on_text_received(self, text_type: str, text: str):
        """Handle received text - store for frontend polling"""
        self._pending_texts.append({
            "type": text_type,
            "text": text
        })
        # Keep only last 100 messages
        if len(self._pending_texts) > 100:
            self._pending_texts = self._pending_texts[-100:]

    # ==================== Settings ====================

    async def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.settings.update(saved)
                logger.info("Settings loaded")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")

    async def save_settings(self):
        """Save settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
            logger.info("Settings saved")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    async def get_settings(self) -> dict:
        """Get current settings"""
        return self.settings.copy()

    async def set_setting(self, key: str, value) -> bool:
        """Set a single setting"""
        if key in DEFAULT_SETTINGS:
            self.settings[key] = value
            await self.save_settings()
            return True
        return False

    async def set_settings(self, settings: dict) -> bool:
        """Set multiple settings"""
        for key, value in settings.items():
            if key in DEFAULT_SETTINGS:
                self.settings[key] = value
        await self.save_settings()
        return True

    async def reset_settings(self) -> dict:
        """Reset to default settings"""
        self.settings = DEFAULT_SETTINGS.copy()
        await self.save_settings()
        return self.settings

    # ==================== Connection ====================

    async def connect(self) -> bool:
        """Connect to LunaTranslator"""
        host = self.settings.get("host", "127.0.0.1")
        port = self.settings.get("port", 8080)
        return await self.bridge.connect(host, port)

    async def disconnect(self) -> bool:
        """Disconnect from LunaTranslator"""
        await self.bridge.disconnect()
        return True

    async def is_connected(self) -> bool:
        """Check connection status"""
        return self.bridge.connected

    async def get_connection_info(self) -> dict:
        """Get connection information"""
        return {
            "connected": self.bridge.connected,
            "host": self.settings.get("host"),
            "port": self.settings.get("port"),
            "has_websockets": HAS_WEBSOCKETS
        }

    # ==================== Text Data ====================

    async def get_latest_text(self) -> dict:
        """Get the latest original and translated text"""
        return {
            "original": self.bridge.last_original,
            "translation": self.bridge.last_translation
        }

    async def get_pending_texts(self) -> list:
        """Get and clear pending text messages"""
        texts = self._pending_texts.copy()
        self._pending_texts = []
        return texts

    async def clear_texts(self) -> bool:
        """Clear stored texts"""
        self.bridge.last_original = ""
        self.bridge.last_translation = ""
        self._pending_texts = []
        return True

    # ==================== Utility ====================

    async def test_connection(self, host: str, port: int) -> dict:
        """Test connection to a specific host:port"""
        if not HAS_WEBSOCKETS:
            return {"success": False, "error": "websockets library not installed"}

        try:
            uri = f"ws://{host}:{port}/api/ws/text/origin"
            async with websockets.connect(uri, close_timeout=5) as ws:
                await ws.close()
            return {"success": True, "message": f"Successfully connected to {host}:{port}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_plugin_info(self) -> dict:
        """Get plugin information"""
        return {
            "name": "LunaTranslator Overlay",
            "version": "1.0.0",
            "author": "AnulTranslator",
            "has_websockets": HAS_WEBSOCKETS,
            "settings_path": self.settings_path
        }
