#!/bin/bash
cd "$(dirname "$0")"
blender -b --python blender_export.py -- --config config.yaml
read -p "Press [Enter] to exit..."