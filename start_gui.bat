@echo off
echo ========================================
echo    Lancement de l'OCR GUI
echo ========================================
echo.
echo Verification d'Ollama...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Ollama n'est pas lance!
    echo Veuillez d'abord lancer: ollama serve
    pause
    exit /b 1
)

echo [OK] Ollama est actif
echo.
echo Lancement de l'interface graphique...
python ocr_gui.py

pause
