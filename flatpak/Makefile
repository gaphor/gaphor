BUILD_DEPENDS := poetry

ID := org.gaphor.Gaphor

BUILD := build
DIST := dist
REPO := $(BUILD)/repo

all: $(REPO) dist-flatpaks

install: $(BUILD)/$(ID).flatpak
	flatpak install --reinstall --assumeyes $(BUILD)/$(ID).flatpak

$(REPO): *.yaml
	flatpak-builder --force-clean --repo=$@ $(BUILD)/build $(ID).yaml
	flatpak build-update-repo $(REPO)

$(BUILD)/$(ID).flatpak: $(REPO)
	flatpak build-bundle $(REPO) $@ $(ID)

$(DIST):
	mkdir -p $(DIST)

$(DIST)/%.flatpak: $(BUILD)/%.flatpak $(DIST)
	cp $< $@

dist-flatpaks: $(DIST)/$(ID).flatpak

clean:
	rm -rf $(BUILD)
	rm -rf $(DIST)

python-modules:
	python3 flatpak-builder-tools/pip/flatpak-pip-generator \
		--cleanup=scripts \
		--output=build-depends \
		$(BUILD_DEPENDS)
	python3 flatpak-builder-tools/flatpak-json2yaml.py build-depends.json -o build-depends.yaml && rm build-depends.json
	python3 flatpak-builder-tools/poetry/flatpak-poetry-generator.py \
	    -o lockfile-depends.json \
	    --production \
	    ../poetry.lock
	python3 flatpak-builder-tools/flatpak-json2yaml.py lockfile-depends.json -o lockfile-depends.yaml && rm lockfile-depends.json


setup:
	flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
	flatpak install flathub org.gnome.Sdk//3.34
	flatpak install flathub org.gnome.Platform//3.34