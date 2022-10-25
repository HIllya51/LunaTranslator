# Textractor

![Como se Parece](screenshot.png)

[English](README.md) ● [Español](README_ES.md) ● [简体中文](README_SC.md) ● [Русский](README_RU.md) ● [한국어](README_KR.md) ● [ภาษาไทย](README_TH.md) ● [Français](README_FR.md) ● [Italiano](README_IT.md) ● [日本語](README_JP.md) ● [Bahasa Indonesia](README_ID.md) ● [Português](README_PT.md)

**Textractor** (também conhecido como NextHooker) é um extrator de textos de video-games x86/x64  para Windows/Wine baseado no [ITHVNR](https://web.archive.org/web/20160202084144/http://www.hongfire.com/forum/showthread.php/438331-ITHVNR-ITH-with-the-VNR-engine).<br>
Assista ao [vídeo tutorial](docs/TUTORIAL.md) para uma rápida apresentação de como utilizá-lo.

## Download

As versões lançadas podem ser encontradas [aqui](https://github.com/Artikash/Textractor/releases).<br>
A última versão lançada do ITHVNR pode ser encontrada [aqui](https://drive.google.com/open?id=13aHF4uIXWn-3YML_k2YCDWhtGgn5-tnO).

## Recursos e Funções

- Altamente extensível e personalizável.
- Automaticamente extrai vários games engines (inclusive algumas não compatíveis com VNR!)
- Extrai texto usando códigos "hook" /H (a maioria dos códigos utilizados pelo AGTH são compatíveis.)
- Extrai texto diretamente utilizando códigos "read" /R

## Suporte Técnico

Por favor, deixe-me saber de quaisquer bugs, jogos que o Textractor tenha problema extraindo texto, pedido por recursos ou funções, ou quaisquer outras sugestões.<br>
Se você tiver algum problema extraindo um jogo, favor me mandar um e-mail do lugar de onde eu possa livremente dar download do jogo, ou presenteie-me o jogo no [Steam](https://steamcommunity.com/profiles/76561198097566313/).

## Extensões

Veja o meu [Projeto de Extensão-Exemplo](https://github.com/Artikash/ExampleExtension) para como construir uma extensão.<br>
Veja a pasta de extensões para mais exemplos do que as extensões são capazes de fazerem. 

## Contribuindo

Todas contribuições são bem-vindas! Por favor, me mande um e-mail no endereço akashmozumdar@gmail.com caso tenha alguma dúvida quanto ao codebase.<br>
Você deve seguir o processo padrão de fazer um pull request (fork, branch, realizar mudanças, realizar o PR do seu branch para o meu master).<br>
Contribuir com uma tradução é fácil: basta traduzir as linhas do text.cpp assim como esse README.

## Compilando

Antes de compilar o  *Textractor* você deve ter o Visual Studio com suporte ao CMake, assim como o Qt versão 5.13.<br>
Você deverá então ser capaz de simplesmente abrir uma pasta no Visual Studio e build. Inicie Textractor.exe.

## Arquitetura do Projeto

O host (veja a pasta host) injeta o texthook.dll (criado a partir da pasta texthook) dentro do processo-alvo e se conecta a ele por meio de 2 arquivos pipe.<br>
O Host escreve para hostPipe, o texthook escreve para hookPipe.<br>
O texthook espera pelo pipe estar conectado e então injeta algumas intruções dentro de quaisquer funções que produzam texto (por exemplo: TextOut, GetGlyphOutline) o que faz com que seu produto seja mandado por meio do pipe.<br>
Informação adicional sobre os hooks é trocada por meio da memória compartilhada.<br>
O texto que o host recebe por meio do pipe é então processado um pouco antes de ser despachado devolta para a IGU/GUI.<br>
Finalmente, a IGU/GUI despacha o texto para as extensões antes de mostrá-lo.

## [Desenvolvedores](docs/CREDITS.md)
