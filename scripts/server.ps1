# Local, read-only static server. Works with Windows PowerShell, no installations.
param([int]$Port = 8080, [switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$listener = New-Object Net.Sockets.TcpListener([Net.IPAddress]::Loopback, $port)
try { $listener.Start() } catch { Write-Host 'El puerto 8080 esta ocupado. Abre http://127.0.0.1:8080 o cierra el otro servidor.'; exit 1 }
Write-Host "GTA Legacy: http://127.0.0.1:$port (Ctrl+C para cerrar)"
if (!$NoBrowser) { Start-Process "http://127.0.0.1:$port" }
$mime = @{'.html'='text/html; charset=utf-8';'.css'='text/css; charset=utf-8';'.js'='text/javascript; charset=utf-8';'.json'='application/json; charset=utf-8';'.jpg'='image/jpeg';'.png'='image/png';'.webp'='image/webp';'.md'='text/plain; charset=utf-8'}
try {
  while ($true) {
    $client = $listener.AcceptTcpClient()
    try {
      $client.ReceiveTimeout = 3000
      $stream = $client.GetStream()
      $reader = New-Object IO.StreamReader($stream, [Text.Encoding]::ASCII, $false, 1024, $true)
      $request = $reader.ReadLine()
      if (!$request) { continue }
      while ($reader.ReadLine()) { }
      $parts = $request.Split(' ')
      $relative = [Uri]::UnescapeDataString(($parts[1] -split '\?')[0]).TrimStart('/')
      if (!$relative) { $relative = 'index.html' }
      $file = [IO.Path]::GetFullPath((Join-Path $projectRoot $relative))
      $status = '200 OK'; $type = 'text/plain; charset=utf-8'
      if ($parts[0] -notin @('GET','HEAD')) { $status='405 Method Not Allowed'; $bytes=[Text.Encoding]::UTF8.GetBytes('Metodo no permitido') }
      elseif (!$file.StartsWith($projectRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { $status='403 Forbidden'; $bytes=[Text.Encoding]::UTF8.GetBytes('Acceso no permitido') }
      elseif (!(Test-Path -LiteralPath $file -PathType Leaf)) { $status='404 Not Found'; $bytes=[Text.Encoding]::UTF8.GetBytes('Recurso no disponible') }
      else { $bytes=[IO.File]::ReadAllBytes($file); $ext=[IO.Path]::GetExtension($file); if ($mime.ContainsKey($ext)) { $type=$mime[$ext] } else { $type='application/octet-stream' } }
      $headers="HTTP/1.1 $status`r`nContent-Type: $type`r`nContent-Length: $($bytes.Length)`r`nConnection: close`r`nX-Content-Type-Options: nosniff`r`n`r`n"
      $headBytes=[Text.Encoding]::ASCII.GetBytes($headers)
      $stream.Write($headBytes,0,$headBytes.Length)
      if ($parts[0] -ne 'HEAD') { $stream.Write($bytes,0,$bytes.Length) }
    } catch { Write-Verbose $_ } finally { $client.Close() }
  }
} finally { $listener.Stop() }
