pyinstaller --name TuringMachine --log-level INFO --noconfirm --onefile --noconsole --windowed --add-data "ui.kv;." --add-binary "help.chm;." --add-binary "icon.png;." --distpath "." --icon="icon.ico" --hiddenimport win32timezone main.py