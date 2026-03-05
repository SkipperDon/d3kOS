@echo off
echo ============================================
echo Fish Species Training - ONE CLICK START
echo ============================================
echo.

REM Create training directory if it doesn't exist
if not exist "C:\fish-training" mkdir "C:\fish-training"
if not exist "C:\fish-training\output" mkdir "C:\fish-training\output"

REM Copy files if they're in the same directory as this script
if exist "%~dp0train_fish_model_483species.py" (
    copy "%~dp0train_fish_model_483species.py" "C:\fish-training\train_fish_model.py"
    echo Copied training script
)

if exist "%~dp0final_all_index.txt" (
    copy "%~dp0final_all_index.txt" "C:\fish-training\final_all_index.txt"
    echo Copied index file
)

echo.
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from python.org
    pause
    exit /b
)

echo.
echo Checking PyTorch installation...
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"
if errorlevel 1 (
    echo.
    echo PyTorch not installed. Installing now...
    echo This will take 5-10 minutes...
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
    pip install pillow numpy scikit-learn tqdm
)

echo.
echo ============================================
echo Starting Training!
echo ============================================
echo This will take 12-16 hours
echo You can close this window and check back later
echo Progress will be saved every epoch
echo ============================================
echo.
pause

cd C:\fish-training
python train_fish_model.py

echo.
echo ============================================
echo Training Complete!
echo ============================================
echo.
echo Your model is saved in: C:\fish-training\output
echo.
echo Look for: fish_classifier_483species_best.onnx
echo Transfer this file to your Raspberry Pi!
echo.
pause
