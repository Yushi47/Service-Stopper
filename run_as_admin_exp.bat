@echo off
REM Get the directory of the batch file
set "batch_dir=%~dp0"

REM Run Python script located in the same directory as the batch file
python "%batch_dir%python-stop-service-exp.py"