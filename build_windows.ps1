# Run on Windows in a clean Python environment. Does not build on Linux.
$ErrorActionPreference = 'Stop'
py -m pip install -r requirements.txt
py -m pip install 'pyinstaller>=6,<7'
py -m PyInstaller --noconfirm --clean --onedir --windowed --name AshkanHotelPro main.py
Write-Host 'Build available in dist/AshkanHotelPro. Test on a clean Windows machine.'
