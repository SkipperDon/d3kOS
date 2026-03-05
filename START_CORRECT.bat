@echo off
echo ================================================
echo    FORWARD WATCH TRAINING
echo ================================================
echo.
echo Training YOLOv8 to detect 6 marine objects:
echo   - Ships and boats
echo   - Marine debris
echo   - Buoys, kayaks, logs
echo.
echo GPU: NVIDIA RTX 3060 Ti
echo Duration: 12-24 hours
echo.
pause

cd /d "C:\Users\donmo\Downloads\forward-watch-complete"
python train_forward_watch_CORRECT.py

pause
