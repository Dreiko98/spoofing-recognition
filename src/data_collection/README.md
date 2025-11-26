# Scripts de Recolección de Datos

Esta carpeta contiene scripts para generar y recolectar muestras de audio para el dataset de entrenamiento.

## 🎯 Objetivo

Generar un dataset balanceado con:
- **Bonafide (humano):** grabaciones de voz humana real
- **Spoof (sintético):** 
  - Siri (macOS)
  - ElevenLabs
  - Otros TTS

---

## 📋 Scripts disponibles

### 1. `generate_siri_samples.py` 🍎

Genera muestras usando la voz de Siri en macOS.

**Requisitos:** macOS con comando `say`

```bash
# Listar voces disponibles
python src/data_collection/generate_siri_samples.py --list_voices

# Generar 50 muestras en español
python src/data_collection/generate_siri_samples.py \
    --output_dir data/raw/siri \
    --num_samples 50 \
    --language es

# Generar en inglés
python src/data_collection/generate_siri_samples.py \
    --output_dir data/raw/siri \
    --num_samples 50 \
    --language en
```

**Salida:** archivos `.aiff` + `metadata.json`

---

### 2. `generate_elevenlabs_samples.py` 🤖

Genera muestras usando la API de ElevenLabs.

**Requisitos:** 
```bash
pip install elevenlabs
export ELEVENLABS_API_KEY="tu_clave_aqui"
```

```bash
# Listar voces disponibles
python src/data_collection/generate_elevenlabs_samples.py --list_voices

# Generar 50 muestras
python src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs \
    --num_samples 50 \
    --model eleven_flash_v2_5 \
    --rate_limit 1.0

# Usar una voz específica
python src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs \
    --num_samples 50 \
    --voice_id "21m00Tcm4TlvDq8ikWAM"
```

**Salida:** archivos `.mp3` + `metadata.json`

---

### 3. `record_human_samples.py` 🎤

Grabación interactiva de voz humana usando el micrófono.

**Requisitos:**
```bash
pip install sounddevice soundfile
```

```bash
# Listar dispositivos de audio
python src/data_collection/record_human_samples.py --list_devices

# Grabar 20 muestras
python src/data_collection/record_human_samples.py \
    --output_dir data/raw/human \
    --num_samples 20 \
    --duration 5 \
    --speaker_id speaker_1

# Si tienes múltiples hablantes
python src/data_collection/record_human_samples.py \
    --output_dir data/raw/human \
    --num_samples 20 \
    --speaker_id speaker_2
```

**Salida:** archivos `.wav` (48kHz) + `metadata_speaker_X.json`

---

### 4. `convert_to_standard_format.py` 🔄

Convierte cualquier formato de audio a WAV 16kHz mono (formato AASIST).

**Requisitos:**
```bash
pip install librosa soundfile
```

```bash
# Convertir una carpeta completa
python src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/siri \
    --output_dir data/processed/siri

# Convertir un archivo individual
python src/data_collection/convert_to_standard_format.py \
    --input_file audio.mp3 \
    --output_file audio_16k.wav

# Cambiar el sample rate objetivo
python src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/elevenlabs \
    --output_dir data/processed/elevenlabs \
    --target_sr 16000
```

**Salida:** archivos `.wav` PCM 16-bit, 16kHz, mono

---

## 🔄 Flujo de trabajo recomendado

### Paso 1: Generar datos raw

```bash
# Siri (macOS)
python src/data_collection/generate_siri_samples.py \
    --output_dir data/raw/siri \
    --num_samples 100 \
    --language es

# ElevenLabs (requiere API key)
export ELEVENLABS_API_KEY="tu_clave"
python src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs \
    --num_samples 100 \
    --rate_limit 1.0

# Humano (interactivo)
python src/data_collection/record_human_samples.py \
    --output_dir data/raw/human \
    --num_samples 50 \
    --speaker_id speaker_1
```

### Paso 2: Convertir a formato estándar

```bash
# Convertir todo a WAV 16kHz mono
python src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/siri \
    --output_dir data/processed/siri

python src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/elevenlabs \
    --output_dir data/processed/elevenlabs

python src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/human \
    --output_dir data/processed/human
```

### Paso 3: Generar CSV maestro

(Pendiente: script para combinar metadata y generar `metadata_all.csv` con splits)

---

## 📊 Balance de dataset recomendado

Para un dataset balanceado:

| Tipo | Fuente | Cantidad sugerida | Label |
|------|--------|-------------------|-------|
| Humano | Grabaciones propias | 200-500 | bonafide |
| Siri | macOS `say` | 150-300 | spoof |
| ElevenLabs | API | 150-300 | spoof |
| **Total** | | **500-1100** | |

Splits recomendados:
- Train: 70%
- Dev: 15%
- Test: 15%

---

## ⚠️ Notas importantes

1. **Siri:** solo funciona en macOS. Si usas Linux/Windows, omite este paso.
2. **ElevenLabs:** requiere API key y tiene límites de uso según tu plan.
3. **Grabaciones humanas:** asegúrate de grabar en ambiente silencioso.
4. **Conversión:** SIEMPRE convierte a 16kHz mono antes de entrenar.
5. **Metadata:** guarda siempre la metadata JSON para trazabilidad.

---

## 🐛 Troubleshooting

### Error: "Import could not be resolved"
Instala las dependencias:
```bash
pip install -r requirements.txt
pip install elevenlabs sounddevice  # opcionales
```

### Error: "say: command not found"
El script de Siri solo funciona en macOS. Si estás en Linux/Windows, usa solo ElevenLabs y grabaciones humanas.

### Error: "ELEVENLABS_API_KEY not configured"
```bash
export ELEVENLABS_API_KEY="tu_clave_aqui"
```

### Audio con ruido de fondo
- Usa un ambiente silencioso
- Acércate al micrófono (pero sin distorsión)
- Considera usar un filtro de ruido en post-procesamiento
