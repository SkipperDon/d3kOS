@echo off
REM ============================================================================
REM Fish Species Model Training - Automated Windows Installer
REM For NVIDIA RTX 3060 Ti
REM ============================================================================

color 0A
echo.
echo ============================================================================
echo                FISH SPECIES MODEL TRAINING INSTALLER
echo                        For Windows + NVIDIA GPU
echo ============================================================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [ERROR] This script must be run as Administrator!
    echo.
    echo Right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo [STEP 1/6] Checking Python installation...
echo ----------------------------------------------------------------------------

python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [X] Python is NOT installed!
    echo.
    echo Please install Python 3.10 or 3.11 from: https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
) else (
    python --version
    echo [OK] Python is installed
)
echo.

REM Check Python version
echo [STEP 2/6] Checking Python version...
echo ----------------------------------------------------------------------------
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [WARNING] Python version might be too old
    echo Recommended: Python 3.10 or 3.11
    echo.
) else (
    echo [OK] Python version is compatible
)
echo.

REM Check CUDA installation
echo [STEP 3/6] Checking NVIDIA CUDA installation...
echo ----------------------------------------------------------------------------
nvcc --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [X] CUDA Toolkit is NOT installed!
    echo.
    echo You MUST install CUDA Toolkit first:
    echo.
    echo 1. Go to: https://developer.nvidia.com/cuda-downloads
    echo 2. Select: Windows ^> x86_64 ^> 11 ^> exe (local)
    echo 3. Download and run the installer (~3GB)
    echo 4. Choose "Express Installation"
    echo 5. Reboot your PC after installation
    echo 6. Run this script again
    echo.
    echo After installing CUDA, run this script again!
    echo.
    pause
    exit /b 1
) else (
    nvcc --version | findstr "release"
    echo [OK] CUDA Toolkit is installed
)
echo.

REM Check GPU
echo [STEP 4/6] Checking NVIDIA GPU...
echo ----------------------------------------------------------------------------
nvidia-smi >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [X] nvidia-smi not found - GPU driver issue!
    echo.
    echo Please install latest NVIDIA drivers from:
    echo https://www.nvidia.com/download/index.aspx
    echo.
    pause
    exit /b 1
) else (
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo [OK] NVIDIA GPU detected
)
echo.

REM Install PyTorch with CUDA
echo [STEP 5/6] Installing PyTorch with CUDA support...
echo ----------------------------------------------------------------------------
echo This will download ~2GB and may take 5-10 minutes...
echo.

python -c "import torch" >nul 2>&1
if %errorLevel% EQU 0 (
    echo [OK] PyTorch already installed
    python -c "import torch; print('PyTorch version:', torch.__version__)"
    python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
) else (
    echo Installing PyTorch...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    if %errorLevel% NEQ 0 (
        echo [X] PyTorch installation failed!
        pause
        exit /b 1
    )
    echo [OK] PyTorch installed successfully
)
echo.

REM Install other dependencies
echo [STEP 6/6] Installing training dependencies...
echo ----------------------------------------------------------------------------
echo Installing: pillow, matplotlib, numpy, tensorboard, onnx, scikit-learn, tqdm
echo.

pip install pillow matplotlib numpy tensorboard onnx onnxruntime scikit-learn tqdm --quiet --disable-pip-version-check

if %errorLevel% NEQ 0 (
    echo [WARNING] Some packages may have failed to install
    echo Try running: pip install pillow matplotlib numpy tensorboard onnx scikit-learn tqdm
) else (
    echo [OK] All dependencies installed
)
echo.

REM Final GPU test
echo ============================================================================
echo                         INSTALLATION COMPLETE
echo ============================================================================
echo.
echo Testing GPU with PyTorch...
echo ----------------------------------------------------------------------------

python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'); print('GPU Memory:', f'{torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB' if torch.cuda.is_available() else 'N/A')"

echo.
echo ============================================================================
echo                            INSTALLATION SUMMARY
echo ============================================================================
echo.
echo [OK] Python installed
echo [OK] CUDA Toolkit installed
echo [OK] NVIDIA GPU detected
echo [OK] PyTorch with CUDA support installed
echo [OK] Training dependencies installed
echo.
echo ============================================================================
echo                              NEXT STEPS
echo ============================================================================
echo.
echo 1. Wait for dataset download to complete on Raspberry Pi
echo    Check progress: ssh -i %%USERPROFILE%%\.ssh\d3kos_key d3kos@192.168.1.237 'find /opt/d3kos/datasets/fish-worldwide -name "*.jpg" | wc -l'
echo.
echo 2. Create training directory:
echo    mkdir C:\fish-training\dataset
echo.
echo 3. Transfer dataset from Pi to this PC (takes 1-2 hours):
echo    scp -r -i %%USERPROFILE%%\.ssh\d3kos_key d3kos@192.168.1.237:/opt/d3kos/datasets/fish-worldwide C:\fish-training\dataset\
echo.
echo 4. Copy training script to C:\fish-training\
echo.
echo 5. Edit train_fish_model.py line 17:
echo    DATASET_ROOT = Path("C:/fish-training/dataset/fish-worldwide")
echo.
echo 6. Start training:
echo    cd C:\fish-training
echo    python train_fish_model.py
echo.
echo Training will take approximately 12-16 hours on your RTX 3060 Ti.
echo.
echo ============================================================================
echo.

pause
