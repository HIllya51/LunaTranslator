# Guia Completo: LunaTranslator no Steam Deck

> Jogue Visual Novels japonesas no Steam Deck com tradução em tempo real no Gaming Mode!

---

## O que é isso?

Este plugin permite que você veja as traduções do **LunaTranslator** diretamente na tela do seu Steam Deck enquanto joga no **Gaming Mode** - sem precisar alternar entre janelas ou sair do jogo.

### Como funciona?

```
┌────────────────────────────────────────────────────────┐
│  WINE (Lutris/Proton)                                  │
│  ┌──────────────────┐    ┌───────────────────────┐    │
│  │  Visual Novel    │───▶│   LunaTranslator      │    │
│  │  (seu jogo)      │    │   (captura + traduz)  │    │
│  └──────────────────┘    └───────────┬───────────┘    │
└──────────────────────────────────────┼────────────────┘
                                       │ WebSocket
                                       ▼
┌────────────────────────────────────────────────────────┐
│  STEAM DECK (Gaming Mode)                              │
│  ┌──────────────────────────────────────────────┐     │
│  │          Plugin Decky                         │     │
│  │    ┌─────────────────────────────────┐       │     │
│  │    │  Overlay de Tradução            │       │     │
│  │    │  "Texto traduzido aparece aqui" │       │     │
│  │    └─────────────────────────────────┘       │     │
│  └──────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────┘
```

---

## Pré-requisitos

Antes de começar, você precisa ter:

- [ ] **Steam Deck** (ou PC com Linux + Steam Gaming Mode)
- [ ] **Decky Loader** instalado ([decky.xyz](https://decky.xyz))
- [ ] **Lutris** instalado (para rodar o LunaTranslator)
- [ ] **LunaTranslator** baixado (versão Windows)
- [ ] **Sua Visual Novel** instalada

---

## Parte 1: Instalando o Decky Loader

Se você ainda não tem o Decky Loader:

### Passo 1.1: Entrar no Desktop Mode

1. Pressione o botão **Steam** no seu Deck
2. Vá em **Power** (Energia)
3. Selecione **Switch to Desktop** (Alternar para Área de Trabalho)

### Passo 1.2: Instalar o Decky

1. Abra o navegador **Firefox** (ou Chromium)
2. Acesse: **https://decky.xyz**
3. Clique em **Download**
4. Execute o instalador baixado
5. Siga as instruções na tela

### Passo 1.3: Verificar instalação

1. Volte para o Gaming Mode
2. Pressione o botão **...** (Quick Access)
3. Você deve ver o ícone do **Decky** (uma tomada)

---

## Parte 2: Configurando o Lutris

### Passo 2.1: Instalar o Lutris

No Desktop Mode:

1. Abra o **Discover** (loja de aplicativos)
2. Pesquise por **Lutris**
3. Clique em **Install** (Instalar)

### Passo 2.2: Criar Wine Prefix dedicado

Recomendo usar um prefix separado para o LunaTranslator:

```bash
# Abra o Konsole (terminal) e execute:
mkdir -p ~/.wine-lunatranslator
```

### Passo 2.3: Adicionar LunaTranslator no Lutris

1. Abra o **Lutris**
2. Clique no **+** no canto superior esquerdo
3. Selecione **"Add locally installed game"**
4. Preencha:

| Campo | Valor |
|-------|-------|
| **Name** | LunaTranslator |
| **Runner** | Wine |
| **Wine prefix** | `~/.wine-lunatranslator` |
| **Executable** | Caminho para `LunaTranslator.exe` |

5. Clique em **Save**

### Passo 2.4: Configurar o Wine

1. No Lutris, clique com botão direito em **LunaTranslator**
2. Selecione **Configure**
3. Vá na aba **Runner options**
4. Configure:

| Opção | Valor Recomendado |
|-------|-------------------|
| **Wine version** | wine-ge-8-26 (ou mais recente) |
| **DXVK** | Desabilitado |
| **Esync** | Habilitado |
| **Fsync** | Habilitado |

5. Clique em **Save**

---

## Parte 3: Configurando o LunaTranslator

### Passo 3.1: Primeira execução

1. No Lutris, clique duas vezes em **LunaTranslator** para iniciar
2. Aguarde carregar (primeira vez pode demorar)

### Passo 3.2: Habilitar o Serviço de Rede (IMPORTANTE!)

**Este é o passo mais importante!** Sem isso, o plugin não consegue se conectar.

1. No LunaTranslator, clique no ícone de **engrenagem** (Settings)
2. Procure por **"网络服务"** ou **"Network Service"**
3. **Habilite** o serviço
4. Configure:

| Configuração | Valor |
|--------------|-------|
| **Enable** | ✓ (marcado) |
| **Host** | `0.0.0.0` |
| **Port** | `8080` |

5. **Reinicie** o LunaTranslator

### Passo 3.3: Verificar se está funcionando

Abra o Konsole e teste:

```bash
# Isso deve retornar algo (não um erro)
curl http://127.0.0.1:8080/
```

Se aparecer uma página HTML ou JSON, está funcionando!

---

## Parte 4: Instalando o Plugin Decky

### Passo 4.1: Baixar o plugin

```bash
# No Konsole, execute:
cd ~/Downloads
git clone https://github.com/tobidashite/AnulTranslator
cd AnulTranslator/decky-plugin-lunatranslator
```

### Passo 4.2: Instalar dependências e buildar

```bash
# Instalar Node.js se não tiver
sudo pacman -S nodejs npm

# Instalar pnpm
npm install -g pnpm

# Buildar o plugin
./build.sh
```

### Passo 4.3: Instalar o plugin

```bash
# Executar o instalador
./install.sh
```

### Passo 4.4: Reiniciar o Steam

1. Feche o Steam completamente
2. Abra novamente
3. Ou simplesmente reinicie o Steam Deck

---

## Parte 5: Configurando sua Visual Novel

### Opção A: Mesmo Wine Prefix (Recomendado)

Para o LunaTranslator funcionar com seu jogo, ambos precisam estar no **mesmo Wine prefix**.

1. No Lutris, adicione seu jogo
2. Configure para usar o mesmo prefix: `~/.wine-lunatranslator`

### Opção B: Script de inicialização

Crie um script que inicia tudo junto:

```bash
#!/bin/bash
# Salve como: ~/start-vn.sh

export WINEPREFIX=~/.wine-lunatranslator

# Inicia LunaTranslator em background
wine ~/.wine-lunatranslator/drive_c/LunaTranslator/LunaTranslator.exe &

# Espera 5 segundos
sleep 5

# Inicia o jogo
wine ~/.wine-lunatranslator/drive_c/Games/SeuJogo/game.exe
```

Torne executável:
```bash
chmod +x ~/start-vn.sh
```

### Opção C: Adicionar ao Steam

1. No Steam (Desktop Mode), vá em **Games** → **Add a Non-Steam Game**
2. Adicione o script ou o Lutris
3. Agora aparece na sua biblioteca!

---

## Parte 6: Usando no Gaming Mode

### Passo 6.1: Iniciar o jogo

1. Mude para **Gaming Mode** (Power → Switch to Gaming Mode)
2. Encontre seu jogo na biblioteca
3. Inicie o jogo (LunaTranslator deve abrir junto)

### Passo 6.2: Conectar o plugin

1. Pressione o botão **...** (três pontinhos)
2. Vá até o ícone do **Decky** (parece uma tomada)
3. Encontre **LunaTranslator** na lista
4. Verifique as configurações:
   - **Host:** `127.0.0.1`
   - **Port:** `8080`
5. Clique em **Connect**

### Passo 6.3: Jogar!

Agora, sempre que o LunaTranslator detectar e traduzir texto, a tradução aparecerá automaticamente na tela!

---

## Configurações do Overlay

Você pode personalizar como a tradução aparece:

| Configuração | Descrição | Valores |
|--------------|-----------|---------|
| **Enable Overlay** | Liga/desliga o overlay | On/Off |
| **Show Original** | Mostra texto japonês original | On/Off |
| **Show Translation** | Mostra tradução | On/Off |
| **Position** | Posição na tela | Top, Bottom, Left, Right |
| **Font Size** | Tamanho da fonte | 10-40 px |
| **Width %** | Largura do overlay | 20-100% |
| **Background Opacity** | Transparência do fundo | 0-100% |
| **Auto-hide** | Esconde após X segundos | 0-60s (0 = nunca) |

---

## Solução de Problemas

### "Connection failed" ou "Não conecta"

**Causa:** O LunaTranslator não está com o serviço de rede habilitado.

**Solução:**
1. Abra o LunaTranslator
2. Vá em Settings → Network
3. Habilite e configure Host: `0.0.0.0`, Port: `8080`
4. Reinicie o LunaTranslator

### "websockets not installed"

**Causa:** Biblioteca Python faltando.

**Solução:**
```bash
pip install websockets
# ou
pip3 install --user websockets
```

### O overlay não aparece

**Verificar:**
1. "Enable Overlay" está ativado?
2. Status mostra "Connected"?
3. O jogo está gerando texto? (teste com uma cena de diálogo)

### Texto aparece mas some muito rápido

**Solução:** Aumente o "Auto-hide" nas configurações (ex: 15-30 segundos).

### Performance ruim / lag

**Soluções:**
1. Reduza a taxa de polling (será adicionado em versão futura)
2. Use fonte menor
3. Desabilite "Show Original" para mostrar só a tradução

### LunaTranslator não detecta o jogo

**Isso é um problema do LunaTranslator, não do plugin.**

Soluções:
1. Certifique-se que jogo e LunaTranslator estão no mesmo Wine prefix
2. No LunaTranslator, use "Attach to Process" manualmente
3. Tente diferentes hooks no LunaTranslator

---

## Dicas e Truques

### Atalhos úteis no Steam Deck

| Ação | Atalho |
|------|--------|
| Abrir Quick Access (Decky) | **...** |
| Teclado virtual | **Steam + X** |
| Screenshot | **Steam + R1** |
| Forçar fechar jogo | **Steam + B** (segurar 3s) |
| Ajustar brilho | **Steam + D-pad** |

### Melhor experiência

1. **Posição Bottom** funciona melhor para a maioria dos VNs
2. **Font Size 20-24** é ideal para o Steam Deck
3. **Auto-hide 15s** é um bom equilíbrio
4. Deixe **Show Original** ligado para estudar japonês!

### Economizar bateria

Visual Novels não precisam de muito poder:
1. Vá em **...** → **Performance**
2. Limite TDP para 8-10W
3. Limite GPU para 800-1000 MHz
4. Bateria dura muito mais!

---

## Atualizando o Plugin

Para atualizar para uma nova versão:

```bash
cd ~/Downloads/AnulTranslator
git pull
cd decky-plugin-lunatranslator
./build.sh
./install.sh
```

Reinicie o Steam após atualizar.

---

## Desinstalando

Se quiser remover o plugin:

```bash
cd ~/Downloads/AnulTranslator/decky-plugin-lunatranslator
./uninstall.sh
```

---

## Suporte

Encontrou um bug ou tem sugestões?

- **Issues:** https://github.com/tobidashite/AnulTranslator/issues
- **Discussões:** https://github.com/tobidashite/AnulTranslator/discussions

---

## Créditos

- **LunaTranslator** - O incrível tradutor de Visual Novels
- **Decky Loader** - Framework de plugins para Steam Deck
- **Comunidade Steam Deck** - Por tornar isso possível!

---

**Divirta-se jogando suas Visual Novels favoritas no Steam Deck!** 🎮
