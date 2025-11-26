# 📋 Cheatsheet de comandos útiles

## 🎯 Resumen rápido

```bash
# Ver formato de datos esperado
python3 src/data_collection/show_data_format.py

# Ver estructura del proyecto
tree -L 3 -I '__pycache__|*.pyc|.ipynb_checkpoints' --dirsfirst
```

---

## 1️⃣ Generación de datos

### Siri (macOS)
```bash
# Listar voces disponibles
python3 src/data_collection/generate_siri_samples.py --list_voices

# Generar 100 muestras en español
python3 src/data_collection/generate_siri_samples.py \
    --output_dir data/raw/siri \
    --num_samples 100 \
    --language es

# Generar 100 muestras en inglés
python3 src/data_collection/generate_siri_samples.py \
    --output_dir data/raw/siri \
    --num_samples 100 \
    --language en
```

### ElevenLabs
```bash
# Instalar cliente
pip install elevenlabs

# Configurar API key
export ELEVENLABS_API_KEY="tu_clave_aqui"

# Listar voces
python3 src/data_collection/generate_elevenlabs_samples.py --list_voices

# Generar 100 muestras
python3 src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs \
    --num_samples 100 \
    --model eleven_flash_v2_5 \
    --rate_limit 1.0
```

### Grabaciones humanas
```bash
# Instalar dependencias
pip install sounddevice soundfile

# Listar dispositivos de audio
python3 src/data_collection/record_human_samples.py --list_devices

# Grabar 50 muestras (interactivo)
python3 src/data_collection/record_human_samples.py \
    --output_dir data/raw/human \
    --num_samples 50 \
    --duration 5 \
    --speaker_id speaker_1
```

---

## 2️⃣ Conversión a formato estándar

```bash
# Convertir Siri
python3 src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/siri \
    --output_dir data/processed/siri

# Convertir ElevenLabs
python3 src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/elevenlabs \
    --output_dir data/processed/elevenlabs

# Convertir humano
python3 src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/human \
    --output_dir data/processed/human

# Convertir todo de golpe (bash loop)
for source in siri elevenlabs human; do
    python3 src/data_collection/convert_to_standard_format.py \
        --input_dir data/raw/$source \
        --output_dir data/processed/$source
done
```

---

## 3️⃣ Exploración y validación

```bash
# Abrir notebook de exploración
jupyter notebook notebooks/01_data_exploration.ipynb

# Verificar estructura de datos
python3 src/data_collection/show_data_format.py

# Ver estadísticas de archivos generados
find data/processed -name "*.wav" | wc -l  # contar WAVs procesados
du -sh data/raw/*                           # tamaño por carpeta
```

---

## 4️⃣ Entrenamiento

```bash
# Entrenar (requiere metadata_all.csv)
python3 src/training/train_custom.py

# Ver logs durante entrenamiento
# (el script imprime progreso en consola)
```

---

## 5️⃣ Detección en tiempo real

```bash
# Ejecutar detector
python3 src/realtime/realtime_detection.py
```

---

## 🛠️ Utilidades

### Instalar todas las dependencias
```bash
# Core
pip install -r requirements.txt

# Opcionales
pip install elevenlabs sounddevice jupyter
```

### Verificar instalación
```bash
python3 -c "import torch; print(f'PyTorch: {torch.__version__}')"
python3 -c "import librosa; print(f'Librosa: {librosa.__version__}')"
python3 -c "import soundfile; print('soundfile: OK')"
```

### Limpiar archivos temporales
```bash
# Eliminar caches de Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Eliminar checkpoints Jupyter
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
```

---

## 📊 Análisis de dataset

### Contar archivos por tipo
```bash
# Raw
echo "=== RAW ==="
find data/raw/siri -name "*.aiff" 2>/dev/null | wc -l
find data/raw/elevenlabs -name "*.mp3" 2>/dev/null | wc -l
find data/raw/human -name "*.wav" 2>/dev/null | wc -l

# Processed
echo "=== PROCESSED ==="
find data/processed/siri -name "*.wav" 2>/dev/null | wc -l
find data/processed/elevenlabs -name "*.wav" 2>/dev/null | wc -l
find data/processed/human -name "*.wav" 2>/dev/null | wc -l
```

### Ver metadata generada
```bash
# Siri
cat data/raw/siri/metadata.json | python3 -m json.tool | head -n 20

# ElevenLabs
cat data/raw/elevenlabs/metadata.json | python3 -m json.tool | head -n 20

# Humano
cat data/raw/human/metadata_speaker_1.json | python3 -m json.tool | head -n 20
```

### Verificar sample rate de audios
```bash
# Requiere: pip install soundfile
python3 << EOF
import soundfile as sf
from pathlib import Path

for wav in Path('data/processed').rglob('*.wav'):
    info = sf.info(wav)
    print(f"{wav.name}: {info.samplerate}Hz, {info.channels}ch, {info.duration:.2f}s")
    if info.samplerate != 16000 or info.channels != 1:
        print(f"  ⚠️  ADVERTENCIA: formato incorrecto")
EOF
```

---

## 🔍 Troubleshooting

### Error: "Import could not be resolved"
```bash
# Instalar dependencias faltantes
pip install torch numpy pandas soundfile librosa pyyaml tqdm
```

### Error: "say: command not found"
```bash
# Solo en macOS. Si estás en Linux/Windows, omite Siri y usa solo ElevenLabs + humano
```

### Error: "ELEVENLABS_API_KEY not configured"
```bash
# Exportar la variable
export ELEVENLABS_API_KEY="tu_clave_aqui"

# Verificar
echo $ELEVENLABS_API_KEY
```

### Audio con ruido
```bash
# Opciones:
# 1. Grabar en ambiente más silencioso
# 2. Usar un micrófono de mejor calidad
# 3. Post-procesamiento con filtros (requiere noisereduce o similar)
```

---

## 📚 Documentación

| Archivo | Descripción |
|---------|-------------|
| `README.md` | Visión general del proyecto |
| `QUICKSTART.md` | Guía rápida de inicio |
| `src/data_collection/README.md` | Detalles de generación de datos |
| `data/README.md` | Organización de carpetas de datos |
| `models/README.md` | Gestión de checkpoints |

---

## 🚀 Workflow completo (ejemplo)

```bash
# 1. Generar Siri (macOS)
python3 src/data_collection/generate_siri_samples.py \
    --output_dir data/raw/siri --num_samples 150 --language es

# 2. Generar ElevenLabs
export ELEVENLABS_API_KEY="tu_clave"
python3 src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs --num_samples 150

# 3. Grabar humanos
python3 src/data_collection/record_human_samples.py \
    --output_dir data/raw/human --num_samples 300 --speaker_id speaker_1

# 4. Convertir todo a 16kHz mono
for source in siri elevenlabs human; do
    python3 src/data_collection/convert_to_standard_format.py \
        --input_dir data/raw/$source --output_dir data/processed/$source
done

# 5. Verificar
python3 src/data_collection/show_data_format.py
find data/processed -name "*.wav" | wc -l

# 6. [TODO] Crear metadata_all.csv

# 7. Entrenar
python3 src/training/train_custom.py
```
