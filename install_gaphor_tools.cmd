@echo off
setlocal enabledelayedexpansion

REM ============================================
REM Installation de Gaphor_Tools pour Gaphor Portable
REM ============================================
REM
REM Ce script installe le plugin Gaphor_Tools depuis BitBucket
REM dans le dossier plugins du Gaphor portable.
REM
REM Gaphor_Tools permet l'import/export de requirements SysML
REM et de notes vers Excel et Confluence.
REM ============================================

REM Définir le dossier de base (même dossier que le script)
set "PORTABLE_DIR=%~dp0"
set "PLUGIN_DIR=%PORTABLE_DIR%plugins"
set "TEMP_DIR=%TEMP%\gaphor_tools_install"
set "GAPHOR_TOOLS_REPO=https://bitbucket.org/resonatesystems/gaphor_tools"
set "GAPHOR_TOOLS_ZIP=%GAPHOR_TOOLS_REPO%/get/main.zip"

REM Afficher les informations
echo.
echo ============================================
echo Installation de Gaphor_Tools
echo ============================================
echo.
echo Dossier portable: %PORTABLE_DIR%
echo Dossier plugins: %PLUGIN_DIR%
echo.
echo Gaphor_Tools permet:
echo   - Import/export de requirements SysML vers Excel
echo   - Import/export de notes vers Excel et Confluence
echo   - Edition et synchronisation des donnees avec le modele
echo.

REM Créer le dossier plugins s'il n'existe pas
if not exist "%PLUGIN_DIR%" (
    echo Creation du dossier plugins...
    mkdir "%PLUGIN_DIR%"
    if !ERRORLEVEL! NEQ 0 (
        echo ERREUR: Impossible de creer le dossier %PLUGIN_DIR%
        pause
        exit /b 1
    )
    echo Dossier cree avec succes.
    echo.
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
    echo Vous pouvez aussi utiliser py -m pip si Python est installe.
    echo.
    pause
    exit /b 1
)

REM Vérifier si le plugin est déjà installé
if exist "%PLUGIN_DIR%\gaphor_tools" (
    echo ATTENTION: Gaphor_Tools semble deja installe.
    echo.
    set /p UPDATE="Voulez-vous le mettre a jour? (O/N): "
    if /i not "!UPDATE!"=="O" (
        echo Installation annulee.
        pause
        exit /b 0
    )
    echo.
    echo Mise a jour de Gaphor_Tools...
) else (
    echo Installation de Gaphor_Tools...
)

REM Essayer d'abord avec Git (si disponible)
where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Methode 1: Installation depuis Git (recommandee)
    echo ============================================
    echo URL: %GAPHOR_TOOLS_REPO%.git
    echo Destination: %PLUGIN_DIR%
    echo.
    echo Installation en cours, veuillez patienter...
    echo.
    
    pip install --target "%PLUGIN_DIR%" git+%GAPHOR_TOOLS_REPO%.git
    
    if !ERRORLEVEL! EQU 0 (
        goto :SUCCESS
    )
    echo.
    echo Installation via Git a echoue, tentative avec ZIP...
    echo.
)

REM Méthode alternative : télécharger le ZIP depuis BitBucket
echo.
echo Methode 2: Installation depuis ZIP (sans Git)
echo ============================================
echo.

REM Vérifier si PowerShell est disponible pour télécharger
where powershell >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: PowerShell n'est pas disponible.
    echo.
    echo Options:
    echo   1. Installez Git depuis https://git-scm.com/download/win
    echo   2. Ou telechargez manuellement le ZIP depuis:
    echo      %GAPHOR_TOOLS_REPO%/downloads
    echo      Puis installez-le avec:
    echo      pip install --target "%PLUGIN_DIR%" chemin\vers\gaphor_tools.zip
    echo.
    pause
    exit /b 1
)

REM Créer un dossier temporaire
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

echo Telechargement du ZIP depuis BitBucket...
echo URL: %GAPHOR_TOOLS_ZIP%
echo.

REM Télécharger le ZIP avec PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%GAPHOR_TOOLS_ZIP%' -OutFile '%TEMP_DIR%\gaphor_tools.zip' -UseBasicParsing}"

if !ERRORLEVEL! NEQ 0 (
    echo.
    echo ERREUR: Impossible de telecharger le ZIP depuis BitBucket.
    echo.
    echo Le depot BitBucket peut necessiter une authentification.
    echo.
    echo Options:
    echo   1. Installez Git et utilisez la methode Git (recommandee)
    echo   2. Telechargez manuellement le ZIP depuis:
    echo      %GAPHOR_TOOLS_REPO%/downloads
    echo      Puis installez-le avec:
    echo      pip install --target "%PLUGIN_DIR%" chemin\vers\gaphor_tools.zip
    echo   3. Si le depot est prive, vous devrez vous authentifier
    echo.
    rmdir /s /q "%TEMP_DIR%" 2>nul
    pause
    exit /b 1
)

if not exist "%TEMP_DIR%\gaphor_tools.zip" (
    echo ERREUR: Le fichier ZIP n'a pas ete telecharge.
    rmdir /s /q "%TEMP_DIR%" 2>nul
    pause
    exit /b 1
)

echo ZIP telecharge avec succes.
echo.
echo Installation depuis le fichier ZIP...
echo.

REM Installer depuis le ZIP local
pip install --target "%PLUGIN_DIR%" "%TEMP_DIR%\gaphor_tools.zip"

set "INSTALL_ERROR=!ERRORLEVEL!"

REM Nettoyer le dossier temporaire
rmdir /s /q "%TEMP_DIR%" 2>nul

if !INSTALL_ERROR! NEQ 0 (
    goto :ERROR
)

:SUCCESS
echo.
echo ============================================
echo Gaphor_Tools installe avec succes!
echo ============================================
echo.
echo Le plugin a ete installe dans:
echo   %PLUGIN_DIR%
echo.
echo Pour utiliser ce plugin:
echo.
echo 1. Utilisez le script gaphor-portable.bat qui configure
echo    automatiquement la variable GAPHOR_PLUGIN_PATH
echo.
echo 2. Ou configurez manuellement la variable d'environnement:
echo    set GAPHOR_PLUGIN_PATH=%PLUGIN_DIR%
echo    gaphor.exe
echo.
echo Le plugin devrait apparaitre dans le menu Outils (Tools)
echo apres le redemarrage de Gaphor.
echo.
goto :END

:ERROR
echo.
echo ============================================
echo ERREUR lors de l'installation de Gaphor_Tools
echo ============================================
echo.
echo Verifiez que:
echo   1. Vous avez une connexion Internet active
echo   2. Python et pip sont correctement installes
echo   3. Le depot BitBucket est accessible
echo.
echo Options alternatives:
echo.
echo Option 1 - Installer Git (recommandee):
echo   Telechargez Git depuis https://git-scm.com/download/win
echo   Puis relancez ce script.
echo.
echo Option 2 - Installation manuelle depuis ZIP:
echo   1. Telechargez le ZIP depuis:
echo      %GAPHOR_TOOLS_REPO%/downloads
echo   2. Installez-le avec:
echo      pip install --target "%PLUGIN_DIR%" chemin\vers\gaphor_tools.zip
echo.
echo Option 3 - Si le depot est prive:
echo   Vous devrez vous authentifier ou utiliser Git avec SSH.
echo.

:END
pause
endlocal
