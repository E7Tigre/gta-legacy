$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$parts = @()
foreach ($collection in @('games','trailers','gallery','editions')) {
    $raw = Get-Content -LiteralPath (Join-Path $projectRoot "data/$collection.json") -Raw -Encoding UTF8
    $null = ConvertFrom-Json -InputObject $raw
    $parts += ('"' + $collection + '":' + $raw)
}
$json = '{' + ($parts -join ',') + '}'
$utf8 = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $projectRoot 'data/catalog.js'), "window.GTA_CATALOG = $json;", $utf8)
Write-Host 'Catalogo actualizado. Ya puedes abrir index.html sin servidor.'
