# Função para obter o espaço livre em bytes em uma unidade
function Get-FreeSpaceBytes($driveLetter) {
    $drive = Get-PSDrive -Name $driveLetter -ErrorAction SilentlyContinue
    if ($drive) { return $drive.Free }
    else { return 0 }
}

# Função para formatar bytes em MB/GB
function Format-Bytes($bytes) {
    if ($bytes -gt 1GB) { return "{0:N2} GB" -f ($bytes/1GB) }
    elseif ($bytes -gt 1MB) { return "{0:N2} MB" -f ($bytes/1MB) }
    else { return "$bytes bytes" }
}

# Defina a unidade principal (normalmente C:)
$mainDrive = 'C'

# Espaço livre antes da limpeza
$freeBefore = Get-FreeSpaceBytes $mainDrive

# Cria a pasta temporária
New-Item -Path "C:\temp" -ItemType Directory -Force | Out-Null

Write-Host "----------------------------------------"
Write-Host "--------- Esvaziando lixeira -----------"
Write-Host "----------------------------------------"

# Esvaziar a lixeira de todas as unidades listadas
$drives = @('C', 'D', 'E', 'F', 'G', 'H', 'Z')
foreach ($drive in $drives) {
    $recycleBin = "$drive`:\$Recycle.Bin"
    if (Test-Path $recycleBin) {
        Remove-Item -Path $recycleBin -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "----------------------------------------"
Write-Host "---- apagando prefetch ----"
Write-Host "----------------------------------------"
Write-Host "APAGANDO ARQUIVOS"

Remove-Item -Path "C:\Windows\Prefetch\*" -Force -Recurse -ErrorAction SilentlyContinue
Write-Host "APAGANDO SUBDIRETORIOS"
Remove-Item -Path "C:\Windows\Prefetch" -Force -Recurse -ErrorAction SilentlyContinue

Write-Host "----------------------------------------"
Write-Host " ---- apagando win temp ----"
Write-Host "----------------------------------------"
Write-Host "APAGANDO ARQUIVOS"

Remove-Item -Path "C:\Windows\Temp\*" -Force -Recurse -ErrorAction SilentlyContinue
Write-Host "APAGANDO SUBDIRETORIOS"
Remove-Item -Path "C:\Windows\Temp" -Force -Recurse -ErrorAction SilentlyContinue

Write-Host "----------------------------------------"
Write-Host " ---- apagando temp do app data ----"
Write-Host "----------------------------------------"
Write-Host "APAGANDO ARQUIVOS"

Remove-Item -Path "$env:TEMP\*" -Force -Recurse -ErrorAction SilentlyContinue
Write-Host "APAGANDO SUBDIRETORIOS"
Remove-Item -Path "$env:TEMP" -Force -Recurse -ErrorAction SilentlyContinue

Write-Host "----------------------------------------"
Write-Host "---------- RECRIANDO PASTAS ------------"
Write-Host "----------------------------------------"

New-Item -Path "C:\Windows\Prefetch" -ItemType Directory -Force | Out-Null
New-Item -Path "C:\Windows\Temp" -ItemType Directory -Force | Out-Null
New-Item -Path "$env:TEMP" -ItemType Directory -Force | Out-Null

Write-Host ""
Write-Host "----- LISTANDO ARQUIVOS DAS PASTAS -----"
Write-Host "----  prefetch ----"
Get-ChildItem "C:\Windows\Prefetch" | Select-Object Name
Write-Host "----  win temp ----"
Get-ChildItem "C:\Windows\Temp" | Select-Object Name
Write-Host "----  temp do app data ----"
Get-ChildItem "$env:TEMP" | Select-Object Name

Write-Host ""
Write-Host "----------------------------------------"
Write-Host "Calculando espaco livre - antes e depois"
Write-Host "----------------------------------------"

# Espaço livre depois da limpeza
$freeAfter = Get-FreeSpaceBytes $mainDrive

# Espaço liberado em bytes
$freed = $freeAfter - $freeBefore

Write-Host ""
Write-Host "Espaco livre antes : $(Format-Bytes $freeBefore)"
Write-Host "Espaco livre depois: $(Format-Bytes $freeAfter)"
Write-Host "Espaco liberado    : $(Format-Bytes $freed)"
Write-Host ""

Pause
