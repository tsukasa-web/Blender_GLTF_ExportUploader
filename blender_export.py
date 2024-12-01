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

        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False

        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

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
            self.export_config['filepath'] = str(self.output_dir / output_filename)
        else:
            self.export_config['filepath'] = str(self.output_dir / self.export_config.get('filename', 'model.gltf'))

    def export_gltf(self):
        """GLTFエクスポート処理"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"GLTFエクスポートを開始します: {self.export_config['filepath']}")

        # Blenderのエクスポート処理
        export_args = {
            # 基本設定
            'filepath': self.export_config['filepath'],
            'check_existing': self.export_config.get('check_existing', True),
            'export_format': self.export_config.get('export_format', ''),

            # gltfpack設定
            'export_use_gltfpack': self.export_config.get('export_use_gltfpack', False),
            'export_gltfpack_tc': self.export_config.get('export_gltfpack_tc', True),
            'export_gltfpack_tq': self.export_config.get('export_gltfpack_tq', 8),
            'export_gltfpack_si': self.export_config.get('export_gltfpack_si', 1.0),
            'export_gltfpack_sa': self.export_config.get('export_gltfpack_sa', False),
            'export_gltfpack_slb': self.export_config.get('export_gltfpack_slb', False),
            'export_gltfpack_vp': self.export_config.get('export_gltfpack_vp', 14),
            'export_gltfpack_vt': self.export_config.get('export_gltfpack_vt', 12),
            'export_gltfpack_vn': self.export_config.get('export_gltfpack_vn', 8),
            'export_gltfpack_vc': self.export_config.get('export_gltfpack_vc', 8),
            'export_gltfpack_vpi': self.export_config.get('export_gltfpack_vpi', 'Integer'),
            'export_gltfpack_noq': self.export_config.get('export_gltfpack_noq', True),

            # 一般設定
            'export_copyright': self.export_config.get('export_copyright', ''),
            'export_import_convert_lighting_mode': self.export_config.get('export_import_convert_lighting_mode', 'SPEC'),
            'gltf_export_id': self.export_config.get('gltf_export_id', ''),
            'export_extras': self.export_config.get('export_extras', False),
            'export_yup': self.export_config.get('export_yup', True),

            # イメージ設定
            'export_image_format': self.export_config.get('export_image_format', 'AUTO'),
            'export_image_add_webp': self.export_config.get('export_image_add_webp', False),
            'export_image_webp_fallback': self.export_config.get('export_image_webp_fallback', False),
            'export_texture_dir': self.export_config.get('export_texture_dir', ''),
            'export_jpeg_quality': self.export_config.get('export_jpeg_quality', 75),
            'export_image_quality': self.export_config.get('export_image_quality', 75),
            'export_keep_originals': self.export_config.get('export_keep_originals', False),
            'export_unused_images': self.export_config.get('export_unused_images', False),
            'export_unused_textures': self.export_config.get('export_unused_textures', False),

            # メッシュ設定
            'export_texcoords': self.export_config.get('export_texcoords', True),
            'export_normals': self.export_config.get('export_normals', True),
            'export_tangents': self.export_config.get('export_tangents', False),
            'export_materials': self.export_config.get('export_materials', 'EXPORT'),
            'use_mesh_edges': self.export_config.get('use_mesh_edges', False),
            'use_mesh_vertices': self.export_config.get('use_mesh_vertices', False),
            'export_colors': self.export_config.get('export_colors', True),
            'export_attributes': self.export_config.get('export_attributes', False),
            'export_apply': self.export_config.get('export_apply', False),
            'export_shared_accessors': self.export_config.get('export_shared_accessors', False),

            # ジオメトリノード設定
            'export_gn_mesh': self.export_config.get('export_gn_mesh', False),

            # 頂点カラー設定
            'export_vertex_color': self.export_config.get('export_vertex_color', 'MATERIAL'),
            'export_all_vertex_colors': self.export_config.get('export_all_vertex_colors', False),
            'export_active_vertex_color_when_no_material': self.export_config.get('export_active_vertex_color_when_no_material', True),

            # オブジェクト設定
            'export_cameras': self.export_config.get('export_cameras', False),
            'use_selection': self.export_config.get('use_selection', False),
            'use_visible': self.export_config.get('use_visible', False),
            'use_renderable': self.export_config.get('use_renderable', False),
            'use_active_collection': self.export_config.get('use_active_collection', False),
            'use_active_collection_with_nested': self.export_config.get('use_active_collection_with_nested', True),
            'use_active_scene': self.export_config.get('use_active_scene', True),
            'collection': self.export_config.get('collection', ''),
            'at_collection_center': self.export_config.get('at_collection_center', False),

            # 階層設定
            'export_hierarchy_full_collections': self.export_config.get('export_hierarchy_full_collections', False),
            'export_hierarchy_flatten_bones': self.export_config.get('export_hierarchy_flatten_bones', False),
            'export_hierarchy_flatten_objs': self.export_config.get('export_hierarchy_flatten_objs', False),
            'export_armature_object_remove': self.export_config.get('export_armature_object_remove', False),

            # アニメーション設定
            'export_animations': self.export_config.get('export_animations', False),
            'export_frame_range': self.export_config.get('export_frame_range', True),
            'export_frame_step': self.export_config.get('export_frame_step', 1),
            'export_force_sampling': self.export_config.get('export_force_sampling', True),
            'export_animation_mode': self.export_config.get('export_animation_mode', 'ACTIONS'),
            'export_nla_strips_merged_animation_name': self.export_config.get('export_nla_strips_merged_animation_name', 'Animation'),
            'export_nla_strips': self.export_config.get('export_nla_strips', True),

            # アニメーション詳細設定
            'export_pointer_animation': self.export_config.get('export_pointer_animation', False),
            'export_negative_frame': self.export_config.get('export_negative_frame', 'SLIDE'),
            'export_anim_slide_to_zero': self.export_config.get('export_anim_slide_to_zero', False),
            'export_bake_animation': self.export_config.get('export_bake_animation', False),
            'export_anim_single_armature': self.export_config.get('export_anim_single_armature', True),
            'export_reset_pose_bones': self.export_config.get('export_reset_pose_bones', False),
            'export_current_frame': self.export_config.get('export_current_frame', False),
            'export_rest_position_armature': self.export_config.get('export_rest_position_armature', True),
            'export_anim_scene_split_object': self.export_config.get('export_anim_scene_split_object', True),

            # 最適化設定
            'export_optimize_animation_size': self.export_config.get('export_optimize_animation_size', True),
            'export_optimize_animation_keep_anim_armature': self.export_config.get('export_optimize_animation_keep_anim_armature', True),
            'export_optimize_animation_keep_anim_object': self.export_config.get('export_optimize_animation_keep_anim_object', False),
            'export_optimize_disable_viewport': self.export_config.get('export_optimize_disable_viewport', False),

            # ボーン/スキン設定
            'export_skins': self.export_config.get('export_skins', True),
            'export_influence_nb': self.export_config.get('export_influence_nb', 4),
            'export_all_influences': self.export_config.get('export_all_influences', False),
            'export_def_bones': self.export_config.get('export_def_bones', False),
            'export_leaf_bone': self.export_config.get('export_leaf_bone', False),

            # Draco圧縮設定
            'export_draco_mesh_compression_enable': self.export_config.get('export_draco_mesh_compression_enable', False),
            'export_draco_mesh_compression_level': self.export_config.get('export_draco_mesh_compression_level', 6),
            'export_draco_position_quantization': self.export_config.get('export_draco_position_quantization', 14),
            'export_draco_normal_quantization': self.export_config.get('export_draco_normal_quantization', 10),
            'export_draco_texcoord_quantization': self.export_config.get('export_draco_texcoord_quantization', 12),
            'export_draco_color_quantization': self.export_config.get('export_draco_color_quantization', 10),
            'export_draco_generic_quantization': self.export_config.get('export_draco_generic_quantization', 12),

            # シェイプキー設定
            'export_morph': self.export_config.get('export_morph', True),
            'export_morph_normal': self.export_config.get('export_morph_normal', True),
            'export_morph_tangent': self.export_config.get('export_morph_tangent', False),
            'export_morph_animation': self.export_config.get('export_morph_animation', True),
            'export_morph_reset_sk_data': self.export_config.get('export_morph_reset_sk_data', True),
            'export_try_sparse_sk': self.export_config.get('export_try_sparse_sk', True),
            'export_try_omit_sparse_sk': self.export_config.get('export_try_omit_sparse_sk', False),

            # GPU/拡張機能設定
            'export_gpu_instances': self.export_config.get('export_gpu_instances', False),
            'export_action_filter': self.export_config.get('export_action_filter', False),
            'export_extra_animations': self.export_config.get('export_extra_animations', False),
            'export_lights': self.export_config.get('export_lights', False),
            'export_original_specular': self.export_config.get('export_original_specular', False),
            'export_convert_animation_pointer': self.export_config.get('export_convert_animation_pointer', False),

            # その他
            'export_loglevel': self.export_config.get('export_loglevel', -1),
            'will_save_settings': self.export_config.get('will_save_settings', False),
            'filter_glob': self.export_config.get('filter_glob', '*.glb;*.gltf')
        }

        bpy.ops.export_scene.gltf(**export_args)
        print(f"GLTFエクスポートが完了しました: {self.export_config['filepath']}")
        return self.export_config['filepath']

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
        exporter.upload_to_ftp()
        print("すべての処理が完了しました")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()