# Blender GLTF/GLBエクスポーター

BlenderのGLTF/GLBエクスポート機能をコンソールから実行し、FTPアップロードまで自動化するツールです。複数のBlenderファイルを一括で処理し、それぞれ個別の出力設定やアップロード先を指定できます。

## 機能
- Blenderシーンのコンソールからのバッチエクスポート
- 詳細なエクスポート設定のカスタマイズ
- 複数のBlenderファイルの一括処理
- エクスポートしたファイルの自動FTPアップロード
- ファイルごとの個別アップロード先指定

## 必要環境
- Blender 4.2.3以上
- Python 3.x （Blenderに同梱のもので動作）

## インストール方法

### 1. ファイルの配置
以下の2つのファイルを用意します：
- `blender_export.py`（エクスポートスクリプト）
- `config.yaml`（設定ファイル）

#### 配置方法（3つの選択肢）

1. **プロジェクトフォルダに配置（推奨）**
   ```
   your_project/
   ├── your_file.blend
   ├── blender_export.py
   └── config.yaml
   ```
   - Blenderファイルと同じフォルダに配置するだけで使えます
   - プロジェクトごとに設定を変えられる利点があります

2. **Blenderのスクリプトフォルダに配置**
   - Windows: `C:\Users\[ユーザー名]\AppData\Roaming\Blender Foundation\Blender\[バージョン]\scripts\startup`
   - Mac: `/Users/[ユーザー名]/Library/Application Support/Blender/[バージョン]/scripts/startup`
   - Linux: `/home/[ユーザー名]/.config/blender/[バージョン]/scripts/startup`

3. **カスタムフォルダに配置**
   ```
   C:\BlenderScripts\  # 例：任意の場所に専用フォルダを作成
   ├── blender_export.py
   └── config.yaml
   ```

### 2. スクリプトの実行方法

#### A. プロジェクトフォルダに配置した場合
1. コマンドプロンプト（またはターミナル）を開く
2. プロジェクトフォルダに移動
   ```bash
   cd "C:\Path\To\Your\Project"
   ```
3. スクリプトを実行
   ```bash
   blender -b your_file.blend --python blender_export.py
   ```

#### B. その他のフォルダに配置した場合
1. コマンドプロンプト（またはターミナル）を開く
2. スクリプトのフルパスを指定して実行
   ```bash
   blender -b your_file.blend --python "C:\Path\To\Script\blender_export.py"
   ```

### 3. コマンドプロンプト/ターミナルの開き方

#### Windows
1. `Win + R`キーを押す
2. `cmd`と入力してEnter
3. または、フォルダで`Shift + 右クリック`→「ここでコマンドウィンドウを開く」

#### Mac
1. `Finder`→`アプリケーション`→`ユーティリティ`→`ターミナル`
2. または、`Spotlight`（⌘ + Space）で"ターミナル"を検索

#### Linux
1. `Ctrl + Alt + T`（多くのディストリビューションでのデフォルトショートカット）
2. または、アプリケーションメニューから「ターミナル」を検索

### 4. 便利な使い方

#### Windowsでバッチファイルを作成
1. テキストエディタを開く
2. 以下の内容を入力
   ```batch
   @echo off
   "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" -b --python blender_export.py -- --config config.yaml
   pause
   ```
3. `export.bat`として保存
4. ダブルクリックで実行可能に

#### Macでシェルスクリプトを作成
1. テキストエディタを開く
2. 以下の内容を入力
   ```bash
   #!/bin/bash
   "/Applications/Blender.app/Contents/MacOS/Blender" -b --python blender_export.py -- --config config.yaml
   read -p "Press [Enter] to exit..."
   ```
3. `export.sh`として保存
4. ターミナルで実行権限を付与
   ```bash
   chmod +x export.sh
   ```

### 5. 設定ファイル（config.yaml）の構成

#### マルチファイル設定（blend_files）
|
 パラメータ
|
 説明
|
 必須
|
|
------------
|
------
|
------
|
|
`file_path`
|
 Blenderファイルのパス
|
 はい
|
|
`output_name`
|
 出力するGLTF/GLBファイル名
|
 はい
|
|
`remote_path`
|
 個別のアップロード先パス
|
 いいえ
|

設定例：
```yaml
blend_files:
  - file_path: "./characters/hero.blend"
    output_name: "hero.gltf"
    remote_path: "/assets/characters/"

  - file_path: "./stages/stage01.blend"
    output_name: "stage01.gltf"
    remote_path: "/assets/stages/"
```

### FTPアップロード設定

#### 基本設定（ftp_settings）
すべてのファイルに適用されるデフォルトの設定です。
```yaml
ftp_settings:
  host: "ftp.example.com"
  port: 21
  username: "your-username"
  password: "your-password"
  remote_directory: "/assets/"  # デフォルトのアップロード先
```

#### 個別設定（remote_path）
特定のファイルに対して個別のアップロード先を指定できます。
- 指定がある場合：そのパスが使用されます
- 指定がない場合：ftp_settingsのremote_directoryが使用されます

### 使用例

#### 1. キャラクターとステージの一括処理
```yaml
blend_files:
  - file_path: "./character1.blend"
    output_name: "hero.gltf"
    remote_path: "/assets/characters/"

  - file_path: "./character2.blend"
    output_name: "enemy.gltf"
    remote_path: "/assets/characters/"

  - file_path: "./stage.blend"
    output_name: "stage1.gltf"
    remote_path: "/assets/stages/"
```

#### 2. 同じフォルダに出力する場合
```yaml
ftp_settings:
  remote_directory: "/assets/models/"

blend_files:
  - file_path: "./model1.blend"
    output_name: "model1.gltf"

  - file_path: "./model2.blend"
    output_name: "model2.gltf"
```

### コマンドライン
```bash
# 基本的な使用方法
blender -b --python blender_export.py -- --config config.yaml

# 設定ファイルを指定
blender -b --python blender_export.py -- --config custom_config.yaml
```

### 設定パラメータの詳細

#### エクスポート基本設定（export_settings）
|
 パラメータ
|
 説明
|
 デフォルト値
|
|
------------
|
------
|
--------------
|
|
`filepath`
|
 出力ファイルパス
|
`""`
|
|
`check_existing`
|
 既存ファイルの上書き確認
|
`true`
|
|
`export_format`
|
 出力形式（GLTF_SEPARATE/GLB）
|
`"GLTF_SEPARATE"`
|
|
`export_copyright`
|
 著作権情報
|
`""`
|

#### インクルード設定
|
 パラメータ
|
 説明
|
 デフォルト値
|
|
------------
|
------
|
--------------
|
|
`use_selection`
|
 選択オブジェクトのみ
|
`false`
|
|
`use_visible`
|
 表示オブジェクトのみ
|
`false`
|
|
`use_renderable`
|
 レンダリング可能なオブジェクトのみ
|
`false`
|
|
`use_active_collection`
|
 アクティブコレクションのみ
|
`false`
|
|
`use_active_scene`
|
 アクティブシーンのみ
|
`true`
|

#### メッシュ設定
|
 パラメータ
|
 説明
|
 デフォルト値
|
|
------------
|
------
|
--------------
|
|
`export_apply`
|
 モディファイアを適用
|
`false`
|
|
`export_texcoords`
|
 UV座標をエクスポート
|
`true`
|
|
`export_normals`
|
 法線をエクスポート
|
`true`
|
|
`export_tangents`
|
 接線をエクスポート
|
`false`
|
|
`export_colors`
|
 頂点カラーをエクスポート
|
`true`
|

#### アニメーション設定
|
 パラメータ
|
 説明
|
 デフォルト値
|
|
------------
|
------
|
--------------
|
|
`export_animations`
|
 アニメーションをエクスポート
|
`false`
|
|
`export_frame_range`
|
 フレーム範囲を制限
|
`true`
|
|
`export_frame_step`
|
 フレームステップ（1-120）
|
`1`
|
|
`export_force_sampling`
|
 常にサンプリング
|
`true`
|

#### テクスチャ設定
|
 パラメータ
|
 説明
|
 デフォルト値
|
|
------------
|
------
|
--------------
|
|
`export_image_format`
|
 画像フォーマット（AUTO/JPEG/WEBP/NONE）
|
`"AUTO"`
|
|
`export_jpeg_quality`
|
 JPEG品質（0-100）
|
`75`
|
|
`export_image_quality`
|
 画像品質（0-100）
|
`75`
|

#### Draco圧縮設定
|
 パラメータ
|
 説明
|
 デフォルト値
|
|
------------
|
------
|
--------------
|
|
`export_draco_mesh_compression_enable`
|
 Draco圧縮を使用
|
`false`
|
|
`export_draco_mesh_compression_level`
|
 圧縮レベル（0-10）
|
`6`
|
|
`export_draco_position_quantization`
|
 位置の量子化（0-30）
|
`14`
|
|
`export_draco_normal_quantization`
|
 法線の量子化（0-30）
|
`10`
|

#### FTP設定（ftp_settings）
|
 パラメータ
|
 説明
|
 デフォルト値
|
|
------------
|
------
|
--------------
|
|
`host`
|
 FTPサーバーのホスト名
|
`""`
|
|
`port`
|
 FTPポート番号
|
`21`
|
|
`username`
|
 FTPユーザー名
|
`""`
|
|
`password`
|
 FTPパスワード
|
`""`
|
|
`remote_directory`
|
 デフォルトのアップロード先
|
`"/"`
|

### トラブルシューティング

#### よくあるエラーと解決方法
1. 「'blender'は認識されていないコマンドです」
   - Blenderのインストールフォルダを環境変数PATHに追加する必要があります
   - または、Blenderの実行ファイルのフルパスを使用してください（こちらが手っ取り早いです）
   ```bash
   "C:\Program Files\Blender Foundation\Blender [version]\blender.exe" -b ...
   ```
   パスの例（Win）
   ```
   "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
   "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe"
   ```
   パスの例（Mac）
   ```
   "/Applications/Blender.app/Contents/MacOS/Blender"
   "~/Library/Application Support/Steam/steamapps/common/Blender/blender.app/Contents/MacOS/blender"
   ```

2. 「ファイルが見つかりません」
   - パスに日本語やスペースが含まれていないか確認
   - すべてのパスを「"（ダブルクォート）」で囲む
   - 相対パスではなく絶対パスを使用してみる

3. 「FTPホストが設定されていません」
   - config.yamlのFTP設定を確認
   - インデントが正しいか確認
   - 設定値が空でないか確認

4. 「file_pathが指定されていないファイルがあります」
   - blend_filesセクションの各エントリにfile_pathが正しく設定されているか確認
   - YAMLのインデントが正しいか確認

### 注意事項
1. エクスポート関連
   - モディファイアを適用する設定（`export_apply`）を使用する場合、シェイプキーのエクスポートができなくなります
   - マルチアーマチュアを含むエクスポートでは、`export_anim_single_armature`オプションはサポートされません
   - WebPエクスポートを使用する場合、既にWebP形式のテクスチャに対しては何も行われません

2. FTPアップロード関連
   - `remote_path`を指定しない場合は、`ftp_settings`の`remote_directory`が使用されます
   - FTPサーバーのパスは必ず「/」（フォワードスラッシュ）を使用
   - パスの最後は必ず「/」で終わるようにしてください

3. 一括処理関連
   - 一括処理中にエラーが発生しても、残りのファイルの処理は継続されます
   - 大量のファイルを処理する場合は、小さなバッチに分けることを推奨します

### ベストプラクティス
1. ファイル管理
   ```
   project/
   ├── blender_export.py
   ├── config.yaml
   ├── export.bat
   ├── models/
   │   ├── characters/
   │   │   ├── hero.blend
   │   │   └── enemy.blend
   │   └── stages/
   │       └── stage01.blend
   └── output/
   ```

2. 設定ファイルのバックアップ
   - プロジェクトごとに設定ファイルを用意
   ```
   config_characters.yaml
   config_stages.yaml
   config_props.yaml
   ```

### ライセンス
このツールはオープンソースソフトウェアとして提供されています。