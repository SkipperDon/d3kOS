@echo off
REM ============================================================================
REM Simple Fish Training Installer - No CUDA Toolkit Required
REM Just installs PyTorch with pre-built CUDA binaries
REM ============================================================================

color 0A
echo.
echo ============================================================================
echo           SIMPLE FISH TRAINING INSTALLER
echo         (No Visual Studio or CUDA Toolkit needed)
REM ============================================================================
echo.

REM Check Python
echo [1/3] Checking Python...
python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [X] Python NOT installed
    echo.
    echo Install Python from: https://www.python.org/downloads/
    echo Check "Add Python to PATH" during install!
    pause
    exit /b 1
)
python --version
echo [OK] Python found
echo.

REM Check GPU
echo [2/3] Checking GPU...
nvidia-smi --query-gpu=name --format=csv,noheader >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [X] NVIDIA GPU not detected
    echo Make sure NVIDIA drivers are installed
    pause
    exit /b 1
)
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo [OK] GPU detected
echo.

REM Install everything
echo [3/3] Installing PyTorch + dependencies...
echo This will download ~2GB, please wait 5-10 minutes...
echo.

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install pillow matplotlib numpy tensorboard onnx onnxruntime scikit-learn tqdm

echo.
echo ============================================================================
echo                         TESTING GPU
echo ============================================================================
echo.

python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE'); print('GPU Memory:', f'{torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB' if torch.cuda.is_available() else 'N/A')"

echo.
echo ============================================================================
echo If you see "CUDA available: True" above, you're ready to train!
echo ============================================================================
echo.
pause
