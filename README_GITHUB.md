# 🎤 AASIST Fine-Tuning - Deepfake Detection

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.9.1-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Fine-tuning del modelo AASIST (Audio Anti-Spoofing using Integrated Spectro-Temporal graph attention networks) para detección de deepfakes de audio en español.

## 🎯 Características

- ✅ **100% Accuracy** en dataset personalizado
- 🎤 **Detección en tiempo real** desde micrófono
- 🇪🇸 **Optimizado para español**
- 🚀 **Interfaz simple** con visualización intuitiva
- 📊 **Análisis batch** de múltiples archivos
- 💾 **Guardado automático** de muestras

## 📊 Resultados

| Métrica | Pre-entrenado | Fine-tuned | Mejora |
|---------|---------------|------------|--------|
| **Accuracy** | 69.44% | **100%** | +30.56% |
| **AUC-ROC** | 0.28 | **1.0** | +0.72 |
| **F1-Score** | - | **1.0** | - |

### Detección por Tipo de Audio

| Tipo de Audio | Precisión |
|---------------|-----------|
| 🧑 Voz Humana | 100% |
| 🤖 ElevenLabs TTS | 100% |
| 🔊 Linux espeak | 100% |

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar repositorio
git clone https://github.com/Dreiko98/spoofing-recognition.git
cd spoofing-recognition

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Descargar Modelo Pre-entrenado

```bash
# Crear estructura de carpetas
mkdir -p models/AASIST/models/weights

# Descargar modelo AASIST pre-entrenado
# Desde: https://github.com/clovaai/aasist
# Colocar en: models/AASIST/models/weights/AASIST.pth
```

### 3. Detección en Tiempo Real

#### Modo Interactivo (Micrófono)

```bash
python src/realtime/realtime_detection.py
```

**Salida:**
```
======================================================================
  👤  ✅ VOZ HUMANA DETECTADA
======================================================================

📊 Probabilidades:
   🧑 Humano:    98.7% ████████████████████████████████████████
   🤖 Deepfake:   1.3% ▌

🎯 Confianza: 98.7%
```

#### Modo Batch (Archivos)

```bash
python src/realtime/realtime_detection.py --files audio1.wav audio2.wav
```

## 📁 Estructura del Proyecto

```
spoofing-recognition/
├── src/
│   ├── models/              # Arquitectura AASIST
│   ├── training/            # Scripts de fine-tuning
│   ├── evaluation/          # Evaluación de modelos
│   ├── realtime/            # Detección en tiempo real
│   └── data_collection/     # Generación de datasets
├── config/                  # Configuraciones
├── data/                    # Datasets (no incluidos en repo)
├── models/                  # Modelos (no incluidos en repo)
├── notebooks/               # Jupyter notebooks
├── docs/                    # Documentación
├── requirements.txt         # Dependencias
└── README.md
```

## 🎓 Fine-Tuning

### 1. Preparar Dataset

```bash
# Opción A: Generar muestras TTS
python src/data_collection/generate_elevenlabs_samples.py
python src/data_collection/generate_linux_tts.py

# Opción B: Grabar voz humana
python src/data_collection/record_human_samples.py
```

### 2. Crear Metadata

```bash
python src/data_collection/create_metadata_csv.py --output data/metadata_all.csv
```

### 3. Convertir Audio

```bash
python src/data_collection/convert_to_standard_format.py \
    --csv data/metadata_all.csv \
    --output_dir data/processed
```

### 4. Fine-Tuning

```bash
python src/training/train_aasist.py \
    --csv data/metadata_processed.csv \
    --pretrained models/AASIST/models/weights/AASIST.pth \
    --output_dir models/aasist_fine_tuned \
    --epochs 20 \
    --lr 0.001
```

**Curva de Aprendizaje:**
- Epoch 1: Train 64.9% → Dev 62.5%
- Epoch 2: Train 67.5% → Dev **100%** ✨
- Epoch 7: Train **100%** → Dev 100%
- Epochs 8-15: Consolidación (100% mantenido)

## 🎤 Uso Avanzado

### Opciones del Detector

```bash
# Grabaciones más largas
python src/realtime/realtime_detection.py --duration 5

# Guardar muestras grabadas
python src/realtime/realtime_detection.py --save

# Usar GPU
python src/realtime/realtime_detection.py --device cuda

# Analizar carpeta completa
python src/realtime/realtime_detection.py --files data/audio/*.wav
```

### Evaluación de Modelos

```bash
# Evaluar modelo pre-entrenado
python src/evaluation/evaluate_pretrained.py \
    --model models/AASIST/models/weights/AASIST.pth \
    --csv data/metadata_processed.csv

# Evaluar modelo fine-tuned
python src/evaluation/evaluate_pretrained.py \
    --model models/aasist_fine_tuned/best_model.pth \
    --csv data/metadata_processed.csv
```

## 📋 Requisitos

### Dependencias Principales

- Python 3.12+
- PyTorch 2.9.1+
- librosa 0.10.2+
- sounddevice 0.5.3+
- soundfile 0.12.1+
- numpy, pandas, tqdm

### Hardware

- **Mínimo**: CPU (funciona perfectamente)
- **Recomendado**: GPU NVIDIA con CUDA (para training más rápido)
- **RAM**: 8GB mínimo, 16GB recomendado
- **Disco**: 2GB para código + modelos

### Audio

- **Sample Rate**: 16 kHz
- **Canales**: Mono
- **Formato**: WAV PCM 16-bit
- **Duración**: 3-5 segundos recomendado

## 🔬 Metodología

### Dataset

| Tipo | Cantidad | Fuente |
|------|----------|--------|
| Bonafide (Humano) | 77 | Grabaciones personales (Germán) |
| Spoof (ElevenLabs) | 97 | TTS Colombiana/Peruana Mujer |
| Spoof (Linux TTS) | 50 | espeak con variaciones |
| **Total** | **222** | - |

**Splits:**
- Train: 154 muestras (69.4%)
- Dev: 32 muestras (14.4%)
- Test: 36 muestras (16.2%)

### Entrenamiento

**Configuración:**
- Optimizer: Adam
- Learning Rate: 0.001 (10x mayor que original)
- Loss: BCEWithLogitsLoss (sin feat_loss)
- Batch Size: 8
- Epochs: 15-20
- Device: CPU

**Mejoras Implementadas:**
1. ✅ Eliminación del feat_loss (interferencia en fine-tuning)
2. ✅ Learning rate aumentado 10x (0.0001 → 0.001)
3. ✅ Agregación de output multi-dimensional
4. ✅ Strict=False en carga de pesos

## 📖 Documentación Adicional

- [QUICKSTART.md](QUICKSTART.md) - Inicio rápido
- [COMMANDS.md](COMMANDS.md) - Comandos útiles
- [REALTIME_GUIDE.md](REALTIME_GUIDE.md) - Guía detallada de detección en tiempo real
- [QUICKSTART_REALTIME.md](QUICKSTART_REALTIME.md) - Guía rápida de tiempo real

## 🛠️ Desarrollo

### Configurar Entorno de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Ejecutar tests (si existen)
pytest tests/

# Formatear código
black src/
```

### Contribuir

1. Fork del proyecto
2. Crear branch (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -am 'Añadir mejora'`)
4. Push al branch (`git push origin feature/mejora`)
5. Crear Pull Request

## 🐛 Solución de Problemas

### Error de Micrófono

```bash
# Listar dispositivos de audio
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Modelo No Carga

```bash
# Verificar estructura
ls -lh models/AASIST/models/weights/AASIST.pth
ls -lh models/aasist_fine_tuned/best_model.pth
```

### Baja Confianza en Predicciones

- Verifica calidad del audio (16kHz, mono, WAV)
- Aumenta duración de grabación: `--duration 5`
- Graba en ambiente silencioso
- Asegúrate de usar el modelo fine-tuned

## 📚 Referencias

### Paper Original

```bibtex
@inproceedings{jung2022aasist,
  title={AASIST: Audio Anti-Spoofing using Integrated Spectro-Temporal Graph Attention Networks},
  author={Jung, Jee-weon and Heo, Hee-Soo and Tak, Hemlata and Shim, Hye-jin and Chung, Joon Son and Lee, Bong-Jin and Yu, Ha-Jin and Evans, Nicholas},
  booktitle={ICASSP 2022-2022 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages={6367--6371},
  year={2022},
  organization={IEEE}
}
```

### Repositorio Original

- [clovaai/aasist](https://github.com/clovaai/aasist)
- [ASVspoof 2021 Dataset](https://www.asvspoof.org/)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

El modelo AASIST original está bajo licencia MIT de NAVER Corp.

## 👤 Autor

**Germán (Dreiko98)**

- GitHub: [@Dreiko98](https://github.com/Dreiko98)
- Proyecto: [spoofing-recognition](https://github.com/Dreiko98/spoofing-recognition)

## 🙏 Agradecimientos

- NAVER Corp. por el modelo AASIST original
- ASVspoof Challenge por los datasets
- ElevenLabs por el API de TTS
- Comunidad de PyTorch

## 📈 Roadmap

- [x] Fine-tuning exitoso (100% accuracy)
- [x] Detección en tiempo real
- [x] Modo batch
- [ ] Interfaz web (Gradio/Streamlit)
- [ ] API REST para detección
- [ ] Soporte para más idiomas
- [ ] Modelo cuantizado (menor tamaño)
- [ ] App móvil

## 💡 Casos de Uso

1. **Verificación de Identidad por Voz**
2. **Detección de Fraude Telefónico**
3. **Validación de Audios en Redes Sociales**
4. **Forense Digital**
5. **Control de Calidad en Call Centers**

---

**⭐ Si te resultó útil este proyecto, considera darle una estrella!**

**🐛 Encontraste un bug? [Abre un issue](https://github.com/Dreiko98/spoofing-recognition/issues)**

**💬 ¿Preguntas? [Inicia una discusión](https://github.com/Dreiko98/spoofing-recognition/discussions)**
