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
        value_lower = str(value_str).lower()  # 確実に文字列に変換
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
        current_dict = self.data
        current_indent = 0
        path_stack = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('#') or not line.strip():
                    continue

                indent = len(line) - len(line.lstrip())
                line = line.strip()

                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    while indent < current_indent:
                        current_dict = self.data
                        for p in path_stack[:-1]:
                            current_dict = current_dict[p]
                        current_indent = indent
                        path_stack.pop()

                    if not value:
                        current_dict[key] = {}
                        current_dict = current_dict[key]
                        path_stack.append(key)
                        current_indent = indent
                    else:
                        current_dict[key] = self.parse_value(value)

        return self.data

class BlenderExporter:
    def __init__(self, config_path="config.yaml", output_filename=None):
        """初期化"""
        yaml_parser = SimpleYAMLParser()
        self.config = yaml_parser.parse_file(config_path)

        self.export_config = self.config.get('export_settings', {})
        self.output_dir = Path(self.config.get('output_directory', './output'))
        self.ftp_config = self.config.get('ftp_settings', {})

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
            'export_draco_generic_quantization': int(self.export_config.get('export_draco_generic_quantization', 12)),
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
                host=self.ftp_config['host'],
                port=self.ftp_config.get('port', 21)
            )
            ftp.login(
                user=self.ftp_config['username'],
                passwd=self.ftp_config['password']
            )

            remote_dir = self.ftp_config.get('remote_directory', '/')
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
    """メイン処理"""
    try:
        output_filename, config_path = get_args()

        print("エクスポート処理を開始します...")
        if output_filename:
            print(f"出力ファイル名: {output_filename}")

        exporter = BlenderExporter(config_path=config_path, output_filename=output_filename)
        exporter.export_gltf()
        # exporter.upload_to_ftp()
        print("すべての処理が完了しました")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()