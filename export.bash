#!/bin/bash
cd "$(dirname "$0")"
blender -b --python blender_export.py -- --config config.yaml
if [ $? -ne 0 ]; then
    read -p "Press [Enter] to exit..."
fi