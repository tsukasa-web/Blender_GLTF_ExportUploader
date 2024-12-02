@echo off
cd %~dp0
blender -b pj_clinic.blend --python blender_export.py
pause