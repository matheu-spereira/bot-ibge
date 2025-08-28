#!/bin/bash

# Caminho base do projeto
BASE_DIR="$(dirname "$(realpath "$0")")"

# Ativa o ambiente virtual dentro do projeto
source "$BASE_DIR/venv/bin/activate"

# Vai até o diretório do app
cd "$BASE_DIR/app" || exit

# Executa o script Python
python3 main.py
