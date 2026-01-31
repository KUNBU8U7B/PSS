# PSS (Simple Programming Script) v1.0

PSS is a lightweight, indentation-based programming language that transpiles to optimized C. It's designed to be human-friendly, fast, and easy to run on low-end hardware.

## Features
- **Clean Syntax**: Indentation-based (like Python) but with a focus on simplicity.
- **High Performance**: Transpiles directly to C with GCC `-O3` optimization.
- **OOP Support**: Classes and methods out of the box.
- **Lightweight**: Zero heavy dependencies, ideal for WSL, Linux, and low-end devices.

## Installation

### Easy Install (Automatic)
**Linux / WSL:**
```bash
bash install.sh
```

### Android (via Termux)
1. Unduh **Termux** (disarankan dari F-Droid).
2. Buka Termux dan jalankan perintah:
```bash
pkg install python clang git -y
git clone <URL_REPOLO>
cd PSS
bash install.sh
```
3. PSS siap digunakan! Ketik `pss test.pss`.

**Windows (PowerShell):**
```powershell
.\install.ps1
```

### Manual Install
**Windows**
1. Clone this repository.
2. Add the folder path to your System Environment `PATH`.
3. Run `pss test.pss`.

### Linux / WSL
1. Clone this repository.
2. Make the wrapper executable: `chmod +x pss`.
3. (Optional) Create an alias: `alias pss='/path/to/pss/pss'`.

## Usage
```pss
program hello
    print "Hello, PSS!"
end
```
Run it:
```bash
pss hello.pss
```

## Contributing
PSS is open-source! Feel free to submit issues or pull requests.
