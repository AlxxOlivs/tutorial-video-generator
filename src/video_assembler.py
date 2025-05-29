# src/video_assembler.py - Ensamblador de vídeo usando MoviePy
from moviepy.editor import *
import os
from typing import List, Dict

class VideoAssembler:
    def __init__(self):
        self.fps = 24
        self.resolution = (1280, 720)
    
    def create_video(self, audio_path: str, image_paths: List[str], 
                    script_data: Dict, output_name: str) -> str:
        """
        Ensambla el vídeo final con imágenes, audio y subtítulos
        
        Args:
            audio_path: Ruta del archivo de audio
            image_paths: Lista de rutas de imágenes
            script_data: Datos del guion con timing
            output_name: Nombre del archivo de salida
        
        Returns:
            Ruta del vídeo final
        """
        try:
            print("🎞️ Ensamblando vídeo...")
            
            # Cargar audio
            audio = AudioFileClip(audio_path)
            total_duration = audio.duration
            
            # Calcular duración por imagen
            duration_per_image = total_duration / len(image_paths)
            
            # Crear clips de imagen
            video_clips = []
            for i, image_path in enumerate(image_paths):
                # Crear clip de imagen
                img_clip = (ImageClip(image_path)
                           .set_duration(duration_per_image)
                           .resize(self.resolution))
                
                # Añadir efecto de zoom suave
                img_clip = img_clip.resize(lambda t: 1 + 0.02 * t)
                
                video_clips.append(img_clip)
            
            # Concatenar clips de imagen
            video = concatenate_videoclips(video_clips, method="compose")
            
            # Sincronizar con audio
            video = video.set_audio(audio)
            
            # Añadir título al inicio
            title_clip = self._create_title_clip(script_data['title'])
            video = CompositeVideoClip([video, title_clip])
            
            # Añadir subtítulos (opcional, simplificado)
            # video = self._add_subtitles(video, script_data)
            
            # Exportar vídeo
            output_path = f"output/videos/{output_name}_tutorial.mp4"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Limpiar memoria
            video.close()
            audio.close()
            
            print(f"✅ Vídeo exportado: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Error al ensamblar vídeo: {e}")
    
    def _create_title_clip(self, title: str) -> TextClip:
        """Crea un clip de título para el vídeo"""
        return (TextClip(title, 
                        fontsize=50, 
                        color='white', 
                        font='Arial-Bold')
                .set_position('center')
                .set_duration(3)
                .on_color(size=self.resolution, color=(0,0,0), opacity=0.6))