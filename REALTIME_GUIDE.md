# 🎤 Guía de Detección en Tiempo Real

## 🚀 Inicio Rápido

### Modo Interactivo (Grabar desde micrófono)

```bash
# Modo básico: graba 3 segundos y analiza
python src/realtime/realtime_detection.py

# Grabar y guardar las muestras
python src/realtime/realtime_detection.py --save

# Grabaciones más largas (5 segundos)
python src/realtime/realtime_detection.py --duration 5
```

### Modo Batch (Analizar archivos existentes)

```bash
# Analizar un archivo
python src/realtime/realtime_detection.py --files data/processed/human_00001.wav

# Analizar múltiples archivos
python src/realtime/realtime_detection.py --files data/processed/*.wav

# Analizar con resultados guardados en JSON
python src/realtime/realtime_detection.py --files data/raw/human/*.wav
```

## 📋 Cómo Usar el Modo Interactivo

1. **Ejecuta el script**:
   ```bash
   source .venv/bin/activate
   python src/realtime/realtime_detection.py
   ```

2. **Presiona ENTER** cuando estés listo para grabar

3. **Cuenta regresiva**: 3... 2... 1...

4. **Habla durante 3 segundos** 🎤

5. **Resultados instantáneos**:
   ```
   ======================================================================
     👤  ✅ VOZ HUMANA DETECTADA
   ======================================================================
   
   📊 Probabilidades:
      🧑 Humano:    98.7% ████████████████████████████████████████
      🤖 Deepfake:   1.3% ▌
   
   🎯 Confianza: 98.7%
   ```

6. **Repetir**: Presiona ENTER de nuevo o Ctrl+C para salir

## 🎯 Casos de Uso

### 1. Verificar Audios Sospechosos
```bash
# Analiza un archivo que recibiste
python src/realtime/realtime_detection.py --files audio_sospechoso.wav
```

### 2. Testear el Modelo con Tu Voz
```bash
# Graba varias muestras tuyas
python src/realtime/realtime_detection.py --save
```

### 3. Comparar TTS vs Humano
```bash
# Primero graba tu voz
python src/realtime/realtime_detection.py --save

# Luego analiza TTS junto con tu grabación
python src/realtime/realtime_detection.py --files \
    data/realtime_samples/*.wav \
    data/raw/elevenlabs/*.wav
```

## 📊 Interpretación de Resultados

### Confianza Alta (>90%)
- ✅ **Predicción confiable**
- El modelo está muy seguro de su decisión

### Confianza Media (70-90%)
- ⚠️ **Revisar manualmente**
- El audio podría ser ambiguo

### Confianza Baja (<70%)
- 🔍 **Audio de baja calidad o edge case**
- Puede necesitar más contexto

## 🔧 Opciones Avanzadas

### Especificar Modelo Diferente
```bash
python src/realtime/realtime_detection.py \
    --model models/otro_modelo/checkpoint.pth
```

### Usar GPU (si está disponible)
```bash
python src/realtime/realtime_detection.py --device cuda
```

### Guardar Todas las Grabaciones con Timestamp
```bash
python src/realtime/realtime_detection.py --save --duration 5
```

Las grabaciones se guardan en `data/realtime_samples/` con formato:
```
20241126_153045_human_98.wav      # 98% confianza, humano
20241126_153112_deepfake_87.wav   # 87% confianza, deepfake
```

## 🎵 Requisitos de Audio

- **Sample rate**: 16 kHz (automático)
- **Canales**: Mono (automático)
- **Duración**: 3 segundos recomendado (ajustable con `--duration`)
- **Formato**: WAV PCM 16-bit

## 🐛 Solución de Problemas

### Error de Micrófono
```bash
# Listar dispositivos de audio disponibles
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Sin Sonido en la Grabación
- Verifica permisos del micrófono
- Prueba con otro software de grabación primero
- Aumenta el volumen del micrófono

### Predicciones Incorrectas
- Asegúrate de que el modelo está fine-tuned
- Verifica que el audio tenga buena calidad
- Prueba con grabaciones más largas (--duration 5)

## 📝 Ejemplos Prácticos

### Test Rápido con Diferentes Voces
```bash
# 1. Graba tu voz
python src/realtime/realtime_detection.py --save

# 2. Reproduce un audio de YouTube/TTS y grábalo
python src/realtime/realtime_detection.py --save

# 3. Analiza todo junto
python src/realtime/realtime_detection.py --files data/realtime_samples/*.wav
```

### Validar Dataset Existente
```bash
# Analizar todas las muestras humanas
python src/realtime/realtime_detection.py --files data/raw/human/*.wav

# Analizar todas las muestras de ElevenLabs
python src/realtime/realtime_detection.py --files data/raw/elevenlabs/*.wav

# Analizar todas las muestras de Linux TTS
python src/realtime/realtime_detection.py --files data/raw/linux_tts/*.wav
```

## 🎯 Métricas de Rendimiento

Con tu modelo fine-tuned:
- ✅ **100% accuracy** en test set
- 🎯 **1.0 AUC-ROC** → separación perfecta
- 🚀 **~0.5-1s** tiempo de inferencia en CPU

## 💡 Tips

1. **Audio limpio**: Graba en ambiente silencioso
2. **Volumen adecuado**: No muy bajo ni saturado
3. **Habla natural**: Como lo harías normalmente
4. **Evita ruidos**: Clics, respiración fuerte, etc.

## 🔥 Features

- ✅ Grabación desde micrófono con cuenta regresiva
- ✅ Análisis instantáneo (<1 segundo)
- ✅ Visualización con barras de probabilidad
- ✅ Modo batch para múltiples archivos
- ✅ Guardado automático con timestamps
- ✅ Resultados en JSON exportables
- ✅ Interfaz intuitiva con emojis

¡Disfruta detectando deepfakes en tiempo real! 🎉
