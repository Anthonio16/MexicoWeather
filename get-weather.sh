#!/usr/bin/sh
# get-weather.sh - ejecuta main.py con el entorno conda iccd332
# Proyecto ICCD332 Arquitectura de Computadores - Grupo 3
#
# Fuentes:
# - Activar conda en scripts sh: https://stackoverflow.com/questions/34534513/calling-conda-source-activate-from-bash-script
# - dirname para rutas relativas: https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script

# Ir a la carpeta donde vive este script (asi funciona en cualquier maquina)
cd "$(dirname "$0")" || exit 1

# Activar el entorno iccd332 (requisito del proyecto)
# Ajusta la ruta si tu miniforge esta en otro lugar: verifica con `which mamba`
source "$HOME/miniforge3/etc/profile.d/conda.sh"
eval "$(conda shell.bash hook)"
conda activate iccd332

# API key como variable de entorno (no queda expuesta en el codigo)
export OWM_API_KEY="8ee697c6e4a325851b0e01ab51bbb998"

python main.py
