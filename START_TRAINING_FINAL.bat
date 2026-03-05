@echo off
echo ================================================
echo    FORWARD WATCH TRAINING - FINAL VERSION
echo ================================================
echo.
echo Training YOLOv8 to detect:
echo - Ships and boats
echo - Marine debris
echo - Buoys, kayaks, logs
echo.
echo Training time: 12-24 hours on RTX 3060 Ti
echo Output: C:\Users\donmo\Downloads\forward-watch-complete\output
echo.
pause

cd /d C:\Users\donmo\Downloads\forward-watch-complete
python train_forward_watch_FINAL.py

pause
