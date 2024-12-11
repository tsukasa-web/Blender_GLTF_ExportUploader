import bpy
import ftplib
import re
import sys
import os
from pathlib import Path

class SimpleYAMLParser:
    def __init__(self):
        self.data = {}

    def parse_value(self, value_str):
        """値を適切な型に変換"""
        if value_str is None or value_str == "":
            return ""  # Noneの代わりに空文字列を返す

        # 文字列を小文字に変換して比較
        value_lower = str(value_str).lower()
        if value_lower == 'true':
            return True
        if value_lower == 'false':
            return False

        try:
            if '.' in str(value_str):
                return float(value_str)
            if str(value_str).isdigit():
                return int(value_str)
        except (ValueError, AttributeError):
            pass

        # 文字列の処理
        if isinstance(value_str, str):
            value = value_str.strip()
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            if value.startswith("'") and value.endswith("'"):
                return value[1:-1]
            return value

        return value_str

    def parse_file(self, file_path):
        """YAMLファイルをパース"""
        print("\n=== YAMLパース処理開始 ===")
        print(f"YAMLファイルを読み込み: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"ファイル読み込みエラー: {str(e)}")
            raise

        self.data = {}
        current_dict = self.data
        section_stack = []
        last_indent = 0

        try:
            for line_num, line in enumerate(content.splitlines(), 1):
                if not line or line.strip().startswith('#'):
                    continue

                try:
                    indent = len(line) - len(line.lstrip())
                    line = line.lstrip()

                    # インデントの変更を処理
                    if indent < last_indent:
                        while section_stack and section_stack[-1][1] >= indent:
                            section_stack.pop()
                        if section_stack:
                            current_dict = section_stack[-1][0]
                        else:
                            current_dict = self.data

                    last_indent = indent

                    # セクションの開始
                    if ':' in line and not line.split(':', 1)[1].strip():
                        key = line.split(':', 1)[0].strip()

                        if section_stack:
                            parent_dict = section_stack[-1][0]
                        else:
                            parent_dict = self.data

                        if key == 'blend_files':
                            parent_dict[key] = []
                            current_dict = parent_dict[key]
                        else:
                            parent_dict[key] = {}
                            current_dict = parent_dict[key]

                        section_stack.append((current_dict, indent))
                        continue

                    # リストアイテムの処理
                    if line.startswith('-'):
                        if isinstance(current_dict, list):
                            current_dict.append({})
                            current_dict = current_dict[-1]
                        elif isinstance(current_dict, dict) and 'blend_files' in current_dict:
                            current_dict['blend_files'].append({})
                            current_dict = current_dict['blend_files'][-1]
                        line = line[1:].strip()

                    # キー・バリューペアの処理
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()

                        if isinstance(current_dict, dict):
                            current_dict[key] = self.parse_value(value)

                except Exception as e:
                    print(f"行 {line_num} の処理中にエラーが発生: {line}")
                    print(f"エラー詳細: {str(e)}")
                    raise

            # 必須セクションの確認と初期化
            if 'blend_files' not in self.data:
                self.data['blend_files'] = []
            if 'ftp_settings' not in self.data:
                self.data['ftp_settings'] = {}
            if 'export_settings' not in self.data:
                self.data['export_settings'] = {}

            print("\nパース結果:")
            print(f"blend_files: {self.data.get('blend_files', [])}")
            print(f"ftp_settings: {self.data.get('ftp_settings', {})}")
            return self.data

        except Exception as e:
            print(f"YAMLパースエラー: {str(e)}")
            raise

class BlenderExporter:
    def __init__(self, config_path="config.yaml", output_filename=None):
        """初期化"""
        yaml_parser = SimpleYAMLParser()
        self.config = yaml_parser.parse_file(config_path)

        self.execution_settings = self.config.get('execution_settings', {})
        self.export_config = self.config.get('export_settings', {})

        # シーン指定の処理を追加
        scene_name = self.export_config.get('scene_name', '')
        if scene_name:
            if scene_name in bpy.data.scenes:
                bpy.context.window.scene = bpy.data.scenes[scene_name]
                print(f"シーンを変更: {scene_name}")
            else:
                print(f"警告: 指定されたシーン '{scene_name}' が見つかりません")

        # FTP設定の初期化を修正
        ftp_settings = self.config.get('ftp_settings', {})
        self.ftp_settings = {
            'host': ftp_settings.get('host', ''),
            'port': ftp_settings.get('port', 21),
            'username': ftp_settings.get('username', ''),
            'password': ftp_settings.get('password', ''),
            'remote_directory': ftp_settings.get('remote_directory', '/')
        }

        print("\nFTP設定確認:")  # デバッグ用
        print(f"  host: {self.ftp_settings['host']}")
        print(f"  port: {self.ftp_settings['port']}")
        print(f"  username: {self.ftp_settings['username']}")
        print(f"  remote_directory: {self.ftp_settings['remote_directory']}")

        self.output_dir = Path(str(self.config.get('output_directory', './output')))
        self.blend_files = self.config.get('blend_files', [])

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

    def create_ftp_directory(self, ftp, path):
        """FTPサーバー上にディレクトリを再帰的に作成"""
        dirs = path.split('/')
        current = ''

        for d in dirs:
            if not d:  # パスが/で始まる場合や連続する/がある場合をスキップ
                continue
            current = current + '/' + d
            try:
                ftp.cwd(current)
            except ftplib.error_perm:
                try:
                    print(f"ディレクトリを作成: {current}")
                    ftp.mkd(current)
                    ftp.cwd(current)
                except ftplib.error_perm as e:
                    print(f"ディレクトリの作成に失敗: {current}")
                    print(f"エラー: {str(e)}")
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
            print(f"FTPサーバーに接続: {self.ftp_settings['host']}:{self.ftp_settings['port']}")

            ftp.connect(
                host=self.ftp_settings['host'],
                port=self.ftp_settings['port']
            )

            print(f"FTPログイン: {self.ftp_settings['username']}")
            ftp.login(
                user=self.ftp_settings['username'],
                passwd=self.ftp_settings['password']
            )

            remote_dir = self.ftp_settings['remote_directory']
            print(f"リモートディレクトリに移動: {remote_dir}")

            # リモートディレクトリの作成を試みる
            try:
                self.create_ftp_directory(ftp, remote_dir)
            except ftplib.error_perm as e:
                print(f"警告: ディレクトリの作成に失敗しました: {str(e)}")
                # ここでエラーを再度発生させるか処理を継続するかを選択できます
                raise

            # アップロード処理
            for file_path in self.output_dir.glob('*'):
                if file_path.is_file():
                    with open(file_path, 'rb') as file:
                        print(f'アップロード開始: {file_path.name}')
                        ftp.storbinary(f'STOR {file_path.name}', file)
                        print(f'アップロード完了: {file_path.name}')

            ftp.quit()
            print("FTPアップロード処理が正常に完了しました")

        except ftplib.all_errors as e:
            print(f"FTPアップロードエラー: {str(e)}")
            raise
        except Exception as e:
            print(f"FTPアップロードエラー: {str(e)}")
            raise

    def get_output_extension(self):
        """出力形式に基づいて適切な拡張子を返す"""
        export_format = self.export_config.get('export_format', 'GLTF_SEPARATE')
        if export_format == 'GLB':
            return '.glb'
        return '.gltf'

    def process_files(self):
        """設定ファイルで指定された全ファイルを処理"""
        print("\n=== ファイル処理開始 ===")
        if not self.blend_files:
            print("処理対象ファイルが指定されていません")
            return

        print(f"処理対象ファイル数: {len(self.blend_files)}")
        print("処理対象ファイル一覧:")
        for i, file_info in enumerate(self.blend_files, 1):
            print(f"  {i}: {file_info}")

        for index, file_info in enumerate(self.blend_files, 1):
            print(f"\n=== ファイル {index}/{len(self.blend_files)} の処理開始 ===")
            print(f"処理対象: {file_info}")

            original_filename = self.export_config.get('filename')
            blend_file = None

            try:
                if isinstance(file_info, dict):
                    file_path = file_info.get('file_path')
                    output_name = file_info.get('output_name')
                    remote_path = file_info.get('remote_path')

                    if not file_path:
                        print(f"エラー: file_pathが指定されていません（ファイル {index}）")
                        continue

                    # 拡張子の処理
                    if output_name:
                        base_name = os.path.splitext(output_name)[0]
                        output_name = base_name + self.get_output_extension()

                    blend_file = Path(file_path)
                    if not blend_file.exists():
                        print(f"エラー: ファイルが存在しません: {blend_file}")
                        continue

                    print(f"ファイル読み込み開始: {blend_file}")
                    bpy.ops.wm.open_mainfile(filepath=str(blend_file))
                    print(f"ファイル読み込み完了: {blend_file}")

                    if output_name:
                        self.export_config['filename'] = output_name
                        print(f"出力ファイル名を設定: {output_name}")

                    exported_file = self.export_gltf()
                    print(f"エクスポート完了: {exported_file}")

                    original_remote_dir = None
                    if remote_path and 'remote_directory' in self.ftp_settings:
                        original_remote_dir = self.ftp_settings['remote_directory']
                        self.ftp_settings['remote_directory'] = remote_path
                        print(f"リモートディレクトリを変更: {remote_path}")

                    try:
                        self.upload_to_ftp()
                        print(f"アップロード完了: {blend_file.name}")
                    finally:
                        if original_remote_dir is not None:
                            self.ftp_settings['remote_directory'] = original_remote_dir
                        if original_filename is not None:
                            self.export_config['filename'] = original_filename

            except Exception as e:
                file_name = blend_file.name if blend_file else "不明なファイル"
                print(f"エラー発生 ({file_name}): {str(e)}")
                print("スタックトレース:")
                import traceback
                traceback.print_exc()

            finally:
                if original_filename is not None:
                    self.export_config['filename'] = original_filename
                print(f"=== ファイル {index}/{len(self.blend_files)} の処理完了 ===\n")

        print("全ファイルの処理が完了しました")

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

        # プラットフォーム固有の終了処理
        import platform
        if platform.system() == 'Darwin':  # Mac
            if auto_close:
                try:
                    with open(".close_after_complete", "w") as f:
                        f.write("1")
                except Exception as e:
                    print(f"一時ファイルの作成に失敗しました: {str(e)}")
        else:  # Windows その他
            if auto_close:
                try:
                    with open(".close_after_complete", "w") as f:
                        f.write("1")
                except Exception as e:
                    print(f"一時ファイルの作成に失敗しました: {str(e)}")
                input("Enterキーを押して終了してください...")
            else:
                input("Enterキーを押して終了してください...")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        if platform.system() != 'Darwin':  # Mac以外
            input("Enterキーを押して終了してください...")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()