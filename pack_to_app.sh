pyinstaller main.py \
            -y \
            --clean \
            --onedir \
            --noconsole \
            --icon guitar.icns \
            --name GuitarFret \
            --add-data "resources/Acoustic Guitar - Vince.sf2:resources" 
