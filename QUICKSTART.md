# Guía Rápida: Formato de Datos y Generación de Muestras

## 📝 Resumen

Has creado el esqueleto del proyecto. Ahora toca:

1. ✅ **Ver el formato de datos** → Notebook `notebooks/01_data_exploration.ipynb`
2. ✅ **Generar nuevas muestras** → Scripts en `src/data_collection/`

---

## 1️⃣ Formato de datos esperado

### Audio procesado
- **Formato:** WAV PCM 16-bit
- **Sample rate:** 16 kHz
- **Canales:** mono
- **Ubicación:** `data/processed/{source}/{split}/`

### CSV de metadata
**Ubicación:** `data/metadata/metadata_all.csv`

**Columnas:**
```csv
filepath,label,source,tts_engine,text,split
data/processed/combined/train/human_00001.wav,bonafide,human,,"Hola",train
data/processed/combined/train/siri_00001.wav,spoof,siri,macos_siri,"Hola",train
data/processed/combined/train/eleven_00001.wav,spoof,elevenlabs,eleven_flash_v2_5,"Hola",train
```

**Labels:**
- `bonafide` = humano (clase 0)
- `spoof` = sintético (clase 1)

---

## 2️⃣ Cómo generar muestras

### A. Siri (macOS) 🍎

```bash
# Listar voces disponibles
python src/data_collection/generate_siri_samples.py --list_voices

# Generar 100 muestras en español
python src/data_collection/generate_siri_samples.py \
    --output_dir data/raw/siri \
    --num_samples 100 \
    --language es
```

**Salida:** `data/raw/siri/*.aiff` + `metadata.json`

### B. ElevenLabs 🤖

```bash
# 1. Instalar cliente
pip install elevenlabs

# 2. Configurar API key
export ELEVENLABS_API_KEY="tu_clave_aqui"

# 3. Listar voces
python src/data_collection/generate_elevenlabs_samples.py --list_voices

# 4. Generar 100 muestras
python src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs \
    --num_samples 100 \
    --model eleven_flash_v2_5 \
    --rate_limit 1.0
```

**Salida:** `data/raw/elevenlabs/*.mp3` + `metadata.json`

### C. Grabaciones humanas 🎤

```bash
# 1. Instalar dependencias
pip install sounddevice soundfile

# 2. Listar dispositivos de audio
python src/data_collection/record_human_samples.py --list_devices

# 3. Grabar interactivamente
python src/data_collection/record_human_samples.py \
    --output_dir data/raw/human \
    --num_samples 50 \
    --duration 5 \
    --speaker_id speaker_1
```

**Salida:** `data/raw/human/*.wav` + `metadata_speaker_1.json`

---

## 3️⃣ Convertir a formato estándar

**Todos los audios deben convertirse a WAV 16kHz mono:**

```bash
# Convertir Siri
python src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/siri \
    --output_dir data/processed/siri

# Convertir ElevenLabs
python src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/elevenlabs \
    --output_dir data/processed/elevenlabs

# Convertir humano
python src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/human \
    --output_dir data/processed/human
```

---

## 4️⃣ Explorar el formato (Notebook)

```bash
# Abrir Jupyter
jupyter notebook notebooks/01_data_exploration.ipynb
```

El notebook te muestra:
- Formato de audio esperado
- Estructura del CSV
- Cómo cargar con el DataLoader
- Balance de clases

---

## 📊 Dataset recomendado

| Tipo | Cantidad | Label |
|------|----------|-------|
| Humano | 200-500 | bonafide |
| Siri | 150-300 | spoof |
| ElevenLabs | 150-300 | spoof |
| **Total** | **500-1100** | |

**Splits:**
- Train: 70%
- Dev: 15%
- Test: 15%

---

## ⚡ Quick Start (ejemplo completo)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt
pip install elevenlabs sounddevice  # opcionales

# 2. Generar Siri (macOS)
python src/data_collection/generate_siri_samples.py \
    --output_dir data/raw/siri \
    --num_samples 100 \
    --language es

# 3. Generar ElevenLabs
export ELEVENLABS_API_KEY="tu_clave"
python src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs \
    --num_samples 100

# 4. Grabar humanos
python src/data_collection/record_human_samples.py \
    --output_dir data/raw/human \
    --num_samples 50

# 5. Convertir todo a 16kHz mono
for source in siri elevenlabs human; do
    python src/data_collection/convert_to_standard_format.py \
        --input_dir data/raw/$source \
        --output_dir data/processed/$source
done

# 6. [Siguiente paso] Generar metadata_all.csv y entrenar
```

---

## 📚 Archivos creados

- ✅ `notebooks/01_data_exploration.ipynb` → exploración del formato
- ✅ `src/data_collection/generate_siri_samples.py` → generador Siri
- ✅ `src/data_collection/generate_elevenlabs_samples.py` → generador ElevenLabs
- ✅ `src/data_collection/record_human_samples.py` → grabador interactivo
- ✅ `src/data_collection/convert_to_standard_format.py` → conversor a 16kHz
- ✅ `src/data_collection/README.md` → documentación detallada

---

## 🚀 Próximos pasos

1. Ejecutar los scripts para generar tu dataset
2. Verificar el formato con el notebook
3. Crear script para generar `metadata_all.csv` con splits automáticos
4. Entrenar el modelo con `src/training/train_custom.py`

¿Qué quieres hacer ahora?
- Probar los scripts de generación
- Crear el script de generación de metadata CSV
- Explorar el notebook
- Otra cosa
