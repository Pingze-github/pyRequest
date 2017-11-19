pyinstaller --noconfirm --log-level=INFO ^
    --onedir --windowed ^
    --add-data "assets/icon.ico;assets" ^
    --add-data "assets/MSYHMONO.ttf;assets" ^
    --icon=./assets/icon.ico ^
    --name PyRequest ^
    index.py