#!/bin/bash

current_directory=$(pwd)
folder_name=$(basename "$current_directory")
rsync -av --delete --exclude='__pycache__/' ./ $1:/opt/raya_os/data/apps/${folder_name}