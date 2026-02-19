# Script de compilation pour créer un exécutable Windows de Gaphor
# Utilisation:
#   .\build-windows.ps1              # Compilation complète puis option installateur
#   .\build-windows.ps1 -InstallerOnly   # Uniquement l'étape 5 (installateur), si dist\gaphor existe déjà

param(
    [switch]$InstallerOnly
)

Write-Host "=== Compilation de Gaphor pour Windows ===" -ForegroundColor Cyan

# Vérifier que Poetry est installé
if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "ERREUR: Poetry n'est pas installé. Installez-le avec: pip install poetry" -ForegroundColor Red
    exit 1
}

# Vérifier que Python est installé
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERREUR: Python n'est pas installé." -ForegroundColor Red
    exit 1
}

# Ajouter NSIS au PATH s'il est installé mais pas dans le PATH
if (-not (Get-Command makensis -ErrorAction SilentlyContinue)) {
    $nsisPaths = @(
        "${env:ProgramFiles(x86)}\NSIS",
        "${env:ProgramFiles}\NSIS"
    )
    foreach ($nsisDir in $nsisPaths) {
        if (Test-Path (Join-Path $nsisDir "makensis.exe")) {
            $env:Path = "$nsisDir;$env:Path"
            Write-Host "NSIS ajouté au PATH: $nsisDir" -ForegroundColor Gray
            break
        }
    }
}

function Run-InstallerStep {
    if (-not (Test-Path "dist\gaphor\gaphor.exe")) {
        Write-Host "ERREUR: dist\gaphor\gaphor.exe introuvable. Lancez d'abord la compilation complète (sans -InstallerOnly)." -ForegroundColor Red
        exit 1
    }
    Write-Host "`n5. Création de l'installateur Windows..." -ForegroundColor Yellow
    $canBuild = $true
    if (-not (Get-Command makensis -ErrorAction SilentlyContinue)) {
        Write-Host "NSIS n'est pas installé (makensis introuvable)." -ForegroundColor Yellow
        Write-Host "  Téléchargement: https://nsis.sourceforge.io/Download" -ForegroundColor Gray
        Write-Host "  Ou: winget install nsis" -ForegroundColor Gray
        $canBuild = $false
    }
    if (-not (Get-Command 7z -ErrorAction SilentlyContinue) -and -not (Test-Path "C:\Program Files\7-Zip\7z.exe")) {
        Write-Host "7-Zip n'est pas installé." -ForegroundColor Yellow
        Write-Host "  Téléchargement: https://www.7-zip.org/ ou: winget install 7zip" -ForegroundColor Gray
        $canBuild = $false
    }
    if ($canBuild) {
        poetry run poe win-installer
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n=== Installateur créé avec succès! ===" -ForegroundColor Green
            Write-Host "Les installateurs se trouvent dans le dossier dist\" -ForegroundColor Green
        } else {
            Write-Host "ERREUR lors de la création de l'installateur" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Installez NSIS et 7-Zip puis relancez: .\build-windows.ps1 -InstallerOnly" -ForegroundColor Gray
        exit 1
    }
}

if ($InstallerOnly) {
    Run-InstallerStep
    exit 0
}

Write-Host "`n1. Installation des dépendances..." -ForegroundColor Yellow
poetry install --only main,packaging,automation

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de l'installation des dépendances" -ForegroundColor Red
    exit 1
}

# Vérifier si les wheels GTK sont disponibles
$gtkWheelsPath = "C:\gtk\wheels"
if (Test-Path $gtkWheelsPath) {
    Write-Host "`n2. Installation des wheels GTK pour Windows..." -ForegroundColor Yellow

    $pygobjectWheel = Get-ChildItem -Path "$gtkWheelsPath\PyGObject*.whl" -ErrorAction SilentlyContinue | Select-Object -First 1
    $pycairoWheel = Get-ChildItem -Path "$gtkWheelsPath\pycairo*.whl" -ErrorAction SilentlyContinue | Select-Object -First 1

    if ($pygobjectWheel -and $pycairoWheel) {
        poetry run pip install --force-reinstall $pygobjectWheel.FullName
        poetry run pip install --force-reinstall $pycairoWheel.FullName
        Write-Host "Wheels GTK installés avec succès" -ForegroundColor Green
    } else {
        Write-Host "ATTENTION: Les wheels GTK n'ont pas été trouvés dans $gtkWheelsPath" -ForegroundColor Yellow
        Write-Host "Vous devrez peut-être les télécharger depuis https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer" -ForegroundColor Yellow
    }
} else {
    Write-Host "ATTENTION: Le répertoire GTK wheels n'existe pas: $gtkWheelsPath" -ForegroundColor Yellow
    Write-Host "Vous devrez peut-être installer GTK pour Windows et les wheels correspondants" -ForegroundColor Yellow
}

Write-Host "`n3. Construction du package..." -ForegroundColor Yellow
poetry build

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de la construction du package" -ForegroundColor Red
    exit 1
}

Write-Host "`n4. Création de l'exécutable avec PyInstaller..." -ForegroundColor Yellow
poetry run poe package

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de la création de l'exécutable" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Compilation terminée avec succès! ===" -ForegroundColor Green
Write-Host "L'exécutable se trouve dans: dist\gaphor\gaphor.exe" -ForegroundColor Green

# Demander si l'utilisateur veut créer l'installateur
$createInstaller = Read-Host "`nVoulez-vous créer l'installateur Windows? (O/N)"
if ($createInstaller -eq "O" -or $createInstaller -eq "o") {
    Run-InstallerStep
} else {
    Write-Host "`nPour créer l'installateur plus tard sans recompiler: .\build-windows.ps1 -InstallerOnly" -ForegroundColor Gray
}
