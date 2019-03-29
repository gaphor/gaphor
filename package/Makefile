
# See https://elliotekj.com/2014/05/27/how-to-create-high-resolution-icns-files/


ICON_FILES=\
	gaphor.iconset/icon_16x16.png \
	gaphor.iconset/icon_16x16@2x.png \
	gaphor.iconset/icon_32x32.png \
	gaphor.iconset/icon_32x32@2x.png \
	gaphor.iconset/icon_128x128.png \
	gaphor.iconset/icon_128x128@2x.png \
	gaphor.iconset/icon_256x256.png \
	gaphor.iconset/icon_512x512.png \
	gaphor.iconset/icon_512x512@2x.png

all: gaphor.icns

gaphor.icns: $(ICON_FILES)
	iconutil -c icns gaphor.iconset

gaphor.iconset/icon_16x16.png: gaphor.iconset ../iconsrc/gaphor.svg
	rsvg-convert -h 16 ../iconsrc/gaphor.svg > $@

gaphor.iconset/icon_16x16@2x.png: gaphor.iconset ../iconsrc/gaphor.svg
	rsvg-convert -h 32 ../iconsrc/gaphor.svg > $@

gaphor.iconset/icon_32x32.png: gaphor.iconset ../iconsrc/gaphor.svg
	rsvg-convert -h 32 ../iconsrc/gaphor.svg > $@

gaphor.iconset/icon_32x32@2x.png: gaphor.iconset ../iconsrc/gaphor.svg
	rsvg-convert -h 64 ../iconsrc/gaphor.svg > $@

gaphor.iconset/icon_128x128.png: gaphor.iconset ../iconsrc/gaphor.svg
	rsvg-convert -h 128 ../iconsrc/gaphor.svg > $@

gaphor.iconset/icon_128x128@2x.png: gaphor.iconset ../iconsrc/gaphor.svg
	rsvg-convert -h 256 ../iconsrc/gaphor.svg > $@

gaphor.iconset/icon_256x256.png: gaphor.iconset ../iconsrc/gaphor.svg
	rsvg-convert -h 256 ../iconsrc/gaphor.svg > $@

gaphor.iconset/icon_256x256@2x.png: gaphor.iconset ../iconsrc/gaphor.svg
	rsvg-convert -h 512 ../iconsrc/gaphor.svg > $@

gaphor.iconset/icon_512x512.png: gaphor.iconset ../iconsrc/gaphor.svg
	rsvg-convert -h 512 ../iconsrc/gaphor.svg > $@

gaphor.iconset/icon_512x512@2x.png: gaphor.iconset ../iconsrc/gaphor.svg
	rsvg-convert -h 1024 ../iconsrc/gaphor.svg > $@

gaphor.iconset:
	mkdir -p $@
