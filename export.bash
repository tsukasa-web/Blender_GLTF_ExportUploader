#!/bin/bash
cd "$(dirname "$0")"

# Blenderのパス設定（必要な場合のみ変更）
BLENDER_PATH="/Applications/Blender.app/Contents/MacOS/Blender"

# blenderコマンドが使えるかチェック
if command -v blender >/dev/null 2>&1; then
    # 環境変数のパスが通っている場合
    blender -b --python blender_export.py -- --config config.yaml
else
    # 環境変数のパスが通っていない場合
    if [ -x "$BLENDER_PATH" ]; then
        "$BLENDER_PATH" -b --python blender_export.py -- --config config.yaml
    else
        echo "Blenderが見つかりません。BLENDER_PATHを設定してください。"
        read -p "Press [Enter] to exit..."
        exit 1
    fi
fi

# エラーが発生した場合は一時停止
if [ $? -ne 0 ]; then
    read -p "Press [Enter] to exit..."
    exit 1
fi