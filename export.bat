@echo off
cd %~dp0
blender -b --python blender_export.py -- --config config.yaml
if %ERRORLEVEL% neq 0 (
    pause
)