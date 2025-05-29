#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Generator - Generador de Guiones Mejorado
Genera guiones estructurados para videos tutoriales usando IA gratuita
"""

import logging
import json
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import time
import requests
from datetime import datetime

# Alternativa gratuita a OpenAI
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers no disponible. Instalando...")

# API gratuita como backup
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class ScriptTemplate:
    """Plantillas de guiones para diferentes tipos de contenido"""
    
    TEMPLATES = {
        "educational": {
            "structure": [
                {"type": "hook", "duration": 3, "purpose": "Enganchar audiencia"},
                {"type": "intro", "duration": 5, "purpose": "Presentar tema"},
                {"type": "main_content", "duration": 20, "purpose": "Contenido principal"},
                {"type": "example", "duration": 7, "purpose": "Ejemplo práctico"},
                {"type": "recap", "duration": 3, "purpose": "Resumen clave"},
                {"type": "call_to_action", "duration": 2, "purpose": "CTA final"}
            ],
            "tone": "profesional pero accesible",
            "vocabulary": "técnico pero explicado"
        },
        
        "casual": {
            "structure": [
                {"type": "hook", "duration": 4, "purpose": "Saludo casual"},
                {"type": "intro", "duration": 6, "purpose": "¿Qué vamos a ver?"},
                {"type": "main_content", "duration": 18, "purpose": "Contenido paso a paso"},
                {"type": "tips", "duration": 5, "purpose": "Tips extras"},
                {"type": "outro", "duration": 7, "purpose": "Despedida y CTA"}
            ],
            "tone": "conversacional y amigable",
            "vocabulary": "cotidiano y simple"
        },
        
        "professional": {
            "structure": [
                {"type": "intro", "duration": 3, "purpose": "Presentación directa"},
                {"type": "overview", "duration": 4, "purpose": "Vista general"},
                {"type": "main_content", "duration": 22, "purpose": "Desarrollo técnico"},
                {"type": "best_practices", "duration": 6, "purpose": "Mejores prácticas"},
                {"type": "conclusion", "duration": 5, "purpose": "Conclusiones"}
            ],
            "tone": "formal y autorativo",
            "vocabulary": "técnico especializado"
        }
    }
    
    @classmethod
    def get_template(cls, style: str) -> Dict:
        """Obtiene plantilla por estilo"""
        return cls.TEMPLATES.get(style, cls.TEMPLATES["educational"])


class FreeAIProvider:
    """Proveedor de IA gratuita usando modelos open source"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.tokenizer = None
        self.setup_model()
    
    def setup_model(self):
        """Configura el modelo de IA gratuito"""
        if not TRANSFORMERS_AVAILABLE:
            self.logger.error("Transformers no disponible. Instala con: pip install transformers torch")
            return
        
        try:
            # Usar modelo pequeño y eficiente para generar texto
            model_name = "microsoft/DialoGPT-medium"  # Modelo gratuito y comercial
            
            self.logger.info(f"Cargando modelo: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Añadir token de padding si no existe
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            self.logger.info("Modelo cargado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error cargando modelo: {e}")
            self.model = None
    
    def generate_text(self, prompt: str, max_length: int = 150) -> str:
        """Genera texto usando el modelo local"""
        if not self.model:
            return self._fallback_generation(prompt)
        
        try:
            # Codificar el prompt
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", 
                                         truncation=True, max_length=512)
            
            # Generar texto
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decodificar resultado
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Limpiar el prompt del resultado
            if prompt in generated_text:
                generated_text = generated_text.replace(prompt, "").strip()
            
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Error generando texto: {e}")
            return self._fallback_generation(prompt)
    
    def _fallback_generation(self, prompt: str) -> str:
        """Generación de respaldo usando plantillas"""
        fallback_responses = {
            "introducir": "Hoy vamos a aprender sobre un tema muy interesante que te ayudará en tu día a día.",
            "explicar": "Este concepto es fundamental y te voy a explicar paso a paso cómo funciona.",
            "ejemplo": "Veamos un ejemplo práctico para que quede más claro.",
            "conclusión": "En resumen, hemos visto los puntos más importantes sobre este tema."
        }
        
        for key, response in fallback_responses.items():
            if key in prompt.lower():
                return response
                
        return "Aquí tienes información importante sobre el tema que estamos tratando."


class ScriptGenerator:
    """Generador principal de guiones"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_provider = FreeAIProvider()
        self.cache_dir = Path("cache/scripts")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Base de conocimientos local
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict:
        """Carga base de conocimientos desde archivo JSON"""
        kb_file = Path("knowledge_base.json")
        
        if kb_file.exists():
            try:
                with open(kb_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error cargando base de conocimientos: {e}")
        
        # Base de conocimientos por defecto
        default_kb = {
            "programming": {
                "keywords": ["código", "programación", "desarrollo", "software"],
                "concepts": ["variables", "funciones", "loops", "condicionales"],
                "examples": ["Python", "JavaScript", "HTML", "CSS"]
            },
            "design": {
                "keywords": ["diseño", "UI", "UX", "gráfico"],
                "concepts": ["colores", "tipografía", "layout", "usuario"],
                "examples": ["Photoshop", "Figma", "Canva", "Adobe"]
            },
            "business": {
                "keywords": ["negocio", "empresa", "marketing", "ventas"],
                "concepts": ["estrategia", "clientes", "productos", "servicios"],
                "examples": ["startup", "e-commerce", "social media", "SEO"]
            }
        }
        
        # Guardar base por defecto
        try:
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(default_kb, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando base de conocimientos: {e}")
        
        return default_kb
    
    def _detect_topic_category(self, topic: str) -> str:
        """Detecta la categoría del tema"""
        topic_lower = topic.lower()
        
        for category, data in self.knowledge_base.items():
            for keyword in data.get("keywords", []):
                if keyword in topic_lower:
                    return category
        
        return "general"
    
    def _generate_cache_key(self, topic: str, style: str, duration: int) -> str:
        """Genera clave única para cache"""
        import hashlib
        key_string = f"{topic}_{style}_{duration}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Carga guión desde cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    
                # Verificar que no sea muy antiguo (7 días)
                cache_time = datetime.fromisoformat(cached_data.get('created_at', ''))
                if (datetime.now() - cache_time).days < 7:
                    self.logger.info(f"Guión cargado desde cache: {cache_key}")
                    return cached_data.get('script_data')
                    
            except Exception as e:
                self.logger.error(f"Error cargando cache: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, script_data: Dict) -> None:
        """Guarda guión en cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cache_data = {
            'created_at': datetime.now().isoformat(),
            'script_data': script_data
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando cache: {e}")
    
    def generate_script(self, topic: str, style: str = "educational", 
                       target_duration: int = 30) -> Optional[Dict]:
        """
        Genera un guión completo para el video
        
        Args:
            topic: Tema del video
            style: Estilo del guión
            target_duration: Duración objetivo en segundos
            
        Returns:
            Diccionario con el guión estructurado
        """
        try:
            self.logger.info(f"Generando guión para: {topic}")
            
            # Verificar cache
            cache_key = self._generate_cache_key(topic, style, target_duration)
            cached_script = self._load_from_cache(cache_key)
            if cached_script:
                return cached_script
            
            # Obtener plantilla
            template = ScriptTemplate.get_template(style)
            category = self._detect_topic_category(topic)
            
            # Ajustar duración de secciones según duración total
            sections = self._adjust_section_durations(template["structure"], target_duration)
            
            # Generar contenido para cada sección
            script_sections = []
            scene_descriptions = []
            full_narration = []
            
            for section in sections:
                self.logger.info(f"Generando sección: {section['type']}")
                
                content = self._generate_section_content(
                    topic=topic,
                    section=section,
                    style=template,
                    category=category
                )
                
                if content:
                    script_sections.append({
                        "type": section["type"],
                        "duration": section["duration"],
                        "content": content["text"],
                        "visual_cues": content["visual"],
                        "timing": content["timing"]
                    })
                    
                    scene_descriptions.append(content["visual"])
                    full_narration.append(content["text"])
            
            # Compilar guión final
            script_data = {
                "topic": topic,
                "style": style,
                "duration": target_duration,
                "created_at": datetime.now().isoformat(),
                "sections": script_sections,
                "scenes": scene_descriptions,
                "narration": " ".join(full_narration),
                "metadata": {
                    "word_count": len(" ".join(full_narration).split()),
                    "estimated_reading_time": target_duration,
                    "category": category,
                    "template_used": style
                }
            }
            
            # Guardar en cache
            self._save_to_cache(cache_key, script_data)
            
            self.logger.info("Guión generado exitosamente")
            return script_data
            
        except Exception as e:
            self.logger.error(f"Error generando guión: {e}")
            return None
    
    def _adjust_section_durations(self, structure: List[Dict], total_duration: int) -> List[Dict]:
        """Ajusta las duraciones de las secciones según la duración total"""
        original_total = sum(section["duration"] for section in structure)
        ratio = total_duration / original_total
        
        adjusted_sections = []
        for section in structure:
            adjusted_duration = max(2, int(section["duration"] * ratio))  # Mínimo 2 segundos
            adjusted_sections.append({
                **section,
                "duration": adjusted_duration
            })
        
        return adjusted_sections
    
    def _generate_section_content(self, topic: str, section: Dict, 
                                style: Dict, category: str) -> Optional[Dict]:
        """Genera contenido específico para una sección"""
        
        section_type = section["type"]
        duration = section["duration"]
        
        # Prompts específicos por tipo de sección
        prompts = {
            "hook": f"Crea un gancho atractivo de {duration} segundos sobre {topic}. Debe ser impactante y generar curiosidad.",
            "intro": f"Escribe una introducción de {duration} segundos que presente el tema {topic} de forma clara.",
            "main_content": f"Desarrolla el contenido principal sobre {topic} en {duration} segundos. Incluye información valiosa y práctica.",
            "example": f"Proporciona un ejemplo concreto y práctico sobre {topic} que dure {duration} segundos.",
            "recap": f"Crea un resumen de {duration} segundos de los puntos clave sobre {topic}.",
            "call_to_action": f"Escribe un call-to-action de {duration} segundos que motive a la audiencia.",
            "tips": f"Comparte {duration} segundos de tips útiles sobre {topic}.",
            "outro": f"Crea una despedida de {duration} segundos que sea memorable y amigable."
        }
        
        # Generar texto usando IA
        prompt = prompts.get(section_type, f"Escribe contenido sobre {topic} para {section_type}")
        
        try:
            # Generar contenido
            generated_text = self.ai_provider.generate_text(prompt, max_length=100)
            
            # Limpiar y procesar texto
            cleaned_text = self._clean_generated_text(generated_text, duration)
            
            # Generar descripción visual
            visual_description = self._generate_visual_description(topic, section_type, category)
            
            # Calcular timing
            words_per_second = 2.5  # Velocidad promedio de habla
            estimated_words = int(duration * words_per_second)
            
            return {
                "text": cleaned_text,
                "visual": visual_description,
                "timing": {
                    "duration": duration,
                    "words": len(cleaned_text.split()),
                    "target_words": estimated_words
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generando contenido para {section_type}: {e}")
            return self._generate_fallback_content(topic, section_type, duration)
    
    def _clean_generated_text(self, text: str, target_duration: int) -> str:
        """Limpia y ajusta el texto generado"""
        # Limpiar caracteres extraños
        text = re.sub(r'[^\w\s\.\,\!\?\:\;]', '', text)
        
        # Ajustar longitud según duración
        words = text.split()
        target_words = int(target_duration * 2.5)  # 2.5 palabras por segundo
        
        if len(words) > target_words:
            text = " ".join(words[:target_words])
        elif len(words) < target_words * 0.7:  # Si es muy corto
            # Expandir un poco el texto
            text += " Esto es fundamental para entender el concepto correctamente."
        
        # Asegurar que termine con puntuación
        if not text.endswith(('.', '!', '?')):
            text += "."
        
        return text.strip()
    
    def _generate_visual_description(self, topic: str, section_type: str, category: str) -> str:
        """Genera descripción para las imágenes"""
        
        visual_templates = {
            "hook": f"Imagen llamativa relacionada con {topic}, colores vibrantes, estilo moderno",
            "intro": f"Imagen profesional sobre {topic}, limpia y clara",
            "main_content": f"Diagrama o infografía explicando {topic}, estilo educativo",
            "example": f"Ejemplo visual práctico de {topic}, realista y detallado",
            "recap": f"Resumen visual de conceptos clave de {topic}, organizado",
            "call_to_action": f"Imagen motivacional relacionada con {topic}, inspiradora"
        }
        
        base_description = visual_templates.get(section_type, f"Imagen sobre {topic}")
        
        # Añadir contexto según categoría
        category_styles = {
            "programming": ", con elementos de código y tecnología",
            "design": ", con elementos gráficos y creativos",
            "business": ", con elementos profesionales y corporativos",
            "general": ", estilo limpio y profesional"
        }
        
        return base_description + category_styles.get(category, category_styles["general"])
    
    def _generate_fallback_content(self, topic: str, section_type: str, duration: int) -> Dict:
        """Genera contenido de respaldo cuando falla la IA"""
        
        fallback_texts = {
            "hook": f"¿Sabías que {topic} puede cambiar completamente tu perspectiva? Quédate para descubrirlo.",
            "intro": f"Hoy vamos a explorar {topic} de una manera práctica y fácil de entender.",
            "main_content": f"El {topic} es un concepto fundamental que todos deberíamos conocer. Te explico los puntos más importantes.",
            "example": f"Veamos un ejemplo real de cómo aplicar {topic} en la práctica diaria.",
            "recap": f"Para resumir, hemos visto que {topic} es importante por estas razones clave.",
            "call_to_action": f"Si te gustó este contenido sobre {topic}, no olvides seguirme para más tips como este."
        }
        
        text = fallback_texts.get(section_type, f"Contenido interesante sobre {topic}.")
        
        return {
            "text": text,
            "visual": f"Imagen profesional sobre {topic}",
            "timing": {
                "duration": duration,
                "words": len(text.split()),
                "target_words": int(duration * 2.5)
            }
        }
    
    def validate_script(self, script_data: Dict) -> bool:
        """Valida que el guión esté bien formado"""
        required_fields = ["topic", "style", "sections", "narration", "scenes"]
        
        for field in required_fields:
            if field not in script_data:
                self.logger.error(f"Campo requerido faltante: {field}")
                return False
        
        if not script_data["sections"]:
            self.logger.error("No hay secciones en el guión")
            return False
        
        return True