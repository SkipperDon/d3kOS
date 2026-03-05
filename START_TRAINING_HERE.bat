@echo off
echo ================================================
echo    FORWARD WATCH TRAINING - EASY START
echo ================================================
echo.
echo This will train YOLOv8 to detect:
echo - Ships and boats
echo - Marine debris
echo - Icebergs
echo.
echo Training time: 12-24 hours on RTX 3060 Ti
echo.
echo Current directory: %CD%
echo.
pause

REM Run from current directory (wherever the batch file is)
python train_forward_watch.py

pause
