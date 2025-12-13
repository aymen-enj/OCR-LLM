@echo off
echo ========================================================
echo       CREATION DE L'EXECUTABLE (.EXE)
echo ========================================================

echo.
echo [1/3] Verification de PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo Erreur installation PyInstaller.
    pause
    exit /b
)

echo.
echo [2/3] Compilation en cours...
echo Cela peut prendre 1 a 2 minutes.
echo Inclusion des bibliotheques graphiques (CustomTkinter, TkinterDnD)...

pyinstaller --noconsole --onefile ^
    --name "Ultimate_OCR_App" ^
    --collect-all "customtkinter" ^
    --collect-all "tkinterdnd2" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "babel.numbers" ^
    ocr_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ ECHEC DE LA COMPILATION
    pause
    exit /b
)

echo.
echo [3/3] Nettoyage...
rmdir /s /q build
del /q Ultimate_OCR_App.spec

echo.
echo ========================================================
echo ✅ SUCCES !
echo Votre executable est ici : dist\Ultimate_OCR_App.exe
echo ========================================================
echo.
pause
