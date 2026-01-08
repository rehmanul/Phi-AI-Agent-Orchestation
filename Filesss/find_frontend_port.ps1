# PowerShell script to find the first available frontend port
# Checks ports starting from 3001 and finds the first one that's listening

$startPort = 3001
$maxPort = 3010
$foundPort = $null

Write-Host "Searching for frontend server on ports $startPort-$maxPort..." -ForegroundColor Yellow

for ($port = $startPort; $port -le $maxPort; $port++) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -InformationLevel Quiet
    
    if ($connection -eq $true) {
        Write-Host "Found frontend server on port $port" -ForegroundColor Green
        $foundPort = $port
        break
    }
}

if ($foundPort -ne $null) {
    Write-Output $foundPort
    exit 0
} else {
    Write-Host "No frontend server found on ports $startPort-$maxPort" -ForegroundColor Red
    Write-Output $startPort  # Default fallback
    exit 1
}
