@echo off
echo ================================================
echo    FORWARD WATCH TRAINING - EASY START
echo ================================================
echo.
echo Installing required packages...
echo.

REM Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

REM Install YOLOv8
pip install ultralytics

echo.
echo ================================================
echo    STARTING TRAINING
echo ================================================
echo.
echo This will train YOLOv8 to detect:
echo - Ships and boats
echo - Marine debris
echo - Icebergs
echo - Buoys
echo - Kayaks
echo - Logs
echo.
echo Training time: 12-24 hours on RTX 3060 Ti
echo.
pause

REM Run from current directory
python train_forward_watch.py

pause
