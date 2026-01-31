#!/bin/bash

# PSS (Simple Programming Script) Installer
# Platform: Linux / Termux

echo "------------------------------------------------"
echo "   ____  ____________   ____"
echo "  / __ \/ ___/ ___/ | / / /___ _____  ____ _"
echo " / /_/ /\__ \\__ \  |/ / / __ \`/ __ \/ __ \`/"
echo "/ ____/___/ /__/ / /| / / /_/ / / / / /_/ /"
echo "/_/    /____/____/_/ |_/_/\\__,_/_/ /_/\__, /"
echo "                                     /____/"
echo "------------------------------------------------"
echo "   Building the future, one PSS script at a time."
echo ""

INSTALL_DIR="$HOME/.pss"
BINARY_PATH="$INSTALL_DIR/pss"

echo "Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install it first."
    exit 1
fi

if [ -d "/data/data/com.termux" ]; then
    PLATFORM="Termux (Android)"
else
    PLATFORM="Linux/WSL"
fi

echo "Detected Platform: $PLATFORM"
echo "Installing PSS to $INSTALL_DIR..."

# Create directory
mkdir -p "$INSTALL_DIR"

# Copy files (assuming running from the source folder)
cp pss.py "$INSTALL_DIR/"
cp pss "$INSTALL_DIR/"

# Fix line endings and permissions
sed -i 's/\r$//' "$INSTALL_DIR/pss"
chmod +x "$INSTALL_DIR/pss"

# Add to .bashrc if not already there
if ! grep -q "$INSTALL_DIR" "$HOME/.bashrc"; then
    echo "Adding PSS to PATH in .bashrc..."
    echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$HOME/.bashrc"
    echo ""
    echo "SUCCESS: PSS has been installed!"
    echo "Please restart your terminal or run: source ~/.bashrc"
else
    echo "PSS is already in your PATH."
    echo ""
    echo "SUCCESS: PSS is ready to use!"
fi

echo "Try running: pss test.pss"
echo "------------------------------------------------"
