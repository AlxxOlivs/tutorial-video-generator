# main.py - Archivo principal del generador de tutoriales
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from src.script_generator import ScriptGenerator
from src.voice_generator import VoiceGenerator
from src.image_generator import ImageGenerator
from src.video_assembler import VideoAssembler
from src.utils import setup_directories, clean_temp_files

# Cargar variables de entorno
load_dotenv()

class TutorialVideoGenerator:
    def __init__(self):
        self.script_gen = ScriptGenerator()
        self.voice_gen = VoiceGenerator()
        self.image_gen = ImageGenerator()
        self.video_assembler = VideoAssembler()
        
        # Configurar directorios
        setup_directories()
    
    def generate_tutorial(self, prompt: str, output_name: str = None) -> str:
        """
        Genera un tutorial completo desde un prompt
        
        Args:
            prompt: Descripción del tutorial (ej: "Cómo hacer una empanada de atún")
            output_name: Nombre del archivo de salida (opcional)
        
        Returns:
            Ruta del vídeo generado
        """
        try:
            print(f"🎬 Iniciando generación de tutorial: {prompt}")
            
            # 1. Generar guion estructurado
            print("📝 Generando guion...")
            script_data = self.script_gen.generate_script(prompt)
            
            # 2. Generar audio narración
            print("🎙️ Generando voz en off...")
            audio_path = self.voice_gen.generate_voice(
                script_data['full_text'],
                output_name or "tutorial"
            )
            
            # 3. Generar imágenes para cada paso
            print("🖼️ Generando imágenes...")
            image_paths = []
            for i, step in enumerate(script_data['steps']):
                image_path = self.image_gen.generate_image(
                    step['image_prompt'],
                    f"step_{i+1}"
                )
                image_paths.append(image_path)
            
            # 4. Ensamblar vídeo final
            print("🎞️ Ensamblando vídeo...")
            video_path = self.video_assembler.create_video(
                audio_path=audio_path,
                image_paths=image_paths,
                script_data=script_data,
                output_name=output_name or "tutorial"
            )
            
            print(f"✅ ¡Tutorial completado! Guardado en: {video_path}")
            return video_path
            
        except Exception as e:
            print(f"❌ Error durante la generación: {str(e)}")
            raise
        
        finally:
            # Limpiar archivos temporales (opcional)
            # clean_temp_files()
            pass

def main():
    """Función principal para ejecutar el generador"""
    generator = TutorialVideoGenerator()
    
    # Ejemplo de uso
    prompt = input("📋 Describe el tutorial que quieres crear: ")
    
    if not prompt.strip():
        prompt = "Cómo hacer una empanada de atún"
        print(f"Usando ejemplo por defecto: {prompt}")
    
    try:
        video_path = generator.generate_tutorial(prompt)
        print(f"\n🎉 ¡Listo! Tu tutorial está en: {video_path}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n💥 Error inesperado: {str(e)}")

if __name__ == "__main__":
    main()
