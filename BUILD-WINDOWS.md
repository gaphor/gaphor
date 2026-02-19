# Guide de compilation pour Windows

Ce guide explique comment compiler Gaphor pour créer un exécutable Windows.

## Prérequis

1. **Python 3.12 ou 3.13** (obligatoire : Gaphor ne supporte pas Python 3.11 ni 3.15+)
2. **Poetry** - Installer avec **pipx** et Python 3.13 (voir ci-dessous), pas avec `pip install poetry` sous Python 3.11
3. **GTK pour Windows (gvsbuild)** - À installer **avant** toute compilation :
   - Téléchargez l’archive : https://github.com/wingtk/gvsbuild/releases (fichier `GTK4_Gvsbuild_*_x64.zip`)
   - Extrayez-la dans `C:\gtk` (par ex. avec 7-Zip : `7z x GTK4_Gvsbuild_*.zip -oC:\gtk -y`)
   - Vous devez avoir ensuite le dossier `C:\gtk\wheels\` avec les fichiers `.whl`

### Optionnel (pour créer un installateur)

4. **NSIS** - Installer avec: `winget install nsis`
5. **7-Zip** - Installer avec: `winget install 7zip`

## Méthode 1: Utilisation du script automatique

Le script `build-windows.ps1` automatise tout le processus:

```powershell
.\build-windows.ps1
```

Le script va:
1. Installer les dépendances nécessaires
2. Installer les wheels GTK (si disponibles)
3. Construire le package
4. Créer l'exécutable avec PyInstaller
5. Optionnellement créer l'installateur Windows

L'exécutable sera créé dans `dist\gaphor\gaphor.exe`

## Méthode 2: Compilation manuelle

Si vous préférez exécuter les commandes manuellement:

### 1. Installer les dépendances

```powershell
poetry install --only main,packaging,automation
```

### 2. Installer les wheels GTK pour Windows

```powershell
poetry run pip install --force-reinstall (Resolve-Path C:\gtk\wheels\PyGObject*.whl)
poetry run pip install --force-reinstall (Resolve-Path C:\gtk\wheels\pycairo*.whl)
```

### 3. Construire le package

```powershell
poetry build
```

### 4. Créer l'exécutable avec PyInstaller

```powershell
poetry run poe package
```

L'exécutable sera créé dans `dist\gaphor\gaphor.exe`

### 5. (Optionnel) Créer l'installateur Windows

```powershell
poetry run poe win-installer
```

Cela créera deux fichiers dans le dossier `dist\`:
- `gaphor-<version>-installer.exe` - Installateur NSIS
- `gaphor-<version>-portable.exe` - Version portable avec 7-Zip

## Résultat

Après la compilation réussie, vous trouverez:

- **Exécutable simple**: `dist\gaphor\gaphor.exe` - Contient tous les fichiers nécessaires dans un dossier
- **Installateur**: `dist\gaphor-<version>-installer.exe` - Installateur Windows complet
- **Portable**: `dist\gaphor-<version>-portable.exe` - Version portable auto-extractible

## Dépannage

### Erreur: "Cannot find path 'C:\gtk\wheels' because it does not exist"
Vous n’avez pas encore installé GTK (gvsbuild). À faire **une seule fois** :
1. Allez sur https://github.com/wingtk/gvsbuild/releases
2. Téléchargez le fichier **GTK4_Gvsbuild_*_x64.zip** (dernière version)
3. Extrayez-le **dans** `C:\` pour obtenir `C:\gtk\bin`, `C:\gtk\wheels`, etc.
   - Avec 7-Zip en PowerShell : `7z x .\GTK4_Gvsbuild_*.zip -oC:\ -y`
   - Vérifiez que `C:\gtk\wheels` existe et contient des fichiers `.whl`
4. Ensuite seulement, relancez les commandes d’installation des wheels.

### Erreur: "Unable to create process using ... Python311\python.exe" ou "Fatal error in launcher"
Poetry a été installé avec Python 3.11, alors que Gaphor demande **Python 3.12 ou 3.13**. Il faut utiliser Poetry avec Python 3.12/3.13 :
1. Installez Python 3.12 ou 3.13 depuis https://www.python.org/downloads/windows/
2. Installez **pipx** avec ce Python :  
   `py -3.13 -m pip install --user pipx` puis `py -3.13 -m pipx ensurepath`
3. Fermez et rouvrez PowerShell, puis installez Poetry avec pipx :  
   `pipx install poetry`
4. Dans le dossier du projet, indiquez à Poetry d’utiliser Python 3.13 :  
   `poetry env use "C:\Users\VOTRE_UTILISATEUR\AppData\Local\Programs\Python\Python313\python.exe"`  
   (adapter le chemin si Python 3.13 est ailleurs, ou utiliser `py -3.13` pour le trouver)
5. Relancez : `poetry install --only main,packaging,automation`

### Erreur: "Poetry n'est pas installé"
Installez Poetry avec pipx (voir ci-dessus), pas avec `pip install poetry` si vous avez plusieurs versions de Python.

### Erreur lors de la compilation PyInstaller
- Assurez-vous que toutes les dépendances sont installées
- Vérifiez que Python 3.12 ou 3.13 est utilisé (pas 3.15+)
- Essayez de reconstruire le bootloader PyInstaller si nécessaire

### L'exécutable ne démarre pas
- Vérifiez que toutes les DLL GTK sont incluses
- Assurez-vous que les chemins sont corrects
- Consultez les logs dans le dossier `build\` pour plus d'informations

## Notes

- La compilation peut prendre plusieurs minutes
- L'exécutable final sera assez volumineux (plusieurs centaines de Mo) car il inclut toutes les dépendances
- Pour une version de développement, vous pouvez simplement utiliser `poetry run gaphor` sans créer d'exécutable
