@echo off
title Update Seeker - Denni Kontrola
cd /d "%~dp0src"
echo Spoustim denni kontrolu zarizeni a aktualizaci...
echo.
python main.py --headless
echo.
echo Kontrola byla dokončena. Stiskněte libovolnou klávesu pro zavření.
pause > nul
