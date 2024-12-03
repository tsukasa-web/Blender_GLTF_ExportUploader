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
        if not value_str:
            return None

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
            return int(value_str)
        except ValueError:
            pass

        # クォートの除去
        if isinstance(value_str, str):
            if value_str.startswith('"') and value_str.endswith('"'):
                return value_str[1:-1]
            if value_str.startswith("'") and value_str.endswith("'"):
                return value_str[1:-1]

        return value_str

    def parse_file(self, file_path):
        """YAMLファイルをパース"""
        self.data = {}
        current_dict = None
        current_indent = 0
        path_stack = []

        print("\n=== YAMLパース処理開始 ===")
        # print(f"ファイル: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                line = lines[i].rstrip()
                if line.strip().startswith('#') or not line.strip():
                    i += 1
                    continue

                indent = len(line) - len(line.lstrip())
                line = line.strip()
                # print(f"\n処理行: {line}")
                # print(f"インデント: {indent}")

                if line.startswith('-'):  # リストアイテムの処理開始
                    # print("リストアイテムの処理開始")
                    if not isinstance(self.data.get(path_stack[-1]), list):
                        self.data[path_stack[-1]] = []
                        # print(f"新規リスト作成: {path_stack[-1]}")

                    item_dict = {}

                    # リストアイテムの最初の要素を処理
                    if ':' in line[1:]:
                        key, value = line[1:].split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if '#' in value:
                            value = value.split('#')[0].strip()
                        item_dict[key] = self.parse_value(value)
                        # print(f"リストアイテムの最初の要素を追加: {key} = {value}")

                    self.data[path_stack[-1]].append(item_dict)
                    current_dict = item_dict
                    # print(f"現在のリスト状態: {self.data[path_stack[-1]]}")

                    i += 1
                    while i < len(lines):
                        next_line = lines[i].rstrip()
                        next_indent = len(next_line) - len(next_line.lstrip())
                        # print(f"サブアイテム処理: {next_line}")
                        # print(f"サブインデント: {next_indent}")

                        if not next_line.strip() or next_line.strip().startswith('#'):
                            i += 1
                            continue

                        if next_indent <= indent:
                            break

                        next_line = next_line.lstrip()
                        if ':' in next_line:
                            key, value = next_line.split(':', 1)
                            key = key.strip()
                            value = value.strip()

                            if '#' in value:
                                value = value.split('#')[0].strip()

                            current_dict[key] = self.parse_value(value)
                            # print(f"アイテム追加: {key} = {value}")
                        i += 1
                    continue

                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    if indent == 0:  # トップレベルの項目
                        current_dict = {}
                        self.data[key] = current_dict
                        path_stack = [key]
                        current_indent = 0
                    else:
                        if not value:  # サブディクショナリの開始
                            new_dict = {}
                            current_dict[key] = new_dict
                            current_dict = new_dict
                            path_stack.append(key)
                            current_indent = indent
                        else:  # 値の設定
                            # コメントを除去
                            if '#' in value:
                                value = value.split('#')[0].strip()
                            current_dict[key] = self.parse_value(value)

                i += 1

        # print("\n=== パース結果 ===")
        # print(self.data)
        return self.data

class BlenderExporter:
    def __init__(self, config_path="config.yaml", output_filename=None):
        """初期化"""
        yaml_parser = SimpleYAMLParser()
        self.config = yaml_parser.parse_file(config_path)

        self.export_config = self.config.get('export_settings', {})
        self.ftp_settings = self.config.get('ftp_settings', {})
        self.output_dir = Path(str(self.config.get('output_directory', './output')))
        self.blend_files = self.config.get('blend_files', [])

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
            'export_draco_mesh_compression_enable',
            'export_tangents',
            'export_unused_images',
            'export_unused_textures',
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
            'export_anim_scene_split_object',
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
            'export_action_filter',
            'export_original_specular',
            'will_save_settings',
            'export_hierarchy_full_collections',
            'export_extra_animations',
            'export_convert_animation_pointer'
        ]

        # エクスポート引数の準備
        export_args = {
            # 文字列パラメータ
            'filepath': str(self.output_dir / self.export_config.get('filename', 'model.gltf')),
            'export_format': self.export_config.get('export_format', 'GLTF_SEPARATE'),
            'export_copyright': self.export_config.get('export_copyright', ''),
            'gltf_export_id': self.export_config.get('export_copyright', ''),
            'collection': self.export_config.get('collection', ''),
            'export_image_format': self.export_config.get('export_image_format', 'AUTO'),
            'export_texture_dir': self.export_config.get('export_texture_dir', ''),
            'export_vertex_color': self.export_config.get('export_vertex_color', 'MATERIAL'),
            'export_materials': self.export_config.get('export_materials', 'EXPORT'),
            'export_animation_mode': self.export_config.get('export_animation_mode', 'ACTIONS'),
            'export_negative_frame': self.export_config.get('export_negative_frame', 'SLIDE'),
            'export_nla_strips_merged_animation_name': self.export_config.get('export_nla_strips_merged_animation_name', 'Animation'),
            'export_import_convert_lighting_mode': self.export_config.get('export_import_convert_lighting_mode', 'SPEC'),
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
            'export_influence_nb': int(self.export_config.get('export_influence_nb', 4)),
            'export_draco_mesh_compression_level': int(self.export_config.get('export_draco_mesh_compression_level', 6)),
            'export_draco_position_quantization': int(self.export_config.get('export_draco_position_quantization', 14)),
            'export_draco_normal_quantization': int(self.export_config.get('export_draco_normal_quantization', 10)),
            'export_draco_texcoord_quantization': int(self.export_config.get('export_draco_texcoord_quantization', 12)),
            'export_draco_color_quantization': int(self.export_config.get('export_draco_color_quantization', 10)),
            'export_draco_generic_quantization': int(self.export_config.get('export_draco_generic_quantization', 12))
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
            ftp.cwd(remote_dir)

            for file_path in self.output_dir.glob('*'):
                if file_path.is_file():
                    with open(file_path, 'rb') as file:
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
        # print(f"blend_files の型: {type(self.blend_files)}")
        print(f"blend_files の内容: {self.blend_files}")

        for file_info in self.blend_files:
            print(f"\n--- .blendファイル情報処理開始 ---")
            # print(f"file_info の型: {type(file_info)}")
            # print(f"file_info の内容: {file_info}")
            print(f"file_info のキー: {file_info.keys() if isinstance(file_info, dict) else 'Not a dict'}")

            blend_file = None
            try:
                # file_pathの取得を確認
                if isinstance(file_info, dict):
                    file_path = file_info.get('file_path')
                    print(f"取得したfile_path: {file_path}")
                else:
                    print(f"file_infoが辞書ではありません: {type(file_info)}")
                    continue

                if not file_path:
                    print("エラー: file_pathが指定されていないファイルがあります")
                    continue

                blend_file = Path(file_path)
                output_name = file_info.get('output_name')
                remote_path = file_info.get('remote_path')

                print(f"\n処理開始: {blend_file.name}")

                # Blenderファイルを開く
                bpy.ops.wm.open_mainfile(filepath=str(blend_file))

                # 出力ファイル名を一時的に変更
                original_filename = self.export_config.get('filename')
                if output_name:
                    self.export_config['filename'] = output_name

                # エクスポート実行
                self.export_gltf()

                # 出力ファイル名を元に戻す
                if output_name:
                    self.export_config['filename'] = original_filename

                # リモートパスの一時変更とアップロード
                original_remote_dir = self.ftp_settings.get('remote_directory')
                if remote_path:
                    self.ftp_settings['remote_directory'] = remote_path

                self.upload_to_ftp()

                # リモートパスを元に戻す
                if remote_path:
                    self.ftp_settings['remote_directory'] = original_remote_dir

                print(f"処理完了: {blend_file.name}")

            except Exception as e:
                file_name = blend_file.name if blend_file else "不明なファイル"
                print(f"エラー ({file_name}): {str(e)}")

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

        # 複数ファイル処理の実行
        if exporter.blend_files:
            exporter.process_files()
        else:
            # 従来の単一ファイル処理
            exporter.export_gltf()
            exporter.upload_to_ftp()

        print("すべての処理が完了しました")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()