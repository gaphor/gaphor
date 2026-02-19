@echo off
setlocal

REM ============================================
REM Script de lancement pour Gaphor Portable
REM ============================================
REM
REM Ce script configure automatiquement les chemins
REM pour une utilisation portable de Gaphor.
REM ============================================

REM Définir le dossier de base (même dossier que le script)
REM %~dp0 donne le chemin avec backslash final (ex: C:\path\)
set "PORTABLE_DIR=%~dp0"
REM Construire les chemins complets
set "PLUGIN_DIR=%PORTABLE_DIR%plugins"
set "CONFIG_DIR=%PORTABLE_DIR%config"
set "CACHE_DIR=%PORTABLE_DIR%cache"

REM Configurer les variables d'environnement pour Gaphor
set "XDG_CONFIG_HOME=%CONFIG_DIR%"
set "XDG_CACHE_HOME=%CACHE_DIR%"
set "GAPHOR_PLUGIN_PATH=%PLUGIN_DIR%"

REM Créer les dossiers s'ils n'existent pas
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"
if not exist "%CACHE_DIR%" mkdir "%CACHE_DIR%"
if not exist "%PLUGIN_DIR%" mkdir "%PLUGIN_DIR%"

REM Vérifier que gaphor.exe existe
if not exist "%PORTABLE_DIR%gaphor.exe" (
    echo ERREUR: gaphor.exe introuvable dans %PORTABLE_DIR%
    echo.
    echo Assurez-vous que ce script se trouve dans le meme dossier que gaphor.exe
    echo.
    pause
    exit /b 1
)

REM Lancer Gaphor avec tous les arguments passés au script
REM Les variables d'environnement sont automatiquement héritées par le processus enfant
"%PORTABLE_DIR%gaphor.exe" %*

endlocal
