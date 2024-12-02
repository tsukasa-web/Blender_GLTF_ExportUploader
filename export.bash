#!/bin/bash
cd "$(dirname "$0")"
blender -b your_file.blend --python blender_export.py
read -p "Press [Enter] to exit..."