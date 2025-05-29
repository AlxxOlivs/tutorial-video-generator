import openai
import json
import os
from typing import Dict, List

class ScriptGenerator:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
    
    def generate_script(self, prompt: str) -> Dict:
        """
        Genera un guion estructurado para el tutorial
        
        Returns:
            Dict con estructura: {
                'title': str,
                'full_text': str,
                'steps': [{'text': str, 'image_prompt': str, 'duration': float}]
            }
        """
        system_prompt = """
        Eres un experto en crear tutoriales cortos y claros. 
        
        Genera un guion para un vídeo tutorial de 45-60 segundos que incluya:
        1. Un título atractivo
        2. Una introducción muy breve (5-7 segundos)
        3. 4-6 pasos principales claros y concisos
        4. Una conclusión motivadora (3-5 segundos)
        
        Para cada paso, también genera una descripción visual detallada para crear imágenes.
        
        Responde SOLO en formato JSON con esta estructura:
        {
            "title": "Título del tutorial",
            "full_text": "Texto completo para narrar",
            "steps": [
                {
                    "text": "Texto del paso",
                    "image_prompt": "Descripción detallada para generar imagen",
                    "duration": 8.0
                }
            ]
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Crea un tutorial sobre: {prompt}"}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Limpiar posibles markdown
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            script_data = json.loads(content)
            
            # Validar estructura
            self._validate_script(script_data)
            
            return script_data
            
        except json.JSONDecodeError as e:
            raise Exception(f"Error al parsear respuesta de OpenAI: {e}")
        except Exception as e:
            raise Exception(f"Error al generar guion: {e}")
    
    def _validate_script(self, script_data: Dict):
        """Valida que el guion tenga la estructura correcta"""
        required_keys = ['title', 'full_text', 'steps']
        for key in required_keys:
            if key not in script_data:
                raise Exception(f"Falta la clave '{key}' en el guion generado")
        
        if not isinstance(script_data['steps'], list) or len(script_data['steps']) == 0:
            raise Exception("El guion debe tener al menos un paso")