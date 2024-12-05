@echo off
cd %~dp0
blender -b --python blender_export.py -- --config config.yaml
if errorlevel 1 (
    pause
    exit /b 1
)