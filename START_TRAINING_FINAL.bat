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
echo Training time: 18-24 hours on RTX 3060 Ti
echo.
pause

cd /d "C:\Users\donmo\Downloads\forward-watch-dataset\forward-watch-dataset"

python -c "from ultralytics import YOLO; import os; os.makedirs('output', exist_ok=True); model = YOLO('yolov8n.pt'); model.train(data='data.yaml', epochs=100, batch=8, imgsz=640, project='output', name='forward-watch', device=0, patience=20, save=True, plots=True)"

pause
