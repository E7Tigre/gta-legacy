$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
& (Join-Path $PSScriptRoot 'build-data.ps1')
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zipPath = Join-Path $projectRoot 'GTA_Legacy_Web.zip'
$stream = [System.IO.File]::Open($zipPath, [System.IO.FileMode]::Create)
$archive = [System.IO.Compression.ZipArchive]::new($stream, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    $files = @('index.html', 'README.md', 'INFORME_COBERTURA.md') | ForEach-Object { Get-Item -LiteralPath (Join-Path $projectRoot $_) }
    foreach ($directory in @('css', 'js', 'assets')) {
        $files += Get-ChildItem -LiteralPath (Join-Path $projectRoot $directory) -File -Recurse
    }
    $files += @('games.json', 'trailers.json', 'gallery.json', 'editions.json', 'catalog.js') | ForEach-Object { Get-Item -LiteralPath (Join-Path $projectRoot "data/$_") }
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($projectRoot.Length + 1).Replace('\', '/')
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, $file.FullName, $relative, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
    }
    $archive.CreateEntry('.nojekyll') | Out-Null
} finally {
    $archive.Dispose()
    $stream.Dispose()
}
Write-Host "Paquete web preparado: $zipPath"
