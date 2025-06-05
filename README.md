Olá, gentalha!

Os projetos estão todos aí em cima.
Os scripts PowerShell só vão funcionar se antes, como ADM, executar esse comando: Enable PowerShell execution: Set-ExecutionPolicy Unrestricted -Force
P.S.: os scripts também deverão ser executados como ADM.

Lista de Comandos/Scripts:

Scripts PS1 online Edu (nomes das funções estão nos próprio nomes dos arquivos)
-------------------------------------------------------------------------------

iwr -useb "https://raw.githubusercontent.com/jakelino/jakelino/main/liberar_espaco.ps1" | iex

OU
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/jakelino/jakelino/main/liberar_espaco.ps1" | Invoke-Expression

====================================

iwr -useb "https://raw.githubusercontent.com/jakelino/jakelino/refs/heads/main/manutencao_SO.ps1" | iex

====================================

iwr -useb "https://raw.githubusercontent.com/jakelino/jakelino/refs/heads/main/manut_rede.ps1" | iex

====================================


====================================



[![](https://img.shields.io/badge/Go%20to%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935)](https://github.com/jakelino/jakelino/issues/1)
