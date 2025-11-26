# 🚀 GUÍA RÁPIDA: Re-entrenamiento con Podcast

## Opción 1: Script Automatizado (Recomendado)

### 1️⃣ Descargar podcast de YouTube
```bash
# Instalar yt-dlp si no lo tienes
pip install yt-dlp

# Descargar podcast (15-30 minutos, español, diálogo claro)
yt-dlp -x --audio-format mp3 "URL_DEL_PODCAST" -o "data/raw/podcast/podcast.mp3"
```

**Recomendaciones de podcasts:**
- The Wild Project (episodios de entrevistas)
- La Pija y la Quinqui
- Entiende Tu Mente
- Nadie Sabe Nada
- Cualquier podcast de conversación en español claro

### 2️⃣ Ejecutar script automatizado
```bash
chmod +x scripts/retrain_robust_model.py

# Opción A: Con ElevenLabs (requiere API key)
export ELEVENLABS_API_KEY="tu_api_key_aqui"
python scripts/retrain_robust_model.py \
    --podcast data/raw/podcast/podcast.mp3 \
    --segments 150 \
    --tts_samples 200 \
    --epochs 20

# Opción B: Solo con Linux TTS (gratis, sin API)
python scripts/retrain_robust_model.py \
    --podcast data/raw/podcast/podcast.mp3 \
    --segments 150 \
    --tts_samples 200 \
    --epochs 20 \
    --skip_tts

# Si usas --skip_tts, genera TTS manualmente antes:
python src/data_collection/generate_linux_tts_samples.py \
    --output_dir data/raw/linux_tts \
    --num_samples 200
```

El script automatizado hará:
1. ✂️ Segmentar podcast en 150 clips de 3 segundos
2. 🤖 Generar 200 muestras TTS (ElevenLabs o Linux TTS)
3. 📝 Crear metadata combinada
4. 🔄 Convertir todo a formato estándar WAV 16kHz
5. 🏋️ Re-entrenar modelo por 20 épocas
6. 📊 Guardar modelo mejorado en `models/aasist_v2_robust/`

---

## Opción 2: Paso a Paso Manual

### 1️⃣ Segmentar podcast
```bash
python src/data_collection/segment_podcast.py \
    data/raw/podcast/podcast.mp3 \
    --duration 3 \
    --max_segments 150 \
    --voice_ratio 0.7 \
    --output data/raw/podcast_segments \
    --prefix human_podcast
```

### 2️⃣ Generar muestras TTS

**Opción A: ElevenLabs (mejor calidad)**
```bash
python src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs_extended \
    --num_samples 200 \
    --rate_limit 1.5
```

**Opción B: Linux TTS (gratis)**
```bash
# Instalar engines TTS
sudo apt install espeak libttspico-utils

# Generar muestras
python src/data_collection/generate_linux_tts_samples.py \
    --output_dir data/raw/linux_tts \
    --num_samples 200
```

### 3️⃣ Crear metadata combinada
```bash
python src/data_collection/create_metadata_csv.py \
    --output data/metadata_extended.csv
```

### 4️⃣ Convertir a formato estándar
```bash
python src/data_collection/convert_to_standard_format.py \
    --csv data/metadata_extended.csv \
    --output_dir data/processed_extended
```

### 5️⃣ Re-entrenar modelo
```bash
python src/training/train_aasist.py \
    --csv data/metadata_extended.csv \
    --pretrained models/AASIST/models/weights/AASIST.pth \
    --output_dir models/aasist_v2_robust \
    --epochs 20 \
    --lr 0.001 \
    --batch_size 8
```

---

## 📊 Validación del Modelo Mejorado

### Test con audios de WhatsApp
```bash
python src/data_collection/test_whatsapp_audios.py \
    --model models/aasist_v2_robust/best_model.pth \
    --threshold 0.5
```

### Comparar modelo antiguo vs nuevo
```bash
python src/evaluation/compare_models.py \
    --model1 models/aasist_finetuned/best_model.pth \
    --model2 models/aasist_v2_robust/best_model.pth \
    --test_dir data/test_validation/whatsapp_processed
```

### Prueba en tiempo real
```bash
python src/realtime/realtime_detection.py \
    --model models/aasist_v2_robust/best_model.pth \
    --threshold 0.5
```

---

## 📈 Resultados Esperados

| Métrica | Modelo Original | Modelo Mejorado |
|---------|----------------|-----------------|
| **WhatsApp (threshold 50%)** | 0% (0/6) | 70-80% |
| **WhatsApp (threshold 70%)** | 83.3% (5/6) | 90-95% |
| **Audio limpio WAV** | 95-100% | 95-100% |
| **Nuevas voces TTS** | 100% | 100% |
| **Dataset size** | 222 muestras | 572 muestras |

---

## 🔧 Troubleshooting

### Error: "No module named 'yt_dlp'"
```bash
pip install yt-dlp
```

### Error: "espeak: command not found"
```bash
sudo apt install espeak libttspico-utils
```

### Error: "ELEVENLABS_API_KEY not found"
```bash
# Opción 1: Usar Linux TTS (gratis)
python scripts/retrain_robust_model.py --skip_tts ...

# Opción 2: Configurar API key
export ELEVENLABS_API_KEY="tu_key_aqui"
```

### Poco espacio en disco
```bash
# Ver tamaño de datasets
du -sh data/raw/*

# Limpiar segmentos antiguos si es necesario
rm -rf data/raw/podcast_segments_old
```

### Entrenamiento muy lento
```bash
# Reducir épocas
python scripts/retrain_robust_model.py --epochs 10 ...

# Aumentar batch size (si tienes RAM)
# Edita train_aasist.py: --batch_size 16
```

---

## ⏱️ Tiempos Estimados

| Paso | Tiempo (CPU) |
|------|--------------|
| Descargar podcast | 1-2 min |
| Segmentar (150 clips) | 2-5 min |
| Generar TTS (200) | 5-10 min |
| Convertir formato | 3-5 min |
| Re-entrenar (20 épocas) | 40-90 min |
| **TOTAL** | **~1-2 horas** |

---

## 📝 Notas Importantes

1. **Balance del dataset**: Mantén ratio ~1:2 bonafide:spoof
   - 227 humanos + 345 TTS = ratio 1:1.5 ✅
   
2. **Calidad del podcast**:
   - Preferir conversaciones/entrevistas (no música)
   - Audio claro, sin mucho ruido de fondo
   - Múltiples voces (diversidad)

3. **Validación continua**:
   - Después de entrenar, SIEMPRE valida con WhatsApp
   - Compara con modelo anterior
   - Ajusta threshold si es necesario

4. **Backup**:
   - Guarda modelo antiguo: `cp -r models/aasist_finetuned models/aasist_finetuned_backup`
   - Git commit después de entrenar: `git add . && git commit -m "Model v2 trained"`
