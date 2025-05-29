# src/voice_generator.py - Generador de voz usando Bark
import os
import scipy
import numpy as np
from bark import SAMPLE_RATE, generate_audio, preload_models
from bark.generation import SAMPLE_RATE
import warnings
warnings.filterwarnings("ignore")

class VoiceGenerator:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.voice_preset = "v2/es_speaker_6"  # Voz en español
        
        # Precargar modelos de Bark
        print("🔄 Cargando modelos de voz...")
        preload_models()
        print("✅ Modelos de voz cargados")
    
    def generate_voice(self, text: str, output_name: str) -> str:
        """
        Genera audio a partir de texto usando Bark
        
        Args:
            text: Texto a convertir en voz
            output_name: Nombre base del archivo de salida
        
        Returns:
            Ruta del archivo de audio generado
        """
        try:
            # Limpiar y preparar texto
            text = self._prepare_text(text)
            
            print(f"🎙️ Generando audio para: {text[:50]}...")
            
            # Generar audio con Bark
            audio_array = generate_audio(
                text,
                history_prompt=self.voice_preset,
                text_temp=0.7,
                waveform_temp=0.7
            )
            
            # Guardar archivo
            output_path = f"output/audio/{output_name}_voice.wav"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convertir a formato compatible con scipy
            audio_data = (audio_array * 32767).astype(np.int16)
            scipy.io.wavfile.write(output_path, self.sample_rate, audio_data)
            
            print(f"✅ Audio guardado en: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Error al generar voz: {e}")
    
    def _prepare_text(self, text: str) -> str:
        """Prepara el texto para una mejor síntesis de voz"""
        # Limpiar texto
        text = text.strip()
        
        # Añadir pausas naturales
        text = text.replace('.', '. ')
        text = text.replace(',', ', ')
        text = text.replace(':', ': ')
        
        # Limitar longitud para Bark
        if len(text) > 500:
            text = text[:500] + "..."
        
        return text