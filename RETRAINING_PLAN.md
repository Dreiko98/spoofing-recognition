# 🎙️ Plan de Re-entrenamiento con Podcast

## 🎯 Objetivo
Mejorar la robustez del modelo para manejar:
- Diferentes calidades de audio (compresión, ruido)
- Múltiples hablantes
- Diferentes ambientes acústicos
- Audios de WhatsApp y otras plataformas comprimidas

## 📋 Plan Paso a Paso

### 1️⃣ **Preparar Datos de Podcast** (30-60 min)

#### Opción A: Descargar podcast de YouTube
```bash
# Instalar yt-dlp si no lo tienes
pip install yt-dlp

# Descargar solo audio de un podcast
yt-dlp -x --audio-format mp3 "URL_DEL_PODCAST" -o "data/raw/podcast/podcast.mp3"

# Ejemplos de podcasts en español:
# - The Wild Project
# - La Pija y la Quinqui
# - Entiende Tu Mente
# - Cualquier canal de noticias
```

#### Opción B: Usar audio local
```bash
# Si ya tienes un MP3/WAV
cp tu_podcast.mp3 data/raw/podcast/
```

### 2️⃣ **Segmentar Podcast** (5-10 min)

```bash
# Segmentar en clips de 3 segundos, extraer 100-200 segmentos
python src/data_collection/segment_podcast.py \
    data/raw/podcast/podcast.mp3 \
    --duration 3 \
    --max_segments 150 \
    --voice_ratio 0.7 \
    --output data/raw/podcast_segments \
    --prefix human_podcast
```

**Resultado esperado:**
- 150 archivos WAV de 3 segundos
- Solo segmentos con >70% de voz
- Normalizados a 16kHz mono

### 3️⃣ **Generar TTS Equivalente** (10-15 min)

Necesitas balancear el dataset. Si añades 150 humanos, añade ~150-300 TTS.

```bash
# Generar 200 muestras nuevas de ElevenLabs
python src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs_extended \
    --num_samples 200 \
    --rate_limit 1.5
```

**O mejor: Combinar múltiples fuentes TTS:**
- 100 ElevenLabs (voces variadas)
- 100 Google TTS
- 50 Linux espeak
- 50 otros TTS

### 4️⃣ **Crear Metadata Combinada** (2 min)

```bash
# Combinar todo: dataset original + podcast + nuevo TTS
python src/data_collection/create_metadata_csv.py \
    --output data/metadata_extended.csv
```

### 5️⃣ **Convertir a Formato Estándar** (5-10 min)

```bash
# Procesar todos los nuevos audios
python src/data_collection/convert_to_standard_format.py \
    --csv data/metadata_extended.csv \
    --output_dir data/processed_extended
```

### 6️⃣ **Re-entrenar Modelo** (30-60 min en CPU)

```bash
# Entrenar con dataset extendido
python src/training/train_aasist.py \
    --csv data/metadata_extended.csv \
    --pretrained models/AASIST/models/weights/AASIST.pth \
    --output_dir models/aasist_v2_robust \
    --epochs 20 \
    --lr 0.001 \
    --batch_size 8
```

### 7️⃣ **Validar Nuevo Modelo** (5 min)

```bash
# Probar con los audios de WhatsApp
python src/data_collection/test_whatsapp_audios.py \
    --model models/aasist_v2_robust/best_model.pth
```

## 📊 Expectativas de Mejora

| Métrica | Modelo v1 | Modelo v2 (esperado) |
|---------|-----------|---------------------|
| **Accuracy en WAV limpio** | 100% | 95-100% ✅ |
| **Accuracy en WhatsApp** (umbral 50%) | 0% | 70-80% 🎯 |
| **Accuracy en WhatsApp** (umbral 70%) | 83% | 90-95% ✅ |
| **Generalización** | Buena | Excelente ⭐ |
| **Robustez a ruido** | Baja | Alta ✅ |

## 🎯 Dataset Objetivo

| Tipo | Cantidad Actual | Objetivo | Fuente |
|------|----------------|----------|--------|
| **Humano (original)** | 77 | 77 | Tu voz |
| **Humano (podcast)** | 0 | 150 | 📱 Podcast segmentado |
| **Humano TOTAL** | 77 | **227** | - |
| **TTS (original)** | 145 | 145 | ElevenLabs + Linux |
| **TTS (nuevo)** | 0 | 200 | Múltiples fuentes |
| **TTS TOTAL** | 145 | **345** | - |
| **GRAN TOTAL** | 222 | **~570** | - |

## 💡 Recomendaciones Adicionales

### Para Máxima Robustez:

1. **Variedad de fuentes humanas:**
   - Podcast en español (varios hablantes)
   - Audiobooks
   - Noticias de YouTube
   - Entrevistas

2. **Variedad de TTS:**
   - ElevenLabs (múltiples voces)
   - Google Cloud TTS
   - Amazon Polly
   - Microsoft Azure TTS
   - Linux espeak/festival

3. **Augmentación de datos:**
   - Añadir ruido de fondo
   - Simular compresión de WhatsApp
   - Variar volumen

### Para Testing:

```bash
# Crear conjunto de test independiente
mkdir -p data/test_independent/{human,tts}

# Grabar 10 nuevas voces tuyas
# Generar 10 nuevos TTS
# No usarlos en training - solo para validación final
```

## 🚀 Script Rápido Todo-en-Uno

Voy a crear un script que automatice todo esto...

### Siguiente paso:
```bash
# 1. Descarga un podcast (15-30 min de duración)
# 2. Guárdalo en data/raw/podcast/podcast.mp3
# 3. Ejecuta:
python scripts/retrain_robust_model.py
```

## ⚠️ Notas Importantes

1. **Calidad del podcast:**
   - Preferir voz clara y única (no múltiples personas hablando a la vez)
   - Evitar música de fondo intensa
   - Preferir podcasts de conversación/entrevista

2. **Balance del dataset:**
   - Mantener ratio 1:2 (bonafide:spoof) es ideal
   - Más TTS que humanos ayuda a reducir falsos negativos

3. **Tiempo de entrenamiento:**
   - Con ~570 muestras: 40-90 min en CPU
   - Con GPU: 10-20 min

4. **Expectativa realista:**
   - No esperes 100% con WhatsApp comprimido
   - 85-95% es excelente para audio comprimido
   - El modelo seguirá siendo muy bueno con audio limpio
