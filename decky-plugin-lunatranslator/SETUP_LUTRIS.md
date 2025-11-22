# Configuração do LunaTranslator no Lutris para Steam Deck

Guia passo a passo para configurar o LunaTranslator no Lutris e usar com o plugin Decky.

## 1. Pré-requisitos

- Steam Deck em Desktop Mode
- Lutris instalado (via Discover/Flatpak)
- LunaTranslator baixado (versão Windows)

## 2. Configuração do Wine Prefix

### Criar prefix dedicado

```bash
# Criar diretório para o prefix
mkdir -p ~/.wine-lunatranslator

# Configurar o prefix (via Lutris ou winetricks)
WINEPREFIX=~/.wine-lunatranslator winecfg
```

### Configuração recomendada

- **Windows Version:** Windows 7 ou 10
- **DPI:** 96 (ou ajuste para sua tela)

## 3. Adicionar LunaTranslator no Lutris

1. Abra **Lutris**
2. Clique no **+** (Add Game)
3. Selecione **"Add locally installed game"**
4. Preencha:
   - **Name:** LunaTranslator
   - **Runner:** Wine
   - **Executable:** Caminho para `LunaTranslator.exe`
   - **Wine prefix:** `~/.wine-lunatranslator`

### Opções avançadas do Wine

No Lutris, vá em **Configure** → **Runner Options**:

```
Wine version: wine-ge-8-xx (ou lutris-7.x)
DXVK: Desabilitado (não é necessário)
VKD3D: Desabilitado
Esync: Habilitado
Fsync: Habilitado (se suportado)
```

## 4. Habilitar Serviço de Rede no LunaTranslator

**IMPORTANTE:** Este passo é essencial para o plugin Decky funcionar!

1. Inicie o LunaTranslator pelo Lutris
2. Vá em **Settings** (ícone de engrenagem)
3. Procure por **"Network"** ou **"网络服务"**
4. Habilite **"Enable Network Service"**
5. Configure:
   - **Host:** `0.0.0.0` (para aceitar conexões de fora do Wine)
   - **Port:** `8080` (ou outra porta livre)

### Verificar configuração

O arquivo de config fica em:
```
~/.wine-lunatranslator/drive_c/users/<user>/AppData/Roaming/LunaTranslator/config.json
```

Deve conter algo como:
```json
{
  "network_service": {
    "use": true,
    "port": 8080,
    "host": "0.0.0.0"
  }
}
```

## 5. Configurar Jogo no Mesmo Prefix

Para usar o LunaTranslator com um jogo:

### Opção A: Adicionar jogo separado no Lutris

1. Adicione o jogo no Lutris
2. Configure para usar o **mesmo Wine prefix**: `~/.wine-lunatranslator`
3. Inicie LunaTranslator primeiro, depois o jogo

### Opção B: Script de inicialização

Crie um script que inicia ambos:

```bash
#!/bin/bash
# start-vn.sh

WINEPREFIX=~/.wine-lunatranslator
LUNA_PATH="$WINEPREFIX/drive_c/LunaTranslator/LunaTranslator.exe"
GAME_PATH="$WINEPREFIX/drive_c/Games/MeuJogo/game.exe"

# Inicia LunaTranslator em background
WINEPREFIX=$WINEPREFIX wine "$LUNA_PATH" &
sleep 3

# Inicia o jogo
WINEPREFIX=$WINEPREFIX wine "$GAME_PATH"
```

## 6. Adicionar ao Steam (para Gaming Mode)

### Via Lutris

1. No Lutris, clique com botão direito no jogo
2. Selecione **"Create Steam shortcut"**

### Manual

1. No Steam (Desktop Mode), vá em **Games** → **Add a Non-Steam Game**
2. Clique **Browse** e adicione o script ou executável
3. Configure os argumentos se necessário

## 7. Testar Conexão

No Desktop Mode, abra um terminal:

```bash
# Verificar se a porta está aberta
ss -tlnp | grep 8080

# Testar WebSocket
python3 << 'EOF'
import asyncio
import websockets

async def test():
    try:
        async with websockets.connect("ws://127.0.0.1:8080/api/ws/text/origin") as ws:
            print("Conectado com sucesso!")
            await ws.close()
    except Exception as e:
        print(f"Erro: {e}")

asyncio.run(test())
EOF
```

## 8. Usar no Gaming Mode

1. Mude para **Gaming Mode**
2. Inicie seu jogo (que abre LunaTranslator junto)
3. Pressione **...** (Quick Access)
4. Abra **Decky** → **LunaTranslator**
5. Configure o Host/Port e clique **Connect**
6. Jogue! As traduções aparecerão automaticamente.

## Troubleshooting

### "Connection refused"

O LunaTranslator pode estar escutando apenas em `127.0.0.1` dentro do Wine.

**Solução:** Configure o host como `0.0.0.0` no LunaTranslator.

### Porta bloqueada

```bash
# Verificar firewall
sudo iptables -L -n | grep 8080

# Liberar porta se necessário
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

### Wine bridge network

Em alguns casos, o Wine usa uma interface de rede separada:

```bash
# Encontrar IP do Wine
ip addr show

# Procure por interfaces tipo 'virbr' ou IPs 192.168.x.x
```

Use esse IP no plugin Decky ao invés de `127.0.0.1`.

### Logs do LunaTranslator

```bash
# Verificar logs do Wine
cat ~/.wine-lunatranslator/*.log

# Ou no diretório do LunaTranslator
cat ~/.wine-lunatranslator/drive_c/LunaTranslator/logs/*.log
```

## Dicas de Performance

1. **Gamescope:** O Gaming Mode usa Gamescope automaticamente
2. **MangoHud:** Pode coexistir com o overlay do plugin
3. **FSR:** Funciona normalmente com o overlay
4. **TDP Limit:** Ajuste conforme necessário (visual novels não precisam de muito)

## Atalhos Úteis

| Ação | Atalho |
|------|--------|
| Abrir Quick Access | **...** |
| Alternar teclado | **Steam + X** |
| Screenshot | **Steam + R1** |
| Forçar fechar | **Steam + B** (segurar) |
