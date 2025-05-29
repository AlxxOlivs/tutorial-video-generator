# 🎬 Tutorial Video Generator

Generador automático de vídeos tutoriales cortos (30-60 segundos) usando IA.

## 🚀 Características

- **Generación automática** de guiones usando OpenAI GPT
- **Síntesis de voz** natural con Bark (gratuito, offline)
- **Imágenes AI** personalizadas con Stable Diffusion (Replicate)
- **Ensamblaje automático** de vídeo con MoviePy
- **Subtítulos incluidos** (próximamente)

## 🛠️ Instalación Rápida

```bash
# Clonar o descargar el proyecto
git clone [tu-repo] tutorial_video_generator
cd tutorial_video_generator

# Ejecutar instalación automática
./setup.sh

# O instalación manual:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## 🔑 Configuración

1. **Obtener claves API** (gratuitas para empezar):
   - [OpenAI](https://platform.openai.com/api-keys) - $5 de crédito gratuito
   - [Replicate](https://replicate.com/account/api-tokens) - Prueba gratuita

2. **Configurar .env**:
   ```env
   OPENAI_API_KEY=tu_clave_aqui
   REPLICATE_API_TOKEN=tu_token_aqui
   ```

## 🎯 Uso

### Básico
```bash
python main.py
# Introduce tu prompt: "Cómo hacer una empanada de atún"
```

### Programático
```python
from main import TutorialVideoGenerator

generator = TutorialVideoGenerator()
video_path = generator.generate_tutorial("Cómo hacer pasta carbonara")
print(f"Vídeo creado: {video_path}")
```

## 📁 Estructura del Proyecto

```
tutorial_video_generator/
├── main.py              # 🎬 Orquestador principal
├── src/
│   ├── script_generator.py   # 📝 Generador de guiones (OpenAI)
│   ├── voice_generator.py    # 🎙️ Síntesis de voz (Bark)
│   ├── image_generator.py    # 🖼️ Generador de imágenes (Replicate)
│   ├── video_assembler.py    # 🎞️ Ensamblador (MoviePy)
│   └── utils.py             # 🔧 Utilidades
└── output/              # 📤 Archivos generados
    ├── videos/         # Vídeos finales (.mp4)
    ├── audio/          # Audio generado (.wav)
    └── images/         # Imágenes (.png)
```

## 🎨 Ejemplos de Prompts

- "Cómo hacer una empanada de atún"
- "Tutorial para plantar una suculenta"
- "Cómo preparar café en V60"
- "Pasos para cambiar una llanta de bicicleta"
- "Cómo hacer origami de grulla"

## 🔧 Personalización

### Cambiar voz:
```python
# En voice_generator.py
self.voice_preset = "v2/es_speaker_1"  # Diferentes voces disponibles
```

### Ajustar calidad de imagen:
```python
# En image_generator.py
"num_inference_steps": 50,  # Más pasos = mejor calidad
"guidance_scale": 10.0      # Más adherencia al prompt
```

### Modificar duración:
```python
# En script_generator.py - Ajustar en el system_prompt
"Genera un guion para un vídeo tutorial de 30-45 segundos"
```

## 🚀 Roadmap

- [x] **MVP básico funcional**
- [x] **Generación de voz offline**
- [x] **Integración con APIs gratuitas**
- [ ] **Subtítulos automáticos**
- [ ] **Vídeos generados (Pika Labs/RunwayML)**
- [ ] **Interfaz web simple**
- [ ] **Optimización de costos**
- [ ] **Múltiples idiomas**

## 💰 Costos Estimados (Uso moderado)

- **OpenAI**: ~$0.002 por tutorial (GPT-3.5)
- **Replicate**: ~$0.10-0.30 por tutorial (4-6 imágenes)
- **Bark**: Gratuito (local)
- **Total por tutorial**: ~$0.10-0.30

## 🛟 Solución de Problemas

### Error: "No se encuentra ffmpeg"
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows: Descargar desde https://ffmpeg.org/
```

### Error: "CUDA no disponible"
```python
# Bark funcionará en CPU (más lento pero funcional)
# Para acelerar: instalar CUDA y PyTorch con GPU
```

### Error: "API Key inválida"
```bash
# Verificar que las claves estén en .env
# Verificar que tengas créditos disponibles
```

## 📞 Soporte

- **Issues**: Reportar bugs o solicitar funciones
- **Discusiones**: Compartir ejemplos y casos de uso
- **Wiki**: Documentación detallada

## 📄 Licencia

MIT License - Úsalo libremente para proyectos personales y comerciales.

---

# examples/test_prompts.txt
# Prompts de Ejemplo para Tutoriales

## 🍳 Cocina y Recetas
- Cómo hacer una empanada de atún
- Tutorial para preparar café espresso perfecto
- Cómo hacer pasta carbonara en 5 pasos
- Receta rápida de guacamole casero
- Cómo hornear galletas de chocolate
- Tutorial de smoothie verde saludable

## 🌱 Jardinería y Plantas
- Cómo plantar una suculenta paso a paso
- Tutorial para germinar semillas de tomate
- Cómo cuidar una planta de albahaca
- Pasos para hacer compost casero
- Cómo propagar plantas por esquejes

## 🔧 Bricolaje y Reparaciones
- Cómo cambiar una llanta de bicicleta
- Tutorial para arreglar un grifo que gotea
- Cómo instalar una estantería flotante
- Pasos para cambiar un enchufe
- Cómo armar un mueble de IKEA rápidamente

## 🎨 Arte y Manualidades
- Cómo hacer origami de grulla japonesa
- Tutorial de dibujo: rostro básico
- Cómo tejer una bufanda para principiantes
- Pasos para hacer slime casero
- Tutorial de acuarela: técnica húmedo sobre húmedo

## 💻 Tecnología Básica
- Cómo hacer backup de fotos del móvil
- Tutorial para crear una contraseña segura
- Cómo limpiar la pantalla del ordenador
- Pasos para actualizar aplicaciones del móvil
- Cómo conectarse a WiFi por primera vez
