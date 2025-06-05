# Executando ipconfig /release
Write-Host "# Executando ipconfig /release"
# Start-Process -FilePath "ipconfig.exe" -ArgumentList "/release" -Wait

# Executando ipconfig /renew
Write-Host "# Executando ipconfig /renew"
# Start-Process -FilePath "ipconfig.exe" -ArgumentList "/renew" -Wait

# Executando ipconfig /flushdns
Write-Host "# Executando ipconfig /flushdns"
Start-Process -FilePath "ipconfig.exe" -ArgumentList "/flushdns" -Wait

# Executando ipconfig /registerdns
Write-Host "# Executando ipconfig /registerdns"
Start-Process -FilePath "ipconfig.exe" -ArgumentList "/registerdns" -Wait

# Executando netsh winsock reset
Write-Host "# Executando netsh winsock reset"
Start-Process -FilePath "netsh.exe" -ArgumentList "winsock reset" -Wait

# Executando netsh int ip reset resetlog.txt
Write-Host "# Executando netsh int ip reset resetlog.txt"
Start-Process -FilePath "netsh.exe" -ArgumentList "int ip reset resetlog.txt" -Wait

# Executando netsh winsock reset all
Write-Host "# Executando netsh winsock reset all"
Start-Process -FilePath "netsh.exe" -ArgumentList "winsock reset all" -Wait

# Executando netsh int 6to4 reset all
Write-Host "# Executando netsh int 6to4 reset all"
Start-Process -FilePath "netsh.exe" -ArgumentList "int 6to4 reset all" -Wait

# Executando netsh int ip reset all
Write-Host "# Executando netsh int ip reset all"
Start-Process -FilePath "netsh.exe" -ArgumentList "int ip reset all" -Wait

# Executando netsh int ipv4 reset all
Write-Host "# Executando netsh int ipv4 reset all"
Start-Process -FilePath "netsh.exe" -ArgumentList "int ipv4 reset all" -Wait

# Executando netsh int ipv6 reset all
Write-Host "# Executando netsh int ipv6 reset all"
Start-Process -FilePath "netsh.exe" -ArgumentList "int ipv6 reset all" -Wait

# Executando netsh int httpstunnel reset all
Write-Host "# Executando netsh int httpstunnel reset all"
Start-Process -FilePath "netsh.exe" -ArgumentList "int httpstunnel reset all" -Wait

# Executando netsh int isatap reset all
Write-Host "# Executando netsh int isatap reset all"
Start-Process -FilePath "netsh.exe" -ArgumentList "int isatap reset all" -Wait

# Executando netsh int portproxy reset all
Write-Host "# Executando netsh int portproxy reset all"
Start-Process -FilePath "netsh.exe" -ArgumentList "int portproxy reset all" -Wait

# Executando netsh int tcp reset all
Write-Host "# Executando netsh int tcp reset all"
Start-Process -FilePath "netsh.exe" -ArgumentList "int tcp reset all" -Wait

# Executando netsh int teredo reset all
Write-Host "# Executando netsh int teredo reset all"
Start-Process -FilePath "netsh.exe" -ArgumentList "int teredo reset all" -Wait

# Executando netsh int ip reset
Write-Host "# Executando netsh int ip reset"
Start-Process -FilePath "netsh.exe" -ArgumentList "int ip reset" -Wait

# Executando netsh winsock reset
Write-Host "# Executando netsh winsock reset"
Start-Process -FilePath "netsh.exe" -ArgumentList "winsock reset" -Wait

# Executando nbtstat -rr
Write-Host "# Executando nbtstat -rr"
Start-Process -FilePath "nbtstat.exe" -ArgumentList "-rr" -Wait

# Executando netsh int ip reset all
Write-Host "# Executando netsh int ip reset all"
Start-Process -FilePath "netsh.exe" -ArgumentList "int ip reset all" -Wait

# Executando netsh winsock reset
Write-Host "# Executando netsh winsock reset"
Start-Process -FilePath "netsh.exe" -ArgumentList "winsock reset" -Wait

Write-Host ""
Write-Host ""
Write-Host "Quer reiniciar o PC?"
Write-Host ""
Write-Host ""

# Menu interativo para reinicio do PC
$reiniciar = $null
while ($reiniciar -notin @('S','N')) {
    $reiniciar = Read-Host "Digite S para Sim ou N para NAO"
    $reiniciar = $reiniciar.ToUpper()
}

if ($reiniciar -eq 'S') {
    Write-Host "Reiniciando o computador..."
    Start-Sleep -Seconds 2
    Restart-Computer -Force
} else {
    Write-Host "Operaçao concluída! O computador NAO sera reiniciado."
}

# Pausas adicionais, se necessário
Start-Sleep -Seconds 1
Start-Sleep -Seconds 1
Start-Sleep -Seconds 1
Start-Sleep -Seconds 1
