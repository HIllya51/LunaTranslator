import {
  definePlugin,
  PanelSection,
  PanelSectionRow,
  ButtonItem,
  SliderField,
  ToggleField,
  TextField,
  DropdownItem,
  staticClasses,
} from "@decky/ui";
import { callable, routerHook } from "@decky/api";
import { useState, useEffect, useCallback, VFC } from "react";
import { FaLanguage, FaPlug, FaCog, FaTrash } from "react-icons/fa";

// ==================== Types ====================

interface Settings {
  enabled: boolean;
  host: string;
  port: number;
  show_original: boolean;
  show_translation: boolean;
  position: string;
  font_size: number;
  background_opacity: number;
  text_color: string;
  background_color: string;
  original_color: string;
  max_lines: number;
  auto_hide_seconds: number;
  width_percent: number;
}

interface TextData {
  original: string;
  translation: string;
}

interface ConnectionInfo {
  connected: boolean;
  host: string;
  port: number;
  has_websockets: boolean;
}

// ==================== Backend Calls ====================

const getSettings = callable<[], Settings>("get_settings");
const setSetting = callable<[string, unknown], boolean>("set_setting");
const setSettings = callable<[Settings], boolean>("set_settings");
const resetSettings = callable<[], Settings>("reset_settings");
const connect = callable<[], boolean>("connect");
const disconnect = callable<[], boolean>("disconnect");
const isConnected = callable<[], boolean>("is_connected");
const getConnectionInfo = callable<[], ConnectionInfo>("get_connection_info");
const getLatestText = callable<[], TextData>("get_latest_text");
const getPendingTexts = callable<[], Array<{ type: string; text: string }>>("get_pending_texts");
const clearTexts = callable<[], boolean>("clear_texts");
const testConnection = callable<[string, number], { success: boolean; error?: string }>("test_connection");

// ==================== Overlay Component ====================

const TranslationOverlay: VFC<{ settings: Settings }> = ({ settings }) => {
  const [textData, setTextData] = useState<TextData>({ original: "", translation: "" });
  const [visible, setVisible] = useState(false);
  const [hideTimeout, setHideTimeout] = useState<ReturnType<typeof setTimeout> | null>(null);

  // Poll for new texts
  useEffect(() => {
    if (!settings.enabled) return;

    const pollInterval = setInterval(async () => {
      try {
        const texts = await getPendingTexts();
        if (texts.length > 0) {
          // Process latest texts
          for (const item of texts) {
            if (item.type === "original") {
              setTextData((prev) => ({ ...prev, original: item.text }));
            } else if (item.type === "translation") {
              setTextData((prev) => ({ ...prev, translation: item.text }));
            }
          }
          setVisible(true);

          // Reset auto-hide timer
          if (hideTimeout) clearTimeout(hideTimeout);
          if (settings.auto_hide_seconds > 0) {
            const timeout = setTimeout(() => setVisible(false), settings.auto_hide_seconds * 1000);
            setHideTimeout(timeout);
          }
        }
      } catch (e) {
        console.error("[LunaTranslator] Poll error:", e);
      }
    }, 200);

    return () => {
      clearInterval(pollInterval);
      if (hideTimeout) clearTimeout(hideTimeout);
    };
  }, [settings.enabled, settings.auto_hide_seconds]);

  if (!settings.enabled || !visible) return null;

  const positionStyles: Record<string, React.CSSProperties> = {
    top: { top: 0, left: "50%", transform: "translateX(-50%)" },
    bottom: { bottom: 0, left: "50%", transform: "translateX(-50%)" },
    left: { left: 0, top: "50%", transform: "translateY(-50%)" },
    right: { right: 0, top: "50%", transform: "translateY(-50%)" },
  };

  const containerStyle: React.CSSProperties = {
    position: "fixed",
    zIndex: 9999,
    padding: "12px 20px",
    borderRadius: "8px",
    maxWidth: `${settings.width_percent}%`,
    maxHeight: "40%",
    overflow: "hidden",
    backgroundColor: `${settings.background_color}${Math.round(settings.background_opacity * 255).toString(16).padStart(2, "0")}`,
    color: settings.text_color,
    fontSize: `${settings.font_size}px`,
    fontFamily: "sans-serif",
    textAlign: "center",
    boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
    ...positionStyles[settings.position],
  };

  const originalStyle: React.CSSProperties = {
    color: settings.original_color,
    fontSize: `${settings.font_size * 0.85}px`,
    marginBottom: "8px",
    opacity: 0.9,
  };

  const translationStyle: React.CSSProperties = {
    color: settings.text_color,
    fontSize: `${settings.font_size}px`,
    fontWeight: "bold",
  };

  return (
    <div style={containerStyle}>
      {settings.show_original && textData.original && (
        <div style={originalStyle}>{textData.original}</div>
      )}
      {settings.show_translation && textData.translation && (
        <div style={translationStyle}>{textData.translation}</div>
      )}
    </div>
  );
};

// ==================== Settings Panel ====================

const SettingsPanel: VFC = () => {
  const [settings, setSettingsState] = useState<Settings | null>(null);
  const [connectionInfo, setConnectionInfo] = useState<ConnectionInfo | null>(null);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<string>("");

  // Load settings
  const loadSettings = useCallback(async () => {
    try {
      const s = await getSettings();
      setSettingsState(s);
      const info = await getConnectionInfo();
      setConnectionInfo(info);
    } catch (e) {
      console.error("[LunaTranslator] Failed to load settings:", e);
    }
  }, []);

  useEffect(() => {
    loadSettings();
    const interval = setInterval(async () => {
      const info = await getConnectionInfo();
      setConnectionInfo(info);
    }, 2000);
    return () => clearInterval(interval);
  }, [loadSettings]);

  const updateSetting = async (key: keyof Settings, value: unknown) => {
    if (!settings) return;
    await setSetting(key, value);
    setSettingsState({ ...settings, [key]: value });
  };

  const handleConnect = async () => {
    const result = await connect();
    const info = await getConnectionInfo();
    setConnectionInfo(info);
    return result;
  };

  const handleDisconnect = async () => {
    await disconnect();
    const info = await getConnectionInfo();
    setConnectionInfo(info);
  };

  const handleTest = async () => {
    if (!settings) return;
    setTesting(true);
    setTestResult("");
    try {
      const result = await testConnection(settings.host, settings.port);
      setTestResult(result.success ? "Connection successful!" : `Failed: ${result.error}`);
    } catch (e) {
      setTestResult(`Error: ${e}`);
    }
    setTesting(false);
  };

  const handleReset = async () => {
    const s = await resetSettings();
    setSettingsState(s);
  };

  const handleClearTexts = async () => {
    await clearTexts();
  };

  if (!settings) {
    return (
      <PanelSection title="Loading...">
        <PanelSectionRow>Loading settings...</PanelSectionRow>
      </PanelSection>
    );
  }

  const positionOptions = [
    { data: "top", label: "Top" },
    { data: "bottom", label: "Bottom" },
    { data: "left", label: "Left" },
    { data: "right", label: "Right" },
  ];

  return (
    <>
      {/* Connection Section */}
      <PanelSection title="Connection">
        <PanelSectionRow>
          <ToggleField
            label="Enable Overlay"
            checked={settings.enabled}
            onChange={(val) => updateSetting("enabled", val)}
          />
        </PanelSectionRow>

        <PanelSectionRow>
          <TextField
            label="LunaTranslator Host"
            value={settings.host}
            onChange={(e) => updateSetting("host", e.target.value)}
          />
        </PanelSectionRow>

        <PanelSectionRow>
          <SliderField
            label="Port"
            value={settings.port}
            min={1024}
            max={65535}
            step={1}
            showValue
            onChange={(val) => updateSetting("port", val)}
          />
        </PanelSectionRow>

        <PanelSectionRow>
          <div style={{ display: "flex", gap: "8px" }}>
            {connectionInfo?.connected ? (
              <ButtonItem layout="below" onClick={handleDisconnect}>
                <FaPlug /> Disconnect
              </ButtonItem>
            ) : (
              <ButtonItem layout="below" onClick={handleConnect}>
                <FaPlug /> Connect
              </ButtonItem>
            )}
            <ButtonItem layout="below" onClick={handleTest} disabled={testing}>
              {testing ? "Testing..." : "Test"}
            </ButtonItem>
          </div>
        </PanelSectionRow>

        {testResult && (
          <PanelSectionRow>
            <div style={{ color: testResult.includes("successful") ? "#4caf50" : "#f44336" }}>
              {testResult}
            </div>
          </PanelSectionRow>
        )}

        <PanelSectionRow>
          <div style={{ fontSize: "12px", opacity: 0.7 }}>
            Status: {connectionInfo?.connected ? "Connected" : "Disconnected"}
            {!connectionInfo?.has_websockets && " (websockets not installed)"}
          </div>
        </PanelSectionRow>
      </PanelSection>

      {/* Display Section */}
      <PanelSection title="Display">
        <PanelSectionRow>
          <ToggleField
            label="Show Original Text"
            checked={settings.show_original}
            onChange={(val) => updateSetting("show_original", val)}
          />
        </PanelSectionRow>

        <PanelSectionRow>
          <ToggleField
            label="Show Translation"
            checked={settings.show_translation}
            onChange={(val) => updateSetting("show_translation", val)}
          />
        </PanelSectionRow>

        <PanelSectionRow>
          <DropdownItem
            label="Position"
            rgOptions={positionOptions}
            selectedOption={positionOptions.find((o) => o.data === settings.position)?.data}
            onChange={(option) => updateSetting("position", option.data)}
          />
        </PanelSectionRow>

        <PanelSectionRow>
          <SliderField
            label="Font Size"
            value={settings.font_size}
            min={10}
            max={40}
            step={1}
            showValue
            onChange={(val) => updateSetting("font_size", val)}
          />
        </PanelSectionRow>

        <PanelSectionRow>
          <SliderField
            label="Width %"
            value={settings.width_percent}
            min={20}
            max={100}
            step={5}
            showValue
            onChange={(val) => updateSetting("width_percent", val)}
          />
        </PanelSectionRow>

        <PanelSectionRow>
          <SliderField
            label="Background Opacity"
            value={settings.background_opacity}
            min={0}
            max={1}
            step={0.1}
            showValue
            onChange={(val) => updateSetting("background_opacity", val)}
          />
        </PanelSectionRow>

        <PanelSectionRow>
          <SliderField
            label="Auto-hide (seconds, 0=never)"
            value={settings.auto_hide_seconds}
            min={0}
            max={60}
            step={1}
            showValue
            onChange={(val) => updateSetting("auto_hide_seconds", val)}
          />
        </PanelSectionRow>
      </PanelSection>

      {/* Actions Section */}
      <PanelSection title="Actions">
        <PanelSectionRow>
          <ButtonItem layout="below" onClick={handleClearTexts}>
            <FaTrash /> Clear Texts
          </ButtonItem>
        </PanelSectionRow>

        <PanelSectionRow>
          <ButtonItem layout="below" onClick={handleReset}>
            <FaCog /> Reset to Defaults
          </ButtonItem>
        </PanelSectionRow>
      </PanelSection>
    </>
  );
};

// ==================== Plugin Definition ====================

export default definePlugin(() => {
  const [settings, setSettings] = useState<Settings | null>(null);

  // Load settings on mount
  useEffect(() => {
    getSettings().then(setSettings);
  }, []);

  // Register overlay route
  routerHook.addGlobalComponent("LunaTranslatorOverlay", () => {
    const [currentSettings, setCurrentSettings] = useState<Settings | null>(null);

    useEffect(() => {
      getSettings().then(setCurrentSettings);
      // Poll for settings changes
      const interval = setInterval(() => {
        getSettings().then(setCurrentSettings);
      }, 5000);
      return () => clearInterval(interval);
    }, []);

    if (!currentSettings) return null;
    return <TranslationOverlay settings={currentSettings} />;
  });

  return {
    name: "LunaTranslator Overlay",
    title: <div className={staticClasses.Title}>LunaTranslator</div>,
    content: <SettingsPanel />,
    icon: <FaLanguage />,
    onDismount() {
      routerHook.removeGlobalComponent("LunaTranslatorOverlay");
    },
  };
});
