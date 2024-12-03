# Blender GLTF/GLBエクスポーター

BlenderのGLTF/GLBエクスポート機能をコンソールから実行し、FTPアップロードまで自動化するツールです。

## 機能
- Blenderシーンのコンソールからのバッチエクスポート
- 複数の.blendファイルの一括処理
- 詳細なエクスポート設定のカスタマイズ
- エクスポートしたファイルの自動FTPアップロード

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

## 使用方法

### コマンドライン
```bash
# 基本的な使用方法
blender -b your_file.blend --python blender_export.py

# 出力ファイル名を指定
blender -b your_file.blend --python blender_export.py -- --output model.gltf

# 設定ファイルを指定
blender -b your_file.blend --python blender_export.py -- --config custom_config.yaml

# 両方を指定
blender -b your_file.blend --python blender_export.py -- --config custom_config.yaml --output model.gltf
```

## 設定ファイル（config.yaml）

### 基本設定
| パラメータ         | 説明                                            | デフォルト値 |
| ------------------ | ----------------------------------------------- | ------------ |
| `filepath`         | 出力ファイルパス                                | `""`         |
| `check_existing`   | 既存ファイルの上書き確認                        | `true`       |
| `export_format`    | 出力形式 - Binary(効率的) or JSON(編集しやすい) | `""`         |
| `export_copyright` | 著作権情報                                      | `""`         |
| `gltf_export_id`   | エクスポーターの識別子                          | `""`         |

### その他の基本設定
| パラメータ             | 説明                             | デフォルト値     |
| ---------------------- | -------------------------------- | ---------------- |
| `collection`           | ソースコレクション               | `""`             |
| `at_collection_center` | コレクションの中心でエクスポート | `false`          |
| `will_save_settings`   | エクスポート設定を保存           | `false`          |
| `filter_glob`          | フィルターグロブ                 | `"*.glb;*.gltf"` |

### Include設定
#### Limit to
| パラメータ                          | 説明                               | デフォルト値 |
| ----------------------------------- | ---------------------------------- | ------------ |
| `use_selection`                     | 選択オブジェクトのみ               | `false`      |
| `use_visible`                       | 表示オブジェクトのみ               | `false`      |
| `use_renderable`                    | レンダリング可能なオブジェクトのみ | `false`      |
| `use_active_collection`             | アクティブコレクションのみ         | `false`      |
| `use_active_collection_with_nested` | ネストされたコレクションを含める   | `true`       |
| `use_active_scene`                  | アクティブシーンのみ               | `true`       |

#### Data
| パラメータ       | 説明                                              | デフォルト値 |
| ---------------- | ------------------------------------------------- | ------------ |
| `export_extras`  | カスタムプロパティをglTF extrasとしてエクスポート | `false`      |
| `export_cameras` | カメラをエクスポート                              | `false`      |
| `export_lights`  | ライトをエクスポート                              | `false`      |

### Transform設定
| パラメータ   | 説明                             | デフォルト値 |
| ------------ | -------------------------------- | ------------ |
| `export_yup` | glTF規約のY-up方向でエクスポート | `true`       |

### Mesh設定
| パラメータ                | 説明                                       | デフォルト値 |
| ------------------------- | ------------------------------------------ | ------------ |
| `export_apply`            | モディファイアを適用（アーマチュアを除く） | `false`      |
| `export_texcoords`        | UV座標                                     | `true`       |
| `export_normals`          | 法線                                       | `true`       |
| `export_tangents`         | 接線                                       | `false`      |
| `export_attributes`       | カスタム属性                               | `false`      |
| `use_mesh_edges`          | エッジ                                     | `false`      |
| `use_mesh_vertices`       | 頂点                                       | `false`      |
| `export_shared_accessors` | 共有アクセサーを使用                       | `false`      |

### 頂点カラー設定
| パラメータ                                    | 説明                                             | デフォルト値 |
| --------------------------------------------- | ------------------------------------------------ | ------------ |
| `export_vertex_color`                         | 頂点カラーの使用方法 (MATERIAL, ACTIVE, NONE)    | `MATERIAL`   |
| `export_all_vertex_colors`                    | すべての頂点カラーをエクスポート                 | `false`      |
| `export_active_vertex_color_when_no_material` | マテリアルがない場合アクティブな頂点カラーを使用 | `true`       |

### マテリアル設定
| パラメータ                   | 説明                                      | デフォルト値 |
| ---------------------------- | ----------------------------------------- | ------------ |
| `export_materials`           | マテリアル (EXPORT, PLACEHOLDER, NONE)    | `EXPORT`     |
| `export_image_format`        | 画像フォーマット (AUTO, JPEG, WEBP, NONE) | `AUTO`       |
| `export_jpeg_quality`        | JPEG品質 (0-100)                          | `75`         |
| `export_image_quality`       | 画像品質 (0-100)                          | `75`         |
| `export_image_add_webp`      | WebPテクスチャを作成                      | `false`      |
| `export_image_webp_fallback` | WebPのフォールバックとしてPNGを作成       | `false`      |
| `export_keep_originals`      | オリジナルテクスチャを保持                | `false`      |

### Compression (Draco)
| パラメータ                             | 説明                  | デフォルト値 |
| -------------------------------------- | --------------------- | ------------ |
| `export_draco_mesh_compression_enable` | Draco圧縮を使用       | `false`      |
| `export_draco_mesh_compression_level`  | 圧縮レベル (0-10)     | `6`          |
| `export_draco_position_quantization`   | 位置の量子化 (0-30)   | `14`         |
| `export_draco_normal_quantization`     | 法線の量子化 (0-30)   | `10`         |
| `export_draco_texcoord_quantization`   | UV座標の量子化 (0-30) | `12`         |
| `export_draco_color_quantization`      | カラーの量子化 (0-30) | `10`         |
| `export_draco_generic_quantization`    | その他の量子化 (0-30) | `12`         |

### Animation設定
| パラメータ              | 説明                                                                         | デフォルト値 |
| ----------------------- | ---------------------------------------------------------------------------- | ------------ |
| `export_animations`     | アニメーション                                                               | `false`      |
| `export_animation_mode` | アニメーションモード (ACTIONS, ACTIVE_ACTIONS, BROADCAST, NLA_TRACKS, SCENE) | `ACTIONS`    |
| `export_bake_animation` | すべてのオブジェクトアニメーションをベイク                                   | `false`      |
| `export_current_frame`  | 現在のフレームをレスト変換として使用                                         | `false`      |
| `export_frame_range`    | フレーム範囲を制限                                                           | `true`       |
| `export_frame_step`     | フレームステップ (1-120)                                                     | `1`          |

### シェイプキー設定
| パラメータ                   | 説明                                 | デフォルト値 |
| ---------------------------- | ------------------------------------ | ------------ |
| `export_morph`               | シェイプキー                         | `true`       |
| `export_morph_normal`        | シェイプキーの法線                   | `true`       |
| `export_morph_tangent`       | シェイプキーの接線                   | `false`      |
| `export_morph_animation`     | シェイプキーアニメーション           | `true`       |
| `export_morph_reset_sk_data` | アクション間でシェイプキーをリセット | `true`       |

### GLTF圧縮設定
| パラメータ            | 説明                                                     | デフォルト値 |
| --------------------- | -------------------------------------------------------- | ------------ |
| `export_use_gltfpack` | gltfpackを使用してメッシュの簡略化やテクスチャ圧縮を行う | `false`      |
| `export_gltfpack_tc`  | KTX2形式でテクスチャを圧縮                               | `true`       |
| `export_gltfpack_tq`  | テクスチャエンコード品質 (1-10)                          | `8`          |
| `export_gltfpack_si`  | メッシュ単純化率 (0-1)                                   | `1.0`        |
| `export_gltfpack_sa`  | 強制的なメッシュ単純化                                   | `false`      |
| `export_gltfpack_slb` | 境界頂点をロック                                         | `false`      |
| `export_gltfpack_vp`  | 位置の量子化 (1-16)                                      | `14`         |
| `export_gltfpack_vt`  | UV座標の量子化 (1-16)                                    | `12`         |
| `export_gltfpack_vn`  | 法線/接線の量子化 (1-16)                                 | `8`          |
| `export_gltfpack_vc`  | 頂点カラーの量子化 (1-16)                                | `8`          |
| `export_gltfpack_vpi` | 頂点位置属性タイプ (Integer, Normalized, Floating-point) | `Integer`    |
| `export_gltfpack_noq` | 量子化を無効化                                           | `true`       |

### 出力設定
| パラメータ         | 説明             | デフォルト値 |
| ------------------ | ---------------- | ------------ |
| `output_directory` | 出力ディレクトリ | `"./output"` |

### FTP設定
| パラメータ         | 説明                                 | デフォルト値 |
| ------------------ | ------------------------------------ | ------------ |
| `host`             | FTPサーバーのホスト名                | `""`         |
| `port`             | FTPポート番号                        | `21`         |
| `username`         | FTPユーザー名                        | `""`         |
| `password`         | FTPパスワード                        | `""`         |
| `remote_directory` | アップロード先のリモートディレクトリ | `"/"`        |

### 処理対象ファイルリスト設定
| パラメータ    | 説明                 | 例                      |
| ------------- | -------------------- | ----------------------- |
| `file_path`   | .blendファイルのパス | `"./pj_clinic.blend"`   |
| `output_name` | 出力ファイル名       | `"output.gltf"`         |
| `remote_path` | 個別のアップロード先 | `"/assets/model/test/"` |

## 注意事項
- モディファイアを適用する設定（`export_apply`）を使用する場合、シェイプキーのエクスポートができなくなります
- アニメーションエクスポートを有効にする場合は、`export_animations`を`true`に設定する必要があります
- WebPエクスポートを使用する場合、既にWebP形式のテクスチャに対しては何も行われません
- 複数ファイルを処理する場合、各ファイルの設定は`blend_files`セクションで個別に指定できます
- 処理対象ファイルリストで個別のアップロード先を指定しなかった場合はアップロード先のリモートディレクトリがデフォルト値として使用されます

## トラブルシューティング

### よくあるエラーと解決方法

1. **「'blender'は認識されていないコマンドです」**
   - Blenderのインストールフォルダを環境変数PATHに追加する必要があります
   - または、Blenderの実行ファイルのフルパスを使用してください
   ```bash
   "C:\Program Files\Blender Foundation\Blender [version]\blender.exe" -b ...
   ```
   パスの例：
   - Windows:
   ```
   "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
   "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe"
   ```
   - Mac:
   ```
   "/Applications/Blender.app/Contents/MacOS/Blender"
   "~/Library/Application Support/Steam/steamapps/common/Blender/blender.app/Contents/MacOS/blender"
   ```

2. **「ファイルが見つかりません」**
   - パスに日本語やスペースが含まれていないか確認
   - すべてのパスを「"（ダブルクォート）」で囲む
   - 相対パスではなく絶対パスを使用してみる

3. **「FTPアップロードエラー」**
   - FTP接続情報が正しいか確認
   - リモートディレクトリのパーミッションを確認
   - ファイアウォールの設定を確認

4. **「設定ファイルが読み込めない」**
   - YAMLファイルの構文が正しいか確認
   - インデントがスペースで統一されているか確認
   - 設定値の型が正しいか確認（数値、文字列、真偽値など）

### 設定のバックアップ
- `config.yaml`の設定内容は必ずバックアップを取っておくことをお勧めします
- プロジェクトごとに異なる設定を使う場合は、設定ファイルの名前を変えて保存しておくと便利です
  ```
  config_character.yaml
  config_stage.yaml
  config_props.yaml
  など
  ```

## ライセンス
このツールはオープンソースソフトウェアとして提供されています。