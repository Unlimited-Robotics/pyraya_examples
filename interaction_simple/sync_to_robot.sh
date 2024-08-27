#!/bin/bash

current_dir=$(basename "$PWD")

rsync -av --delete --exclude='__pycache__/' --exclude='.git' ./ $1:/opt/raya_os/data/apps/${current_dir}
