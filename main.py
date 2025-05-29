#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tutorial Video Generator - Versión Mejorada
Genera videos tutoriales automatizados usando IA
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

# Configuración de logging mejorada
def setup_logging() -> logging.Logger:
    """Configura el sistema de logging con archivos rotativos"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar formato de logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Logger principal
    logger = logging.getLogger('TutorialGenerator')
    logger.setLevel(logging.INFO)
    
    # Handler para archivo
    file_handler = logging.FileHandler(
        log_dir / f"tutorial_generator_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Configuración global mejorada
class Config:
    """Clase para manejar la configuración de la aplicación"""
    
    def __init__(self):
        self.config_file = Path("config.json")
        self.load_config()
    
    def load_config(self) -> None:
        """Carga la configuración desde archivo JSON"""
        default_config = {
            "output_dir": "generated_videos",
            "temp_dir": "temp",
            "max_video_duration": 60,  # segundos
            "video_resolution": [1080, 1920],  # 9:16 para vertical
            "fps": 30,
            "audio_quality": "high",
            "language": "es",
            "voice_settings": {
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 0.8
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logging.error(f"Error cargando configuración: {e}")
        
        self.__dict__.update(default_config)
        self.save_config()
    
    def save_config(self) -> None:
        """Guarda la configuración actual"""
        config_data = {k: v for k, v in self.__dict__.items() 
                      if not k.startswith('_') and k != 'config_file'}
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error guardando configuración: {e}")


class TutorialVideoGenerator:
    """Clase principal para generar videos tutoriales"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.config = Config()
        self.setup_directories()
        
        # Importar módulos locales
        try:
            from .script_generator import ScriptGenerator
            from .image_generator import ImageGenerator
            from .audio_generator import AudioGenerator
            from .video_editor import VideoEditor
            
            self.script_gen = ScriptGenerator()
            self.image_gen = ImageGenerator()
            self.audio_gen = AudioGenerator()
            self.video_editor = VideoEditor()
            
        except ImportError as e:
            self.logger.error(f"Error importando módulos: {e}")
            sys.exit(1)
    
    def setup_directories(self) -> None:
        """Crea los directorios necesarios"""
        directories = [
            self.config.output_dir,
            self.config.temp_dir,
            "assets",
            "logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            self.logger.info(f"Directorio creado/verificado: {directory}")
    
    def generate_video(self, topic: str, style: str = "educational", 
                      duration: int = 30) -> Optional[str]:
        """
        Genera un video tutorial completo
        
        Args:
            topic: Tema del video
            style: Estilo del video (educational, casual, professional)
            duration: Duración aproximada en segundos
            
        Returns:
            Ruta del video generado o None si hay error
        """
        try:
            self.logger.info(f"Iniciando generación de video: {topic}")
            
            # Validar parámetros
            if duration > self.config.max_video_duration:
                duration = self.config.max_video_duration
                self.logger.warning(f"Duración limitada a {duration} segundos")
            
            # 1. Generar guión
            self.logger.info("Generando guión...")
            script_data = self.script_gen.generate_script(
                topic=topic,
                style=style,
                target_duration=duration
            )
            
            if not script_data:
                raise Exception("No se pudo generar el guión")
            
            # 2. Generar imágenes
            self.logger.info("Generando imágenes...")
            images = self.image_gen.generate_images(
                script_data['scenes'],
                style=style
            )
            
            # 3. Generar audio
            self.logger.info("Generando narración...")
            audio_file = self.audio_gen.generate_narration(
                text=script_data['narration'],
                voice_settings=self.config.voice_settings
            )
            
            # 4. Editar video final
            self.logger.info("Editando video final...")
            output_path = self.video_editor.create_video(
                script_data=script_data,
                images=images,
                audio_file=audio_file,
                config=self.config
            )
            
            self.logger.info(f"Video generado exitosamente: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generando video: {str(e)}")
            self.cleanup_temp_files()
            return None
    
    def cleanup_temp_files(self) -> None:
        """Limpia archivos temporales"""
        temp_dir = Path(self.config.temp_dir)
        try:
            for file in temp_dir.glob("*"):
                if file.is_file():
                    file.unlink()
            self.logger.info("Archivos temporales limpiados")
        except Exception as e:
            self.logger.error(f"Error limpiando archivos temporales: {e}")
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de generación"""
        stats = {
            "videos_generated": 0,
            "total_duration": 0,
            "success_rate": 0.0,
            "avg_generation_time": 0.0
        }
        
        # TODO: Implementar tracking de estadísticas
        return stats


def main():
    """Función principal para uso desde línea de comandos"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generador de Videos Tutoriales con IA"
    )
    parser.add_argument("--topic", required=True, help="Tema del video")
    parser.add_argument("--style", default="educational", 
                       choices=["educational", "casual", "professional"],
                       help="Estilo del video")
    parser.add_argument("--duration", type=int, default=30,
                       help="Duración aproximada en segundos")
    parser.add_argument("--gui", action="store_true",
                       help="Abrir interfaz gráfica")
    
    args = parser.parse_args()
    
    generator = TutorialVideoGenerator()
    
    if args.gui:
        # Importar y ejecutar GUI
        try:
            from .gui import TutorialGUI
            app = TutorialGUI(generator)
            app.run()
        except ImportError:
            print("Interfaz gráfica no disponible. Ejecutando en modo CLI.")
            video_path = generator.generate_video(
                topic=args.topic,
                style=args.style,
                duration=args.duration
            )
            if video_path:
                print(f"Video generado: {video_path}")
            else:
                print("Error generando video")
    else:
        video_path = generator.generate_video(
            topic=args.topic,
            style=args.style,
            duration=args.duration
        )
        if video_path:
            print(f"Video generado: {video_path}")
        else:
            print("Error generando video")


if __name__ == "__main__":
    main()