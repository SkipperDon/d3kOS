@echo off
REM ============================================================================
REM Uninstall All Fish Training Software
REM Removes PyTorch and all packages we installed
REM ============================================================================

color 0C
echo.
echo ============================================================================
echo               UNINSTALL FISH TRAINING SOFTWARE
echo ============================================================================
echo.
echo This will remove:
echo   - PyTorch
echo   - TorchVision
echo   - TorchAudio
echo   - Pillow
echo   - Matplotlib
echo   - Numpy
echo   - TensorBoard
echo   - ONNX
echo   - ONNXRuntime
echo   - scikit-learn
echo   - tqdm
echo.
echo This will NOT remove:
echo   - Python itself
echo   - CUDA Toolkit
echo   - Visual Studio
echo   - NVIDIA drivers
echo.

pause

echo.
echo [1/11] Uninstalling PyTorch...
pip uninstall torch -y

echo [2/11] Uninstalling TorchVision...
pip uninstall torchvision -y

echo [3/11] Uninstalling TorchAudio...
pip uninstall torchaudio -y

echo [4/11] Uninstalling Pillow...
pip uninstall pillow -y

echo [5/11] Uninstalling Matplotlib...
pip uninstall matplotlib -y

echo [6/11] Uninstalling Numpy...
pip uninstall numpy -y

echo [7/11] Uninstalling TensorBoard...
pip uninstall tensorboard -y

echo [8/11] Uninstalling ONNX...
pip uninstall onnx -y

echo [9/11] Uninstalling ONNXRuntime...
pip uninstall onnxruntime -y

echo [10/11] Uninstalling scikit-learn...
pip uninstall scikit-learn -y

echo [11/11] Uninstalling tqdm...
pip uninstall tqdm -y

echo.
echo ============================================================================
echo                     UNINSTALL COMPLETE
echo ============================================================================
echo.
echo All fish training packages have been removed.
echo.
echo Python, CUDA, and NVIDIA drivers remain installed.
echo These are safe to keep - they don't pose any security risk.
echo.
echo If you want to remove Python too:
echo   - Go to: Settings ^> Apps ^> Python
echo   - Click Uninstall
echo.
pause
