param([ValidateSet('Play','Editor','Build','Check')][string]$Mode='Play')
$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$projectFile=Join-Path $projectRoot 'Unreal_GTA.uproject'
$packagedExe=Join-Path $projectRoot 'Packaged/Windows/Unreal_GTA.exe'

function Find-UnrealEngine {
    $candidates=@()
    if($env:UE_ROOT){$candidates+=$env:UE_ROOT}
    foreach($key in @('HKLM:\SOFTWARE\EpicGames\Unreal Engine\5.8','HKLM:\SOFTWARE\WOW6432Node\EpicGames\Unreal Engine\5.8')){
        $item=Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue
        if($item -and $item.InstalledDirectory){$candidates+=$item.InstalledDirectory}
    }
    $manifest=Join-Path $env:ProgramData 'Epic/UnrealEngineLauncher/LauncherInstalled.dat'
    if(Test-Path -LiteralPath $manifest){
        $data=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
        $candidates+=@($data.InstallationList | Where-Object {$_.AppName -eq 'UE_5.8'} | ForEach-Object {$_.InstallLocation})
    }
    $candidates+=Join-Path $env:ProgramFiles 'Epic Games/UE_5.8'
    foreach($candidate in $candidates | Select-Object -Unique){
        $versionFile=Join-Path $candidate 'Engine/Build/Build.version'
        if(Test-Path -LiteralPath $versionFile){
            $version=Get-Content -LiteralPath $versionFile -Raw | ConvertFrom-Json
            if($version.MajorVersion -eq 5 -and $version.MinorVersion -eq 8 -and
                (Test-Path -LiteralPath (Join-Path $candidate 'Engine/Build/BatchFiles/Build.bat'))){return $candidate}
        }
    }
    throw 'Unreal Engine 5.8 was not found. Install UE 5.8.2 in Epic Games Launcher. See START_HERE.md. A custom installation can be selected with UE_ROOT.'
}
try {
    if($Mode -eq 'Play' -and (Test-Path -LiteralPath $packagedExe)){
        Start-Process -FilePath $packagedExe -ArgumentList '-windowed -ResX=1600 -ResY=900'
        exit 0
    }
    $engine=Find-UnrealEngine
    if($Mode -eq 'Check'){
        Write-Output 'UE 5.8 installation found.'
        Write-Output ('Ready Windows build present: '+(Test-Path -LiteralPath $packagedExe))
        exit 0
    }
    if($Mode -eq 'Editor'){
        & (Join-Path $engine 'Engine/Build/BatchFiles/Build.bat') Unreal_GTAEditor Win64 Development "-Project=$projectFile" -WaitMutex -NoHotReloadFromIDE
        if($LASTEXITCODE -ne 0){throw 'Editor compilation failed. See START_HERE.md: Windows source requirements.'}
        Start-Process -FilePath (Join-Path $engine 'Engine/Binaries/Win64/UnrealEditor.exe') -ArgumentList ('"'+$projectFile+'"')
        exit 0
    }
    Write-Host 'Building the game. The first build can take a long time. Leave this window open.'
    & (Join-Path $engine 'Engine/Build/BatchFiles/RunUAT.bat') BuildCookRun "-project=$projectFile" -noP4 -platform=Win64 -clientconfig=Shipping -build -cook -cookall -stage -pak -compressed -prereqs -nodebuginfo -archive "-archivedirectory=$projectRoot/Packaged" -unattended -utf8output
    if($LASTEXITCODE -ne 0){throw 'Game build failed. See START_HERE.md: Windows source requirements.'}
    if(-not(Test-Path -LiteralPath $packagedExe)){throw 'Build finished but the game executable is missing.'}
    if($Mode -eq 'Play'){Start-Process -FilePath $packagedExe -ArgumentList '-windowed -ResX=1600 -ResY=900'}
    Write-Host 'Ready: Packaged/Windows/Unreal_GTA.exe'
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
