#!/bin/bash
# PSS UNIVERSAL INSTALLER v1.5.0
# Goal: Auto-install dependencies and globalize pss

echo "===================================================="
echo "      PSS UNIVERSAL INSTALLER v1.5.0"
echo "===================================================="

# 1. Dependency Check & Auto-Install (if possible)
ID=$(grep ^ID= /etc/os-release | cut -d= -f2 | tr -d '"')
echo "Detected Linux: $ID"

install_pkg() {
    case $ID in
        ubuntu|debian|kali|raspbian) sudo apt update && sudo apt install -y gcc binutils ;;
        arch|manjaro) sudo pacman -S --noconfirm gcc binutils ;;
        fedora|rhel|centos) sudo dnf install -y gcc binutils ;;
        alpine) sudo apk add gcc binutils musl-dev ;;
        *) echo "Please ensure 'gcc' and 'binutils' are installed manually." ;;
    esac
}

if ! command -v gcc &> /dev/null; then
    echo "gcc not found. Attempting auto-installation..."
    install_pkg
fi

# 2. Build and Install
INSTALL_DIR="/usr/local/bin"
if [ -n "$TERMUX_VERSION" ]; then INSTALL_DIR="$PREFIX/bin"; fi

echo "Building PSS Native..."
gcc -O3 pss_core.c -o pss_native

# Create Wrapper
cat <<EOF > pss_cmd
#!/bin/bash
DIR="/usr/local/bin"
if [ -n "\$TERMUX_VERSION" ]; then DIR="\$PREFIX/bin"; fi
ARCH_FLAG=""
if [[ "\$(uname -m)" == "aarch64" || "\$(uname -m)" == "arm64" ]]; then ARCH_FLAG="-arm"; fi

"\$DIR/pss_native" \$ARCH_FLAG "\$1" > .temp_pss.s
if [ \$? -eq 0 ]; then
    gcc -nostdlib -no-pie .temp_pss.s -o a.out
    ./a.out
    rm .temp_pss.s a.out
else
    rm .temp_pss.s
fi
EOF

# Move to bin
if [ -n "$TERMUX_VERSION" ]; then
    cp pss_native "$INSTALL_DIR/"
    mv pss_cmd "$INSTALL_DIR/pss"
    chmod +x "$INSTALL_DIR/pss"
    chmod +x "$INSTALL_DIR/pss_native"
else
    sudo cp pss_native "$INSTALL_DIR/"
    sudo mv pss_cmd "$INSTALL_DIR/pss"
    sudo chmod +x "$INSTALL_DIR/pss"
    sudo chmod +x "$INSTALL_DIR/pss_native"
fi

echo "===================================================="
echo "  SUCCESS! PSS v1.5.0 is now global."
echo "  You can now use 'pss' command anywhere."
echo "===================================================="
