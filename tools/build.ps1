param([string]$Assembler = $env:VASM)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
if (-not $Assembler) { $Assembler = Join-Path $taskRoot 'vendor\vasmm68k_mot.exe' }
if (-not (Test-Path -LiteralPath $Assembler)) { throw 'Indiquez vasm avec -Assembler chemin\vasmm68k_mot.exe ou la variable VASM.' }
New-Item -ItemType Directory -Path (Join-Path $taskRoot 'build\hdd') -Force | Out-Null
& $Assembler -quiet -m68000 -Ftos -L (Join-Path $taskRoot 'build\player.lst') -o (Join-Path $taskRoot 'build\hdd\STFPLAY.PRG') (Join-Path $taskRoot 'src\player.s')
if ($LASTEXITCODE) { throw 'Assemblage impossible' }
New-Item -ItemType Directory -Path (Join-Path $taskRoot 'player') -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $taskRoot 'build\hdd\STFPLAY.PRG') -Destination (Join-Path $taskRoot 'player\STFPLAY.PRG') -Force
