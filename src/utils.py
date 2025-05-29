# src/utils.py - Utilidades del sistema
import os
import shutil
from pathlib import Path

def setup_directories():
    """Crea las carpetas necesarias para el proyecto"""
    directories = [
        'output/videos',
        'output/audio', 
        'output/images',
        'temp'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def clean_temp_files():
    """Limpia archivos temporales"""
    temp_dir = Path('temp')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

def validate_env_variables():
    """Valida que las variables de entorno estén configuradas"""
    required_vars = ['OPENAI_API_KEY', 'REPLICATE_API_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise Exception(f"Faltan variables de entorno: {', '.join(missing_vars)}")
    
    return True