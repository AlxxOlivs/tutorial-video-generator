# src/image_generator.py - Generador de imágenes usando Replicate
import replicate
import os
import requests
from PIL import Image
import io

class ImageGenerator:
    def __init__(self):
        self.client = replicate.Client(api_token=os.getenv('REPLICATE_API_TOKEN'))
        self.model = "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478"
    
    def generate_image(self, prompt: str, output_name: str) -> str:
        """
        Genera una imagen a partir de un prompt usando Stable Diffusion
        
        Args:
            prompt: Descripción de la imagen
            output_name: Nombre base del archivo
        
        Returns:
            Ruta de la imagen generada
        """
        try:
            # Mejorar prompt para mejor calidad
            enhanced_prompt = self._enhance_prompt(prompt)
            
            print(f"🖼️ Generando imagen: {enhanced_prompt[:50]}...")
            
            # Generar imagen con Replicate
            output = self.client.run(
                self.model,
                input={
                    "prompt": enhanced_prompt,
                    "negative_prompt": "blurry, low quality, distorted, ugly, bad anatomy",
                    "width": 768,
                    "height": 768,
                    "num_outputs": 1,
                    "num_inference_steps": 20,
                    "guidance_scale": 7.5
                }
            )
            
            # Descargar y guardar imagen
            image_url = output[0]
            output_path = f"output/images/{output_name}.png"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            response = requests.get(image_url)
            image = Image.open(io.BytesIO(response.content))
            
            # Redimensionar para vídeo (16:9)
            image = image.resize((1280, 720), Image.Resampling.LANCZOS)
            image.save(output_path, "PNG", quality=95)
            
            print(f"✅ Imagen guardada: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Error al generar imagen: {e}")
    
    def _enhance_prompt(self, prompt: str) -> str:
        """Mejora el prompt para obtener mejores imágenes"""
        # Añadir descriptores de calidad
        quality_terms = "high quality, detailed, professional photography, well lit, clear"
        
        # Añadir estilo de tutorial/cocina si es relevante
        if any(word in prompt.lower() for word in ['cocina', 'receta', 'comida', 'ingredientes']):
            style_terms = "kitchen setting, food photography, cooking tutorial style"
            return f"{prompt}, {style_terms}, {quality_terms}"
        
        return f"{prompt}, {quality_terms}"