$projectPath = $PSScriptRoot
$gamePath = Join-Path $projectPath 'Builds/Windows/MeridianCoast.exe'
if (Test-Path -LiteralPath $gamePath) {
    Start-Process -FilePath $gamePath -ArgumentList @('-screen-fullscreen','1') -WorkingDirectory $projectPath
} else {
    Start-Process 'https://github.com/Prokopiy8247/GTA-Unity-Godot-Unreal-Blender/releases/tag/unity-v1.0.0'
}
