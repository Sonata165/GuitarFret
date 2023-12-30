pyinstaller main.py \
            -y \
            --clean \
            --onedir \
            --noconsole \
            --icon guitar.icns \
            --name GuitarFret \
            --add-data "resources/Tyros Nylon.sf2:resources" 
