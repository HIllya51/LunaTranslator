# LunaTranslator Overlay - Decky Plugin

Plugin do Decky Loader para exibir traduções do LunaTranslator no Gaming Mode do Steam Deck.

## Como Funciona

```
┌─────────────────────────────────────────────────────────────┐
│ Wine Prefix (Lutris)                                        │
│  ├── Visual Novel (jogo)                                    │
│  └── LunaTranslator (captura e traduz texto)               │
│         │                                                   │
│         └── WebSocket Server (porta 8080)                   │
└─────────────┬───────────────────────────────────────────────┘
              │ localhost:8080
              ↓
┌─────────────────────────────────────────────────────────────┐
│ Steam Deck (Linux)                                          │
│  └── Decky Plugin                                           │
│        ├── WebSocket Client (conecta ao LunaTranslator)     │
│        └── Overlay (exibe tradução no Gaming Mode)          │
└─────────────────────────────────────────────────────────────┘
```

## Requisitos

- Steam Deck (ou PC Linux com Steam no Gaming Mode)
- [Decky Loader](https://decky.xyz/) instalado
- LunaTranslator rodando via Wine/Lutris
- Python 3.10+ com `websockets`

## Instalação

### Método 1: Script Automático

```bash
cd decky-plugin-lunatranslator
chmod +x install.sh
./install.sh
```

### Método 2: Manual

1. **Build o plugin:**
   ```bash
   cd decky-plugin-lunatranslator
   pnpm install
   pnpm build
   ```

2. **Copie para Decky:**
   ```bash
   cp -r . ~/homebrew/plugins/LunaTranslator\ Overlay/
   ```

3. **Instale dependência Python:**
   ```bash
   pip install --user websockets
   ```

4. **Reinicie o Steam**

## Configuração do LunaTranslator

Para que o plugin funcione, você precisa habilitar o servidor de rede no LunaTranslator:

1. Abra LunaTranslator no Wine/Lutris
2. Vá em **Configurações** → **Rede/Network**
3. Habilite **"Serviço de Rede"** ou **"Network Service"**
4. Configure a porta (padrão: `8080`)
5. Certifique-se que o serviço está escutando em `0.0.0.0` ou `127.0.0.1`

### Verificar se está funcionando

No terminal do Steam Deck (Desktop Mode):

```bash
# Teste a conexão WebSocket
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: test" \
  -H "Sec-WebSocket-Version: 13" \
  http://127.0.0.1:8080/api/ws/text/origin
```

## Uso

1. Inicie seu jogo pelo Lutris/Steam (com LunaTranslator rodando)
2. Pressione o botão **...** (Quick Access) no Steam Deck
3. Encontre **LunaTranslator** na lista de plugins Decky
4. Configure host/porta e clique em **Connect**
5. As traduções aparecerão automaticamente sobre o jogo!

## Configurações Disponíveis

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| **Host** | IP do LunaTranslator | `127.0.0.1` |
| **Port** | Porta do serviço | `8080` |
| **Show Original** | Exibir texto original | ✓ |
| **Show Translation** | Exibir tradução | ✓ |
| **Position** | Posição do overlay | `bottom` |
| **Font Size** | Tamanho da fonte | `18` |
| **Width %** | Largura do overlay | `80%` |
| **Background Opacity** | Opacidade do fundo | `0.8` |
| **Auto-hide** | Esconder após X segundos | `10s` |

## Estrutura do Projeto

```
decky-plugin-lunatranslator/
├── main.py              # Backend Python (WebSocket client)
├── src/
│   └── index.tsx        # Frontend React (overlay + settings)
├── plugin.json          # Metadados do plugin
├── package.json         # Dependências Node.js
├── tsconfig.json        # Configuração TypeScript
├── rollup.config.js     # Build config
├── defaults/
│   └── defaults.json    # Configurações padrão
├── requirements.txt     # Dependências Python
├── install.sh           # Script de instalação
├── uninstall.sh         # Script de desinstalação
└── README.md            # Este arquivo
```

## Troubleshooting

### "websockets not installed"

```bash
pip install --user websockets
# ou
pip3 install websockets
```

### "Connection failed"

1. Verifique se o LunaTranslator está rodando
2. Verifique se o serviço de rede está habilitado
3. Teste manualmente:
   ```bash
   python3 -c "import asyncio, websockets; asyncio.run(websockets.connect('ws://127.0.0.1:8080/api/ws/text/origin'))"
   ```

### Overlay não aparece

1. Verifique se "Enable Overlay" está ativado
2. Verifique se está conectado (status: Connected)
3. Verifique os logs: `~/homebrew/logs/LunaTranslator Overlay/`

### Problemas de rede Wine ↔ Linux

Se o LunaTranslator no Wine não consegue ser acessado:

```bash
# Verifique se a porta está escutando
ss -tlnp | grep 8080

# Se necessário, use o IP do Wine bridge
ip addr show | grep wine
```

## Desenvolvimento

### Build

```bash
pnpm install
pnpm build
```

### Watch mode (desenvolvimento)

```bash
pnpm watch
```

### Deploy para teste

```bash
pnpm build && cp -r dist main.py plugin.json ~/homebrew/plugins/LunaTranslator\ Overlay/
```

## Licença

GPL-3.0 (mesma licença do LunaTranslator original)

## Créditos

- [LunaTranslator](https://github.com/HIllya51/LunaTranslator) - O tradutor de visual novels
- [Decky Loader](https://decky.xyz/) - Framework de plugins para Steam Deck
