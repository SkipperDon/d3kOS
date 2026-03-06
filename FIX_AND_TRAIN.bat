@echo off
echo ================================================
echo    FIXING DATA.YAML AND STARTING TRAINING
echo ================================================
echo.

cd /d "C:\Users\donmo\Downloads\forward-watch-dataset\forward-watch-dataset"

echo Fixing data.yaml paths...
(
echo path: .
echo train: images/train
echo val: images/val
echo.
echo nc: 6
echo names:
echo   0: ship
echo   1: boat
echo   2: debris
echo   3: buoy
echo   4: kayak
echo   5: log
) > data.yaml

echo data.yaml fixed.
echo.
echo Starting training...
echo Training time: 18-24 hours
echo.
pause

python -c "from ultralytics import YOLO; import os; os.makedirs('output', exist_ok=True); model = YOLO('yolov8n.pt'); model.train(data='data.yaml', epochs=100, batch=8, imgsz=640, project='output', name='forward-watch', device=0, patience=20, save=True, plots=True)"

pause
