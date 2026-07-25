@echo off
title Update Seeker - Nastaveni Automaticke Denni Kontroly
cd /d "%~dp0"
echo =======================================================
echo     Update Seeker - Automaticka denni kontrola
echo =======================================================
echo.
echo Tento skript nastavi v Planovaci uloh ve Windows automaticke 
echo spusteni kontroly kazdy den v 09:00 na pozadi.
echo.

schtasks /create /tn "UpdateSeekerDailyCheck" /tr "wscript.exe \"%~dp0Spustit_Na_Pozadi.vbs\"" /sc daily /st 09:00 /f

if %errorlevel% equ 0 (
    echo.
    echo [OK] Uloha byla uspesne pridana do Planovace uloh ve Windows!
    echo Kontrola probehne automaticky kazdy den v 09:00 na pozadi.
) else (
    echo.
    echo [CHYBA] Pridani ulohy selhalo. Spustte tento soubor jako Spravce (Administrator).
)

echo.
pause
