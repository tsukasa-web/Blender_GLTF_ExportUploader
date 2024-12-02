# Blender GLTF/GLBエクスポーター

BlenderのGLTF/GLBエクスポート機能をコンソールから実行し、FTPアップロードまで自動化するツールです。

## 機能
- Blenderシーンのコンソールからのバッチエクスポート
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
   blender -b your_file.blend --python blender_export.py
   pause
   ```
3. `export.bat`として保存
4. ダブルクリックで実行可能に

#### Macでシェルスクリプトを作成
1. テキストエディタを開く
2. 以下の内容を入力
   ```bash
   #!/bin/bash
   blender -b your_file.blend --python blender_export.py
   read -p "Press [Enter] to exit..."
   ```
3. `export.sh`として保存
4. ターミナルで実行権限を付与
   ```bash
   chmod +x export.sh
   ```

### 5. トラブルシューティング

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

3. 「Python モジュールが見つかりません」
   - スクリプトとconfig.yamlが同じフォルダにあることを確認

### 6. 設定のバックアップ
- `config.yaml`の設定内容は必ずバックアップを取っておくことをお勧めします
- プロジェクトごとに異なる設定を使う場合は、設定ファイルの名前を変えて保存しておくと便利です
  ```
  config_character.yaml
  config_stage.yaml
  config_props.yaml
  など
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
| `export_loglevel`      | ログレベル                       | `-1`             |
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
### Data設定
#### Scene Graph
| パラメータ                          | 説明                                                 | デフォルト値 |
| ----------------------------------- | ---------------------------------------------------- | ------------ |
| `export_gn_mesh`                    | ジオメトリノードインスタンスをエクスポート（実験的） | `false`      |
| `export_gpu_instances`              | GPUインスタンス                                      | `false`      |
| `export_hierarchy_flatten_objs`     | オブジェクト階層を平坦化                             | `false`      |
| `export_hierarchy_full_collections` | 完全なコレクション階層をエクスポート                 | `false`      |

#### Mesh設定
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

#### 頂点カラー設定
| パラメータ                                    | 説明                                             | デフォルト値 |
| --------------------------------------------- | ------------------------------------------------ | ------------ |
| `export_vertex_color`                         | 頂点カラーの使用方法 (MATERIAL, ACTIVE, NONE)    | `MATERIAL`   |
| `export_all_vertex_colors`                    | すべての頂点カラーをエクスポート                 | `false`      |
| `export_active_vertex_color_when_no_material` | マテリアルがない場合アクティブな頂点カラーを使用 | `true`       |

#### マテリアル設定
| パラメータ                   | 説明                                      | デフォルト値 |
| ---------------------------- | ----------------------------------------- | ------------ |
| `export_materials`           | マテリアル (EXPORT, PLACEHOLDER, NONE)    | `EXPORT`     |
| `export_image_format`        | 画像フォーマット (AUTO, JPEG, WEBP, NONE) | `AUTO`       |
| `export_jpeg_quality`        | JPEG品質 (0-100)                          | `75`         |
| `export_image_quality`       | 画像品質 (0-100)                          | `75`         |
| `export_image_add_webp`      | WebPテクスチャを作成                      | `false`      |
| `export_image_webp_fallback` | WebPのフォールバックとしてPNGを作成       | `false`      |
| `export_keep_originals`      | オリジナルテクスチャを保持                | `false`      |

#### シェイプキー設定
| パラメータ             | 説明               | デフォルト値 |
| ---------------------- | ------------------ | ------------ |
| `export_morph`         | シェイプキー       | `true`       |
| `export_morph_normal`  | シェイプキーの法線 | `true`       |
| `export_morph_tangent` | シェイプキーの接線 | `false`      |

#### Optimize Shapekeys
| パラメータ                  | 説明                                 | デフォルト値 |
| --------------------------- | ------------------------------------ | ------------ |
| `export_try_sparse_sk`      | 可能な場合Sparseアクセサを使用       | `true`       |
| `export_try_omit_sparse_sk` | 空のデータの場合Sparseアクセサを省略 | `false`      |

#### Armature設定
| パラメータ                       | 説明                                     | デフォルト値 |
| -------------------------------- | ---------------------------------------- | ------------ |
| `export_rest_position_armature`  | レストポジションのアーマチュアを使用     | `true`       |
| `export_def_bones`               | 変形ボーンのみ                           | `false`      |
| `export_armature_object_remove`  | 可能な場合アーマチュアオブジェクトを削除 | `false`      |
| `export_hierarchy_flatten_bones` | ボーン階層を平坦化                       | `false`      |
#### Skinning設定
| パラメータ              | 説明                               | デフォルト値 |
| ----------------------- | ---------------------------------- | ------------ |
| `export_skins`          | スキニング                         | `true`       |
| `export_influence_nb`   | ボーンの影響数 (1以上)             | `4`          |
| `export_all_influences` | すべてのボーンの影響をエクスポート | `false`      |

#### Lighting設定
| パラメータ                            | 説明                                       | デフォルト値 |
| ------------------------------------- | ------------------------------------------ | ------------ |
| `export_import_convert_lighting_mode` | ライティングモード変換 (SPEC, COMPAT, RAW) | `SPEC`       |

#### Compression (Draco)
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
#### 基本設定
| パラメータ              | 説明                                                                         | デフォルト値 |
| ----------------------- | ---------------------------------------------------------------------------- | ------------ |
| `export_animations`     | アニメーション                                                               | `false`      |
| `export_animation_mode` | アニメーションモード (ACTIONS, ACTIVE_ACTIONS, BROADCAST, NLA_TRACKS, SCENE) | `ACTIONS`    |
| `export_bake_animation` | すべてのオブジェクトアニメーションをベイク                                   | `false`      |

#### Rest & Ranges
| パラメータ                  | 説明                                 | デフォルト値 |
| --------------------------- | ------------------------------------ | ------------ |
| `export_current_frame`      | 現在のフレームをレスト変換として使用 | `false`      |
| `export_frame_range`        | フレーム範囲を制限                   | `true`       |
| `export_anim_slide_to_zero` | アニメーションを0から開始            | `false`      |
| `export_negative_frame`     | 負のフレーム処理 (SLIDE, CROP)       | `SLIDE`      |

#### Armature Animation
| パラメータ                       | 説明                                         | デフォルト値 |
| -------------------------------- | -------------------------------------------- | ------------ |
| `export_anim_single_armature`    | すべてのアーマチュアアクションをエクスポート | `true`       |
| `export_anim_scene_split_object` | オブジェクトごとにアニメーションを分割       | `true`       |
| `export_reset_pose_bones`        | アクション間でポーズボーンをリセット         | `false`      |
| `export_leaf_bone`               | リーフボーンの追加                           | `false`      |
#### Shape Key Animation
| パラメータ                   | 説明                                 | デフォルト値 |
| ---------------------------- | ------------------------------------ | ------------ |
| `export_morph_animation`     | シェイプキーアニメーション           | `true`       |
| `export_morph_reset_sk_data` | アクション間でシェイプキーをリセット | `true`       |

#### Sampling Animation
| パラメータ                 | 説明                             | デフォルト値 |
| -------------------------- | -------------------------------- | ------------ |
| `export_force_sampling`    | 常にサンプリング                 | `true`       |
| `export_frame_step`        | フレームステップ (1-120)         | `1`          |
| `export_pointer_animation` | アニメーションポインタ（実験的） | `false`      |

#### Optimize Animation
| パラメータ                                     | 説明                                   | デフォルト値 |
| ---------------------------------------------- | -------------------------------------- | ------------ |
| `export_optimize_animation_size`               | アニメーションサイズを最適化           | `true`       |
| `export_optimize_animation_keep_anim_armature` | ボーンのチャンネルを強制保持           | `true`       |
| `export_optimize_animation_keep_anim_object`   | オブジェクトのチャンネルを強制保持     | `false`      |
| `export_optimize_disable_viewport`             | 他のオブジェクトのビューポートを無効化 | `false`      |

### アクションフィルター設定
| パラメータ                         | 説明                                      | デフォルト値 |
| ---------------------------------- | ----------------------------------------- | ------------ |
| `export_action_filter`             | アクションフィルター                      | `false`      |
| `export_extra_animations`          | 追加アニメーション                        | `false`      |
| `export_original_specular`         | オリジナルのPBRスペキュラーをエクスポート | `false`      |
| `export_convert_animation_pointer` | アニメーションポインタに変換              | `false`      |

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

### FTP設定
| パラメータ         | 説明                                 | デフォルト値 |
| ------------------ | ------------------------------------ | ------------ |
| `host`             | FTPサーバーのホスト名                | `""`         |
| `port`             | FTPポート番号                        | `21`         |
| `username`         | FTPユーザー名                        | `""`         |
| `password`         | FTPパスワード                        | `""`         |
| `remote_directory` | アップロード先のリモートディレクトリ | `"/"`        |

## 注意事項
- モディファイアを適用する設定（`export_apply`）を使用する場合、シェイプキーのエクスポートができなくなります
- マルチアーマチュアを含むエクスポートでは、`export_anim_single_armature`オプションはサポートされません
- WebPエクスポートを使用する場合、既にWebP形式のテクスチャに対しては何も行われません

## ライセンス
このツールはオープンソースソフトウェアとして提供されています。