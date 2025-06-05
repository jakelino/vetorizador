# Cria a pasta temporária
New-Item -Path "C:\temp" -ItemType Directory -Force | Out-Null

Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host "--------- Esvaziando lixeira -----------"
Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host ""

# Esvaziar a lixeira de todas as unidades listadas
$drives = @('C', 'D', 'E', 'F', 'G', 'H', 'Z')
foreach ($drive in $drives) {
    $recycleBin = "$drive`:\$Recycle.Bin"
    if (Test-Path $recycleBin) {
        Remove-Item -Path $recycleBin -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host "-------- Apagando Prefetch -------------"
Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host ""
Write-Host "APAGANDO ARQUIVOS PREFETCH"
Write-Host ""

# Apaga arquivos da pasta Prefetch
Remove-Item -Path "C:\Windows\Prefetch\*" -Force -Recurse -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "APAGANDO SUBDIRETORIOS PREFETCH"
Write-Host ""

# Remove a pasta Prefetch
Remove-Item -Path "C:\Windows\Prefetch" -Force -Recurse -ErrorAction SilentlyContinue

Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host " --------- Apagando Win temp -----------"
Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host ""
Write-Host "APAGANDO ARQUIVOS Win temp"
Write-Host ""

# Apaga arquivos da pasta Temp do Windows
Remove-Item -Path "C:\Windows\Temp\*" -Force -Recurse -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "APAGANDO SUBDIRETORIOS Win temp"
Write-Host ""

# Remove a pasta Temp do Windows
Remove-Item -Path "C:\Windows\Temp" -Force -Recurse -ErrorAction SilentlyContinue

Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host "------ Apagando temp do app data -------"
Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host ""
Write-Host "APAGANDO ARQUIVOS temp do app data"
Write-Host ""

# Apaga arquivos da pasta Temp do usuário
Remove-Item -Path "$env:TEMP\*" -Force -Recurse -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "APAGANDO SUBDIRETORIOS temp do app data"
Write-Host ""

# Remove a pasta Temp do usuário
Remove-Item -Path "$env:TEMP" -Force -Recurse -ErrorAction SilentlyContinue

Write-Host "----------------------------------------"
Write-Host "----------------------------------------"
Write-Host "---------- RECRIANDO PASTAS* -----------"
Write-Host "------- *caso seja necessario... -------"
Write-Host "----------------------------------------"

# Recria as pastas removidas
New-Item -Path "C:\Windows\Prefetch" -ItemType Directory -Force | Out-Null
New-Item -Path "C:\Windows\Temp" -ItemType Directory -Force | Out-Null
New-Item -Path "$env:TEMP" -ItemType Directory -Force | Out-Null

Pause
