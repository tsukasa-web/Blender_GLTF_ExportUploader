@echo off
cd %~dp0

REM Blenderのパス設定（必要な場合のみ変更）
set BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

REM blenderコマンドが使えるかチェック
where blender >nul 2>nul
if %ERRORLEVEL% equ 0 (
    REM 環境変数のパスが通っている場合
    blender -b --python blender_export.py -- --config config.yaml
) else (
    REM 環境変数のパスが通っていない場合
    if exist %BLENDER_PATH% (
        %BLENDER_PATH% -b --python blender_export.py -- --config config.yaml
    ) else (
        echo Blenderが見つかりません。BLENDER_PATHを設定してください。
        pause
        exit /b 1
    )
)

REM エラーが発生した場合は一時停止
if errorlevel 1 (
    pause
    exit /b 1
)