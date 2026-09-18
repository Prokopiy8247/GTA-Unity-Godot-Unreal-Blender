$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$projectFile=(Join-Path $projectRoot 'Unreal_GTA.uproject')
$engineRoot=Join-Path $env:UE_ROOT 'Engine'
if(-not(Test-Path -LiteralPath $engineRoot)){throw 'Set UE_ROOT to your UE_5.8 installation directory.'}
New-Item -ItemType Directory -Path (Join-Path $projectRoot '.astra-run') -Force | Out-Null
$logPath=Join-Path $projectRoot '.astra-run/validation.log'
& "$engineRoot/Build/BatchFiles/Build.bat" Unreal_GTAEditor Win64 Development "-Project=$projectFile" -WaitMutex -NoHotReloadFromIDE
if($LASTEXITCODE -ne 0){throw 'Editor build failed'}
& "$engineRoot/Binaries/Win64/UnrealEditor-Cmd.exe" $projectFile /Game/GTA/Maps/PortMeridian -game -NullRHI -unattended -nosplash -PMTest "-abslog=$logPath" *> (Join-Path $projectRoot '.astra-run/validation-console.log')
$checks=Select-String -LiteralPath $logPath -Pattern 'PM_TEST_|PM_SMOKE_COMPLETE'
$checks | ForEach-Object {$_.Line}
if(-not (Select-String -LiteralPath $logPath -Pattern 'PM_SMOKE_COMPLETE' -Quiet)){throw 'Runtime test did not complete'}
if(Select-String -LiteralPath $logPath -Pattern 'PM_TEST_.*=FAIL' -Quiet){throw 'Runtime test failure'}
Write-Output 'Port Meridian validation passed.'
