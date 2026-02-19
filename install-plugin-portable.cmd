@echo off
setlocal enabledelayedexpansion

REM ============================================
REM Script d'installation de plugin pour Gaphor Portable
REM ============================================
REM
REM Ce script installe TOUS les plugins dans le même dossier "plugins"
REM pour permettre le partage des dépendances communes.
REM
REM Usage: install-plugin-portable.cmd <URL_ou_nom_du_plugin>
REM
REM Exemples:
REM   install-plugin-portable.cmd git+https://github.com/gaphor/gaphor_plugin_helloworld.git
REM   install-plugin-portable.cmd git+https://bitbucket.org/resonatesystems/gaphor_tools.git
REM   install-plugin-portable.cmd nom-du-plugin
REM ============================================

REM Définir le dossier de base (même dossier que le script)
set "PORTABLE_DIR=%~dp0"
set "PLUGIN_DIR=%PORTABLE_DIR%plugins"

REM Vérifier qu'un argument a été fourni
if "%~1"=="" (
    echo.
    echo ERREUR: Aucun plugin specifie.
    echo.
    echo Usage: %~nx0 ^<URL_ou_nom_du_plugin^>
    echo.
    echo Exemples:
    echo   %~nx0 git+https://github.com/gaphor/gaphor_plugin_helloworld.git
    echo   %~nx0 git+https://bitbucket.org/resonatesystems/gaphor_tools.git
    echo   %~nx0 nom-du-plugin
    echo.
    echo IMPORTANT: Tous les plugins sont installes dans le meme dossier
    echo pour permettre le partage des dependances communes.
    echo.
    pause
    exit /b 1
)

REM Créer le dossier plugins s'il n'existe pas
if not exist "%PLUGIN_DIR%" (
    echo Creation du dossier plugins...
    mkdir "%PLUGIN_DIR%"
    if !ERRORLEVEL! NEQ 0 (
        echo ERREUR: Impossible de creer le dossier %PLUGIN_DIR%
        pause
        exit /b 1
    )
)

REM Vérifier que pip est disponible
where pip >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: pip n'est pas trouve dans le PATH.
    echo.
    echo Installez Python depuis https://python.org ou le Microsoft Store.
    echo Assurez-vous que Python est ajoute au PATH lors de l'installation.
    echo.
    pause
    exit /b 1
)

REM Afficher les informations
echo.
echo ============================================
echo Installation du plugin pour Gaphor Portable
echo ============================================
echo.
echo Dossier portable: %PORTABLE_DIR%
echo Dossier plugins: %PLUGIN_DIR%
echo Plugin: %~1
echo.
echo NOTE: Tous les plugins sont installes dans le meme dossier
echo pour permettre le partage des dependances communes.
echo.

REM Installer le plugin
echo Installation en cours...
echo.
echo Pip va installer le plugin et ses dependances.
echo Les dependances deja installees seront reutilisees si compatibles.
echo.

pip install --target "%PLUGIN_DIR%" %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo Plugin installe avec succes!
    echo ============================================
    echo.
    echo Le plugin a ete installe dans:
    echo   %PLUGIN_DIR%
    echo.
    echo Les dependances communes sont partagees entre tous les plugins.
    echo.
    echo Pour utiliser ce plugin:
    echo.
    echo 1. Utilisez le script gaphor-portable.bat qui configure
    echo    automatiquement la variable GAPHOR_PLUGIN_PATH
    echo.
    echo 2. Ou configurez manuellement:
    echo    set GAPHOR_PLUGIN_PATH=%PLUGIN_DIR%
    echo    gaphor.exe
    echo.
) else (
    echo.
    echo ============================================
    echo ERREUR lors de l'installation du plugin
    echo ============================================
    echo.
    echo Verifiez que:
    echo   1. Le nom ou l'URL du plugin est correct
    echo   2. Vous avez une connexion Internet (si installation depuis Git/PyPI)
    echo   3. Python et pip sont correctement installes
    echo   4. Il n'y a pas de conflit de versions avec les dependances existantes
    echo.
    echo Si deux plugins necessitent des versions incompatibles d'une
    echo meme dependance, vous devrez peut-etre mettre a jour un des plugins.
    echo.
)

pause
endlocal
