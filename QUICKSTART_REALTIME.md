# 🎤 Quick Start - Detección en Tiempo Real

## ¡Listo para usar!

Tu modelo está entrenado con **100% accuracy**. Ahora puedes detectar deepfakes en tiempo real.

### 1️⃣ Modo Más Rápido: Grabar desde Micrófono

```bash
source .venv/bin/activate
python src/realtime/realtime_detection.py
```

**Qué hace:**
1. Presionas ENTER
2. Cuenta regresiva: 3... 2... 1...
3. Hablas durante 3 segundos 🎤
4. ¡Resultado instantáneo!

**Ejemplo de salida:**
```
======================================================================
  👤  ✅ VOZ HUMANA DETECTADA
======================================================================

📊 Probabilidades:
   🧑 Humano:    97.2% ████████████████████████████████████████
   🤖 Deepfake:   2.8% █

🎯 Confianza: 97.2%
```

### 2️⃣ Analizar Archivos Existentes

```bash
source .venv/bin/activate

# Un solo archivo
python src/realtime/realtime_detection.py --files audio_sospechoso.wav

# Varios archivos
python src/realtime/realtime_detection.py --files audio1.wav audio2.wav audio3.wav

# Todos los archivos de una carpeta
python src/realtime/realtime_detection.py --files data/processed/human/*.wav
```

### 3️⃣ Opciones Útiles

```bash
# Grabar y guardar muestras
python src/realtime/realtime_detection.py --save

# Grabaciones más largas (5 segundos)
python src/realtime/realtime_detection.py --duration 5

# Guardar y grabar 5 segundos
python src/realtime/realtime_detection.py --duration 5 --save
```

## 📊 Resultados del Modelo

Tu modelo fine-tuned tiene:
- ✅ **100% accuracy** en test set
- 🎯 **1.0 AUC-ROC** (perfecto)
- 🚀 **Mejora de +30.56%** sobre modelo pre-entrenado

**Detecta perfectamente:**
- ✅ Tu voz (Germán) como HUMANA
- ✅ ElevenLabs TTS como DEEPFAKE
- ✅ Linux espeak TTS como DEEPFAKE

## 💡 Tips

1. **Audio limpio**: Ambiente silencioso
2. **Habla natural**: Como lo harías normalmente
3. **Volumen adecuado**: Ni muy bajo ni saturado
4. **Duración óptima**: 3-5 segundos

## 🎯 Casos de Uso

### Verificar si un audio es deepfake
```bash
python src/realtime/realtime_detection.py --files audio_sospechoso.mp3
```

### Crear dataset de prueba
```bash
# Graba varias muestras tuyas
python src/realtime/realtime_detection.py --save
# (presiona ENTER varias veces)
```

### Comparar TTS vs Humano
```bash
# Analiza todo junto
python src/realtime/realtime_detection.py --files \
    data/processed/human/*.wav \
    data/processed/elevenlabs/*.wav
```

## 🔧 Solución de Problemas

### Error de micrófono
```bash
# Listar dispositivos disponibles
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Confianza baja
- Asegúrate de que el audio tenga buena calidad
- Prueba con grabaciones más largas: `--duration 5`
- Graba en un ambiente más silencioso

## 📁 Archivos Generados

**Cuando usas `--save`:**
- Se guardan en: `data/realtime_samples/`
- Formato: `20241126_153045_human_98.wav`
  - Timestamp
  - Predicción (human/deepfake)
  - Confianza (98%)

**Modo batch:**
- Genera: `batch_results_TIMESTAMP.json`
- Contiene todas las predicciones y probabilidades

## 🎉 ¡Disfruta!

Tu modelo está listo para detectar deepfakes en tiempo real.

Para más detalles, consulta: `REALTIME_GUIDE.md`
