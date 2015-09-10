@echo off
set InstallLocation=C:\Program Files\Epic Games\UnrealTournamentEditor
set UnrealPak=Engine\Binaries\Win64\UnrealPak.exe

set file=%*
set file=%file:/=\%
set file=%file:\\=\%

set EXE=%InstallLocation%\%UnrealPak%
set EXE=%EXE:\\=\%

ECHO.%file%| FIND /I ":\">Nul && ( 
	set file=%file%
) || (
	set file=%cd%\%1
)

set file=%file:"=%
set file="%file%"

echo Maps for %~n1%~x1
echo --------------------------
"%EXE%" %file% -list | find ".umap"
echo.
pause