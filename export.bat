@echo off
cd %~dp0

REM Blenderのパス設定（必要な場合のみ変更）
set STEAM_PATH="C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe"
set DEFAULT_PATH="C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"

REM blenderコマンドが使えるかチェック
where blender >nul 2>nul
if %ERRORLEVEL% equ 0 (
    REM 環境変数のパスが通っている場合
    blender -b --python blender_export.py -- --config config.yaml
) else (
    REM 環境変数のパスが通っていない場合
    if exist %STEAM_PATH% (
        %STEAM_PATH% -b --python blender_export.py -- --config config.yaml
    ) else if exist %DEFAULT_PATH% (
        %DEFAULT_PATH% -b --python blender_export.py -- --config config.yaml
    ) else (
        echo Blenderが見つかりません。以下のパスを確認してください：
        echo   1. Steam版: %STEAM_PATH%
        echo   2. 通常版: %DEFAULT_PATH%
        pause
        exit /b 1
    )
)

REM エラーが発生した場合は一時停止
if errorlevel 1 (
    pause
    exit /b 1
)