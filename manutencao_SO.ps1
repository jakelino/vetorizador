# Certifique-se de rodar como Administrador!

Write-Host "Executando CHKDSK (pode pedir para agendar no próximo boot)..."
chkdsk /f /r /x c:

Write-Host "Executando SFC /scannow..."
sfc /scannow

Write-Host "Executando DISM /CheckHealth..."
DISM /Online /Cleanup-Image /CheckHealth

Write-Host "Executando DISM /ScanHealth..."
DISM /Online /Cleanup-Image /ScanHealth

Write-Host "Executando DISM /RestoreHealth..."
DISM /Online /Cleanup-Image /RestoreHealth


