param([ValidateSet('Windows','macOS')][string]$Platform = 'Windows')
$ErrorActionPreference = 'Stop'
$projectPath = $PSScriptRoot
$version = (Get-Content -LiteralPath (Join-Path $projectPath 'ProjectSettings/ProjectVersion.txt') | Select-String '^m_EditorVersion:').Line.Split(':')[1].Trim()
$editorPath = $env:UNITY_EDITOR
if (-not $editorPath) { $editorPath = Join-Path $env:ProgramFiles "Unity/Hub/Editor/$version/Editor/Unity.exe" }
if (-not (Test-Path -LiteralPath $editorPath)) { throw "Install Unity $version in Unity Hub, or set UNITY_EDITOR to Unity.exe." }
$logDir = Join-Path $projectPath '.astra-run'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$method = if ($Platform -eq 'macOS') { 'MacOS' } else { 'Windows' }
$target = if ($Platform -eq 'macOS') { 'OSXUniversal' } else { 'Win64' }
$logPath = Join-Path $logDir "build-$Platform.log"
$argsList = @('-batchmode','-quit','-buildTarget',$target,'-projectPath',('"'+$projectPath+'"'),'-executeMethod',("Meridian.Editor.ReleaseBuilder.$method"),'-logFile',('"'+$logPath+'"'))
Write-Host "Building $Platform. Close Unity Editor before running this script."
$process = Start-Process -FilePath $editorPath -ArgumentList $argsList -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -ne 0) { throw "Build failed. See $logPath" }
Write-Host "Ready: $projectPath/Builds/$Platform"
