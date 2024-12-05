import bpy
import ftplib
import re
import sys
from pathlib import Path

class SimpleYAMLParser:
    def __init__(self):
        self.data = {}

    def parse_value(self, value_str):
        """値を適切な型に変換"""
        if value_str is None or value_str == "":
            return value_str

        # 文字列を小文字に変換して比較
        value_lower = str(value_str).lower()
        if value_lower == 'true':
            return True
        if value_lower == 'false':
            return False

        # 数値への変換を試みる
        try:
            if '.' in str(value_str):
                return float(value_str)
            if str(value_str).isdigit():
                return int(value_str)
        except (ValueError, AttributeError):
            pass

        # 文字列の処理
        if isinstance(value_str, str):
            # クォートの除去
            if value_str.startswith('"') and value_str.endswith('"'):
                return value_str[1:-1]
            if value_str.startswith("'") and value_str.endswith("'"):
                return value_str[1:-1]
            return value_str.strip()

        return value_str

    def parse_file(self, file_path):
        """YAMLファイルをパース"""
        print("\n=== YAMLパース処理開始 ===")
        self.data = {}
        indent_stack = [(0, self.data)]
        current_dict = self.data
        current_list_item = None
        last_indent = 0

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # コメントと空行をスキップ
                    line = line.rstrip()
                    if not line or line.strip().startswith('#'):
                        continue

                    # インデントを計算
                    indent = len(line) - len(line.lstrip())
                    line = line.lstrip()

                    # リストアイテムの処理
                    if line.startswith('-'):
                        line = line[1:].strip()
                        parent_dict = indent_stack[-1][1]
                        last_key = list(parent_dict.keys())[-1] if parent_dict else None

                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()

                            # 新しいリストアイテムを作成
                            current_list_item = {}
                            if value:
                                current_list_item[key] = self.parse_value(value)

                            # 親リストに追加
                            if last_key and isinstance(parent_dict[last_key], list):
                                parent_dict[last_key].append(current_list_item)

                            # インデントスタックを更新
                            indent_stack.append((indent, current_list_item))

                    # キー・バリューペアの処理
                    elif ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()

                        # インデントに基づいて適切な親を選択
                        while len(indent_stack) > 1 and indent <= indent_stack[-1][0]:
                            indent_stack.pop()
                            current_list_item = None

                        current_dict = indent_stack[-1][1]

                        # 値の処理
                        if not value:
                            # リストまたは新しいセクションの開始
                            if key == 'blend_files':
                                current_dict[key] = []
                            else:
                                new_dict = {}
                                current_dict[key] = new_dict
                                current_dict = new_dict
                                indent_stack.append((indent, current_dict))
                        else:
                            # リストアイテムに属する値
                            if current_list_item is not None and indent > last_indent:
                                current_list_item[key] = self.parse_value(value)
                            else:
                                current_dict[key] = self.parse_value(value)

                    last_indent = indent

                except Exception as e:
                    print(f"エラー (行 {line_num}): {str(e)}")
                    print(f"現在の状態:")
                    print(f"  行: {line}")
                    print(f"  インデント: {indent}")
                    print(f"  current_dict: {current_dict}")
                    print(f"  current_list_item: {current_list_item}")
                    print(f"  indent_stack: {indent_stack}")
                    raise

            return self.data

class BlenderExporter:
    def __init__(self, config_path="config.yaml", output_filename=None):
        """初期化"""
        yaml_parser = SimpleYAMLParser()
        self.config = yaml_parser.parse_file(config_path)

        self.execution_settings = self.config.get('execution_settings', {})
        self.export_config = self.config.get('export_settings', {})

        # FTP設定の初期化
        ftp_settings = self.config.get('ftp_settings', {})
        self.ftp_settings = {
            'host': ftp_settings.get('host', ''),
            'port': ftp_settings.get('port', 21),
            'username': ftp_settings.get('username', ''),
            'password': ftp_settings.get('password', ''),
            'remote_directory': ftp_settings.get('remote_directory', '/')
        }

        self.output_dir = Path(str(self.config.get('output_directory', './output')))
        self.blend_files = self.config.get('blend_files', [])

        # print("\n=== 設定読み込み結果 ===")
        # print(f"blend_files: {self.blend_files}")
        # print(f"export_config: {self.export_config}")
        # print(f"ftp_settings: {self.ftp_settings}")  # FTP設定の確認を追加

        if output_filename:
            self.export_config['filename'] = output_filename

    def convert_bool(self, value):
        """ブール値への変換"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 't', 'y', 'yes')
        if isinstance(value, (int, float)):
            return bool(value)
        return False

    def export_gltf(self):
        """GLTFエクスポート処理"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nエクスポート設定確認:")
        print(f"  - 設定されているfilename: {self.export_config.get('filename', 'Not Set')}")

        # ブール値パラメータのリスト
        boolean_params = [
            'check_existing',
            'export_use_gltfpack',
            'export_gltfpack_tc',
            'export_gltfpack_sa',
            'export_gltfpack_slb',
            'export_gltfpack_noq',
            'export_image_add_webp',
            'export_image_webp_fallback',
            'export_keep_originals',
            'export_texcoords',
            'export_normals',
            'export_gn_mesh',
            'export_tangents',
            'export_all_vertex_colors',
            'export_active_vertex_color_when_no_material',
            'export_attributes',
            'use_mesh_edges',
            'use_mesh_vertices',
            'export_cameras',
            'use_selection',
            'use_visible',
            'use_renderable',
            'use_active_collection',
            'use_active_collection_with_nested',
            'use_active_scene',
            'at_collection_center',
            'export_extras',
            'export_yup',
            'export_apply',
            'export_shared_accessors',
            'export_animations',
            'export_frame_range',
            'export_force_sampling',
            'export_pointer_animation',
            'export_anim_single_armature',
            'export_reset_pose_bones',
            'export_current_frame',
            'export_rest_position_armature',
            'export_morph',
            'export_morph_normal',
            'export_morph_tangent',
            'export_morph_animation',
            'export_morph_reset_sk_data',
            'export_try_sparse_sk',
            'export_try_omit_sparse_sk',
            'export_def_bones',
            'export_hierarchy_flatten_bones',
            'export_hierarchy_flatten_objs',
            'export_armature_object_remove',
            'export_leaf_bone',
            'export_optimize_animation_size',
            'export_optimize_animation_keep_anim_armature',
            'export_optimize_animation_keep_anim_object',
            'export_optimize_disable_viewport',
            'export_anim_slide_to_zero',
            'export_bake_animation',
            'export_skins',
            'export_all_influences',
            'export_lights',
            'export_gpu_instances',
            'will_save_settings',
            'export_hierarchy_full_collections'
        ]

        # エクスポート引数の準備
        export_args = {
            # 文字列パラメータ
            'filepath': str(self.output_dir / self.export_config.get('filename', 'model.gltf')),
            'export_format': self.export_config.get('export_format', 'GLTF_SEPARATE'),
            'export_copyright': self.export_config.get('export_copyright', ''),
            'gltf_export_id': self.export_config.get('gltf_export_id', ''),
            'collection': self.export_config.get('collection', ''),
            'export_image_format': self.export_config.get('export_image_format', 'AUTO'),
            'export_vertex_color': self.export_config.get('export_vertex_color', 'MATERIAL'),
            'export_materials': self.export_config.get('export_materials', 'EXPORT'),
            'export_animation_mode': self.export_config.get('export_animation_mode', 'ACTIONS'),
            'export_negative_frame': self.export_config.get('export_negative_frame', 'SLIDE'),
            'export_import_convert_lighting_mode': self.export_config.get('export_import_convert_lighting_mode', 'COMPAT'),
            'export_gltfpack_vpi': self.export_config.get('export_gltfpack_vpi', 'Integer'),
            'filter_glob': self.export_config.get('filter_glob', '*.glb;*.gltf'),

            # 数値パラメータ
            'export_gltfpack_tq': int(self.export_config.get('export_gltfpack_tq', 8)),
            'export_gltfpack_si': float(self.export_config.get('export_gltfpack_si', 1.0)),
            'export_gltfpack_vp': int(self.export_config.get('export_gltfpack_vp', 14)),
            'export_gltfpack_vt': int(self.export_config.get('export_gltfpack_vt', 12)),
            'export_gltfpack_vn': int(self.export_config.get('export_gltfpack_vn', 8)),
            'export_gltfpack_vc': int(self.export_config.get('export_gltfpack_vc', 8)),
            'export_jpeg_quality': int(self.export_config.get('export_jpeg_quality', 75)),
            'export_image_quality': int(self.export_config.get('export_image_quality', 75)),
            'export_frame_step': int(self.export_config.get('export_frame_step', 1)),
            'export_influence_nb': int(self.export_config.get('export_influence_nb', 4))
        }

        # ブール値パラメータの追加
        for param in boolean_params:
            if param in self.export_config:
                export_args[param] = self.convert_bool(self.export_config[param])

        print(f"GLTFエクスポートを開始します: {export_args['filepath']}")

        try:
            bpy.ops.export_scene.gltf(**export_args)
            print(f"GLTFエクスポートが完了しました: {export_args['filepath']}")
            return export_args['filepath']
        except Exception as e:
            print(f"エクスポートエラー: {str(e)}")
            raise

    def upload_to_ftp(self):
        """FTPアップロード処理"""
        try:
            print("FTPアップロードを開始します...")

            # FTP設定の検証
            if not self.ftp_settings.get('host'):
                raise ValueError("FTPホストが設定されていません")
            if not self.ftp_settings.get('username'):
                raise ValueError("FTPユーザー名が設定されていません")
            if not self.ftp_settings.get('password'):
                raise ValueError("FTPパスワードが設定されていません")

            ftp = ftplib.FTP()
            ftp.connect(
                host=self.ftp_settings['host'],
                port=self.ftp_settings.get('port', 21)
            )
            ftp.login(
                user=self.ftp_settings['username'],
                passwd=self.ftp_settings['password']
            )

            remote_dir = self.ftp_settings.get('remote_directory', '/')
            print(f"リモートディレクトリに移動: {remote_dir}")
            ftp.cwd(remote_dir)

            for file_path in self.output_dir.glob('*'):
                if file_path.is_file():
                    with open(file_path, 'rb') as file:
                        print(f'アップロード開始: {file_path.name}')
                        ftp.storbinary(f'STOR {file_path.name}', file)
                        print(f'アップロード完了: {file_path.name}')

            ftp.quit()
            print("FTPアップロード処理が正常に完了しました")

        except Exception as e:
            print(f"FTPアップロードエラー: {str(e)}")
            raise

    def process_files(self):
        """設定ファイルで指定された全ファイルを処理"""
        print("\n=== ファイル処理開始 ===")
        if not self.blend_files:
            print("処理対象ファイルが指定されていません")
            return

        print(f"処理対象ファイル数: {len(self.blend_files)}")

        for file_info in self.blend_files:
            print("\n=== ファイル処理デバッグ情報 ===")
            print("file_info の型:", type(file_info))
            print("file_info の内容:", file_info)

            # 現在のファイル名設定を保存
            original_filename = self.export_config.get('filename')

            blend_file = None
            try:
                if isinstance(file_info, dict):
                    file_path = file_info.get('file_path')
                    output_name = file_info.get('output_name')
                    remote_path = file_info.get('remote_path')

                    print(f"出力ファイル名設定:")
                    print(f"  - 指定された出力ファイル名: {output_name}")
                    print(f"  - 設定前のfilename: {self.export_config.get('filename', 'Not Set')}")

                    if not file_path:
                        print("エラー: file_pathが指定されていないファイルがあります")
                        continue

                    blend_file = Path(file_path)
                    print(f"\n処理開始: {blend_file.name}")

                    # Blenderファイルを開く
                    bpy.ops.wm.open_mainfile(filepath=str(blend_file))

                    # 出力ファイル名を設定（個別設定が優先）
                    if output_name:
                        self.export_config['filename'] = output_name
                        print(f"  - 設定後のfilename: {self.export_config['filename']}")

                    # エクスポートとアップロード処理
                    exported_file = self.export_gltf()
                    print(f"  - エクスポートされたファイル: {exported_file}")

                    # アップロード処理（変更なし）
                    original_remote_dir = None
                    if remote_path and 'remote_directory' in self.ftp_settings:
                        original_remote_dir = self.ftp_settings['remote_directory']
                        self.ftp_settings['remote_directory'] = remote_path

                    try:
                        self.upload_to_ftp()
                    finally:
                        # 設定を元に戻す
                        if original_remote_dir is not None:
                            self.ftp_settings['remote_directory'] = original_remote_dir
                        if original_filename is not None:
                            self.export_config['filename'] = original_filename

            except Exception as e:
                file_name = blend_file.name if blend_file else "不明なファイル"
                print(f"エラー ({file_name}): {str(e)}")

            finally:
                # 必ず元の設定に戻す
                if original_filename is not None:
                    self.export_config['filename'] = original_filename

def get_args():
    """コマンドライン引数を解析"""
    argv = sys.argv
    argv = argv[argv.index("--python") + 2:]

    output_filename = None
    config_path = "config.yaml"

    i = 0
    while i < len(argv):
        if argv[i] == "--output":
            if i + 1 < len(argv):
                output_filename = argv[i + 1]
                i += 2
            else:
                print("エラー: --output オプションには値が必要です")
                sys.exit(1)
        elif argv[i] == "--config":
            if i + 1 < len(argv):
                config_path = argv[i + 1]
                i += 2
            else:
                print("エラー: --config オプションには値が必要です")
                sys.exit(1)
        else:
            i += 1

    return output_filename, config_path

def main():
    try:
        output_filename, config_path = get_args()
        print("エクスポート処理を開始します...")

        exporter = BlenderExporter(config_path=config_path, output_filename=output_filename)
        auto_close = exporter.execution_settings.get('close_after_complete', False)

        # 複数ファイル処理の実行
        if exporter.blend_files:
            exporter.process_files()
        else:
            # 従来の単一ファイル処理
            exporter.export_gltf()
            exporter.upload_to_ftp()

        print("すべての処理が完了しました")

        # 自動終了が無効の場合は入力待ち
        if not auto_close:
            input("Enterキーを押して終了してください...")

        # 正常終了時の処理
        if auto_close:
            import sys
            sys.exit(0)  # 正常終了コード

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        input("Enterキーを押して終了してください...")  # エラー時は必ず待機
        sys.exit(1)  # エラー終了コード

    sys.exit(0)  # 正常終了

if __name__ == "__main__":
    main()