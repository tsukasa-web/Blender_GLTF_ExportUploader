#!/bin/bash
cd "$(dirname "$0")"

# クリーンアップ関数
cleanup() {
    if [ -f ".close_after_complete" ]; then
        rm -f ".close_after_complete"
    fi
}

# 終了時に必ずクリーンアップを実行
trap cleanup EXIT

# 正常終了時に自動で閉じる設定
auto_close_terminal() {
    sleep 1  # 完了ダイアログが表示されるのを待つ
    osascript <<EOF
    tell application "Terminal"
        set windowCount to count windows
        repeat with x from 1 to windowCount
            set windowID to id of window x
            if name of window x contains ".command" then
                close window x
            end if
        end repeat
    end tell
EOF
}

# Blenderのパス設定
BLENDER_PATH="/Applications/Blender.app/Contents/MacOS/Blender"
STEAM_BLENDER_PATH="$HOME/Library/Application Support/Steam/steamapps/common/Blender/blender.app/Contents/MacOS/blender"

# Blenderの検索
if [ -x "$BLENDER_PATH" ]; then
    SELECTED_BLENDER="$BLENDER_PATH"
elif [ -x "$STEAM_BLENDER_PATH" ]; then
    SELECTED_BLENDER="$STEAM_BLENDER_PATH"
else
    osascript -e 'display dialog "Blenderが見つかりません。インストール場所を確認してください。" buttons {"OK"} default button "OK" with icon caution'
    exit 1
fi

# 実行権限の自動付与（初回のみ）
if [ ! -x "./export.command" ]; then
    chmod +x "./export.command"
fi

# Blenderの実行
"$SELECTED_BLENDER" -b --python blender_export.py -- --config config.yaml
BLENDER_EXIT_CODE=$?

# エラーチェックと終了処理
if [ $BLENDER_EXIT_CODE -ne 0 ]; then
    # エラー発生時
    osascript -e 'display dialog "エラーが発生しました。詳細はコンソールを確認してください。" buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# 正常終了時
osascript -e 'display dialog "エクスポートが完了しました。" buttons {"OK"} default button "OK" with icon note'

# close_after_completeの値をチェック
if [ -f ".close_after_complete" ]; then
    auto_close_terminal
fi

exit 0