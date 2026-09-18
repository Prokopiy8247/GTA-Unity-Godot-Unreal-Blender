@echo off
setlocal
cd /d "%~dp0"
set "MC_ENGINE=%GODOT_EXECUTABLE%"
if defined MC_ENGINE if exist "%MC_ENGINE%" goto run
set "MC_ENGINE="
for %%E in ("%~dp0Godot*.exe" "%~dp0.tools\Godot*.exe" "%LOCALAPPDATA%\Programs\Godot\Godot*.exe" "%USERPROFILE%\Downloads\Godot*win64*.exe") do if exist "%%~fE" set "MC_ENGINE=%%~fE"
if defined MC_ENGINE goto run
for %%N in (godot.exe godot4.exe) do for /f "delims=" %%E in ('where %%N 2^>nul') do set "MC_ENGINE=%%E"
if defined MC_ENGINE goto run
echo Godot was not found. For the ready-to-play game, download a Windows ZIP:
echo https://github.com/Prokopiy8247/GTA-Unity-Godot-Unreal-Blender/releases/tag/godot-v0.1.0
echo To run the source project, install Godot 4.7.2 Standard and open project.godot.
echo See PLAY_GUIDE.md.
pause
exit /b 1
:run
"%MC_ENGINE%" --path "%~dp0." %*
exit /b %errorlevel%
