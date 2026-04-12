@echo off
REM Deploy FI4 backup-status CRM page to Admin VM (192.168.236.5)
REM Run this from Windows when VM is running.
REM Requires pscp.exe and plink.exe (PuTTY) in PATH or same directory.

setlocal

set VM_HOST=192.168.236.5
set VM_USER=skipper
set VM_PASS=d3kos2026$
set CRM_DIR=/home/d3kos-admin

REM Helm-OS repo root is 4 levels up from this script's directory:
REM   scripts/ -> fi4-config-backup/ -> features/ -> deployment/ -> Helm-OS/
set REPO_ROOT=%~dp0..\..\..\..\

set APP_PY=%REPO_ROOT%deployment\features\support-tickets\crm\app_patched.py
set BACKUP_HTML=%REPO_ROOT%deployment\features\support-tickets\crm\backup_status.html

echo.
echo Deploy FI4 Backup Status to Admin CRM VM
echo ==========================================
echo VM:        %VM_HOST%
echo CRM path:  %CRM_DIR%
echo.

echo Uploading app_patched.py...
pscp -pw "%VM_PASS%" "%APP_PY%" %VM_USER%@%VM_HOST%:/tmp/app_patched.py
if errorlevel 1 goto error

echo Uploading backup_status.html...
pscp -pw "%VM_PASS%" "%BACKUP_HTML%" %VM_USER%@%VM_HOST%:/tmp/backup_status.html
if errorlevel 1 goto error

echo Uploading install script...
pscp -pw "%VM_PASS%" "%~dp0install-crm-backup-status.sh" %VM_USER%@%VM_HOST%:/tmp/install-crm-backup-status.sh
if errorlevel 1 goto error

echo Running install script on VM...
plink -batch -pw "%VM_PASS%" %VM_USER%@%VM_HOST% "chmod +x /tmp/install-crm-backup-status.sh && echo '%VM_PASS%' | sudo -S /tmp/install-crm-backup-status.sh"
if errorlevel 1 goto error

echo.
echo Deploy complete.
echo Backup Status page: http://%VM_HOST%:5000/backup-status
goto end

:error
echo.
echo ERROR: Deploy failed. Check that VM is running and pscp/plink are in PATH.
echo Download PuTTY from https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html

:end
pause
