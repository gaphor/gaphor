# Flatpak Packaging for Gaphor

1. [Install Flatpak](https://flatpak.org/setup)
 
1. Install flatpak-builder
 
        $ sudo apt-get install flatpak-builder

1. Install the GNOME SDK

        $ flatpak install flathub org.gnome.Sdk 3.30

1. Build Gaphor

        $ flatpak-builder --gpg-sign=E4089A143589D73655DF66774E9C27AE08850F1E --gpg-homedir=../.gpg --force-clean --repo=gaphor-repo build org.gaphor.Gaphor.json
        
1. Create a Single-file Bundle

        $ flatpak build-bundle gaphor-repo gaphor-MAJOR.MINOR.PATCH.flatpak org.gaphor.Gaphor
