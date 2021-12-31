#!/bin/bash

set -euo pipefail

pip install setuptools_scm
# The environment variable HDDCOIN_INSTALLER_VERSION needs to be defined.
# If the env variable NOTARIZE and the username and password variables are
# set, this will attempt to Notarize the signed DMG.
HDDCOIN_INSTALLER_VERSION=$(python installer-version.py)

if [ ! "$HDDCOIN_INSTALLER_VERSION" ]; then
	echo "WARNING: No environment variable HDDCOIN_INSTALLER_VERSION set. Using 0.0.0."
	HDDCOIN_INSTALLER_VERSION="0.0.0"
fi
echo "HDDcoin Installer Version is: $HDDCOIN_INSTALLER_VERSION"

echo "Installing npm and electron packagers"
npm install electron-installer-dmg -g
# Pinning electron-packager and electron-osx-sign to known working versions
# Current packager uses an old version of osx-sign, so if we install the newer sign package
# things break
npm install electron-packager@15.4.0 -g
npm install electron-osx-sign@v0.5.0 -g
npm install notarize-cli -g

echo "Create dist/"
sudo rm -rf dist
mkdir dist

echo "Create executables with pyinstaller"
pip install pyinstaller==4.5
SPEC_FILE=$(python -c 'import hddcoin; print(hddcoin.PYINSTALLER_SPEC_PATH)')
pyinstaller --log-level=INFO "$SPEC_FILE"
LAST_EXIT_CODE=$?
if [ "$LAST_EXIT_CODE" -ne 0 ]; then
	echo >&2 "pyinstaller failed!"
	exit $LAST_EXIT_CODE
fi
cp -r dist/daemon ../hddcoin-blockchain-gui
cd .. || exit
cd hddcoin-blockchain-gui || exit

echo "npm build"
npm install
# npm audit fix
./node_modules/.bin/electron-rebuild -f -w node-pty
npm run build
LAST_EXIT_CODE=$?
if [ "$LAST_EXIT_CODE" -ne 0 ]; then
	echo >&2 "npm run build failed!"
	exit $LAST_EXIT_CODE
fi

# sets the version for hddcoin-blockchain in package.json
brew install jq
cp package.json package.json.orig
jq --arg VER "$HDDCOIN_INSTALLER_VERSION" '.version=$VER' package.json > temp.json && mv temp.json package.json

electron-packager . HDDcoin --asar.unpack="{**/daemon/**,**/node_modules/node-pty/build/Release/*}" --platform=darwin \
--icon=src/assets/img/HDDcoin.icns --overwrite --app-bundle-id=net.hddcoin.blockchain \
--appVersion=$HDDCOIN_INSTALLER_VERSION
LAST_EXIT_CODE=$?

# reset the package.json to the original
mv package.json.orig package.json

if [ "$LAST_EXIT_CODE" -ne 0 ]; then
	echo >&2 "electron-packager failed!"
	exit $LAST_EXIT_CODE
fi

if [ "$NOTARIZE" == true ]; then
  electron-osx-sign HDDcoin-darwin-x64/HDDcoin.app --platform=darwin \
  --hardened-runtime=true --provisioning-profile=hddcoinblockchain.provisionprofile \
  --entitlements=entitlements.mac.plist --entitlements-inherit=entitlements.mac.plist \
  --no-gatekeeper-assess
fi
LAST_EXIT_CODE=$?
if [ "$LAST_EXIT_CODE" -ne 0 ]; then
	echo >&2 "electron-osx-sign failed!"
	exit $LAST_EXIT_CODE
fi

mv HDDcoin-darwin-x64 ../build_scripts/dist/
cd ../build_scripts || exit

DMG_NAME="HDDcoin-$HDDCOIN_INSTALLER_VERSION.dmg"
echo "Create $DMG_NAME"
mkdir final_installer
electron-installer-dmg dist/HDDcoin-darwin-x64/HDDcoin.app HDDcoin-$HDDCOIN_INSTALLER_VERSION \
--overwrite --out final_installer
LAST_EXIT_CODE=$?
if [ "$LAST_EXIT_CODE" -ne 0 ]; then
	echo >&2 "electron-installer-dmg failed!"
	exit $LAST_EXIT_CODE
fi

if [ "$NOTARIZE" == true ]; then
	echo "Notarize $DMG_NAME on ci"
	cd final_installer || exit
  notarize-cli --file=$DMG_NAME --bundle-id net.hddcoin.blockchain \
	--username "$APPLE_NOTARIZE_USERNAME" --password "$APPLE_NOTARIZE_PASSWORD"
  echo "Notarization step complete"
else
	echo "Not on ci or no secrets so skipping Notarize"
fi

# Notes on how to manually notarize
#
# Ask for username and password. password should be an app specific password.
# Generate app specific password https://support.apple.com/en-us/HT204397
# xcrun altool --notarize-app -f HDDcoin-0.1.X.dmg --primary-bundle-id net.hddcoin.blockchain -u username -p password
# xcrun altool --notarize-app; -should return REQUEST-ID, use it in next command
#
# Wait until following command return a success message".
# watch -n 20 'xcrun altool --notarization-info  {REQUEST-ID} -u username -p password'.
# It can take a while, run it every few minutes.
#
# Once that is successful, execute the following command":
# xcrun stapler staple HDDcoin-0.1.X.dmg
#
# Validate DMG:
# xcrun stapler validate HDDcoin-0.1.X.dmg
