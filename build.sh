#!/bin/bash
set -eE
cp DEBIAN/gcde-desktop.control DEBIAN/control
VERSION=$(cat DEBIAN/control | grep 'Version: ' | sed 's/Version: //g')
PAK=$(cat DEBIAN/control | grep 'Package: ' | sed 's/Package: //g')
ARCH=$(cat DEBIAN/control | grep 'Architecture: '| sed 's/Architecture: //g')
FOLDER="$PAK\_$VERSION\_$ARCH"
FOLDER=$(echo "$FOLDER" | sed 's/\\//g')
if [ "$ARCH" == "amd64" ]; then
	COMPILER="gcc -m64"
	ARGS="-Wall"
elif [ "$ARCH" == "arm64" ]; then
	COMPILER="aarch64-linux-gnu-g++"
	ARGS=""
fi
mkdir ../"$FOLDER"
##############################################################
#							     #
#							     #
#  COMPILE ANYTHING NECSSARY HERE			     #
#							     #
#							     #
##############################################################
cd usr/share/gcde/controller_support
$COMPILER $ARGS gcde-analog-mapper.cxx -o gcde-analog-mapper
cd ../../../..
##############################################################
#							     #
#							     #
#  REMEMBER TO DELETE SOURCE FILES FROM TMP		     #
#  FOLDER BEFORE BUILD					     #
#							     #
#							     #
##############################################################
if [ -d bin ]; then
	cp -R bin ../"$FOLDER"/bin
fi
if [ -d etc ]; then
	cp -R etc ../"$FOLDER"/etc
fi
if [ -d usr ]; then
	cp -R usr ../"$FOLDER"/usr
fi
if [ -d lib ]; then
	cp -R lib ../"$FOLDER"/lib
fi
if [ -d lib32 ]; then
	cp -R lib32 ../"$FOLDER"/lib32
fi
if [ -d lib64 ]; then
	cp -R lib64 ../"$FOLDER"/lib64
fi
if [ -d libx32 ]; then
	cp -R libx32 ../"$FOLDER"/libx32
fi
if [ -d sbin ]; then
	cp -R sbin ../"$FOLDER"/sbin
fi
if [ -d var ]; then
	cp -R var ../"$FOLDER"/var
fi
if [ -d opt ]; then
	cp -R opt ../"$FOLDER"/opt
fi
if [ -d srv ]; then
	cp -R srv ../"$FOLDER"/srv
fi
cp -R DEBIAN ../"$FOLDER"/DEBIAN
cd ..
#DELETE STUFF HERE
rm "$FOLDER"/usr/share/gcde/controller_support/gcde-analog-mapper.cxx
rm gcde/usr/share/gcde/controller_support/gcde-analog-mapper
rm -rf "$FOLDER"/usr/lib
#build the shit
rm "$FOLDER"/DEBIAN/gcde-common.control "$FOLDER"/DEBIAN/gcde-common.install "$FOLDER"/DEBIAN/gcde-desktop.control
dpkg-deb --build "$FOLDER"
cd gcde
cp DEBIAN/gcde-common.control DEBIAN/control
VERSION=$(cat DEBIAN/control | grep 'Version: ' | sed 's/Version: //g')
PAK=$(cat DEBIAN/control | grep 'Package: ' | sed 's/Package: //g')
ARCH=$(cat DEBIAN/control | grep 'Architecture: '| sed 's/Architecture: //g')
NEW_FOLDER="$PAK\_$VERSION\_$ARCH"
NEW_FOLDER=$(echo "$NEW_FOLDER" | sed 's/\\//g')
mv ../"$FOLDER" ../"$NEW_FOLDER"
mv DEBIAN/control ../"$NEW_FOLDER"/DEBIAN/control
cp DEBIAN/gcde-common.install ../"$NEW_FOLDER"/DEBIAN/gcde-common.install
cd ..
rm -rf "$NEW_FOLDER"/usr/share
rm -rf "$NEW_FOLDER"/usr/bin
rm -rf "$NEW_FOLDER"/etc
mkdir "$NEW_FOLDER"/usr/lib
cp -R gcde/usr/lib "$NEW_FOLDER"/usr
dpkg-deb --build "$NEW_FOLDER"
rm -rf "$NEW_FOLDER"
