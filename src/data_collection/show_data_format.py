#!/usr/bin/env python3
"""Demo visual del formato de datos esperado

Muestra cómo debe verse la estructura de datos antes de entrenar.
No requiere dependencias pesadas, solo muestra ejemplos.
"""

from pathlib import Path


def show_directory_structure():
    """Muestra la estructura de directorios esperada"""
    print("📁 Estructura de datos esperada:")
    print("""
data/
├── raw/                           # Audios originales (cualquier formato)
│   ├── siri/
│   │   ├── siri_es_Monica_00001.aiff
│   │   ├── siri_es_Monica_00002.aiff
│   │   ├── ...
│   │   └── metadata.json
│   ├── elevenlabs/
│   │   ├── elevenlabs_eleven_flash_v2_5_00001.mp3
│   │   ├── elevenlabs_eleven_flash_v2_5_00002.mp3
│   │   ├── ...
│   │   └── metadata.json
│   └── human/
│       ├── human_speaker_1_00001.wav
│       ├── human_speaker_1_00002.wav
│       ├── ...
│       └── metadata_speaker_1.json
│
├── processed/                     # WAV 16kHz mono (listo para entrenar)
│   ├── siri/
│   │   ├── siri_es_Monica_00001.wav
│   │   ├── siri_es_Monica_00002.wav
│   │   └── ...
│   ├── elevenlabs/
│   │   ├── elevenlabs_eleven_flash_v2_5_00001.wav
│   │   ├── elevenlabs_eleven_flash_v2_5_00002.wav
│   │   └── ...
│   └── human/
│       ├── human_speaker_1_00001.wav
│       ├── human_speaker_1_00002.wav
│       └── ...
│
└── metadata/                      # CSVs maestros
    └── metadata_all.csv           # ← El CSV principal para entrenar
    """)


def show_csv_example():
    """Muestra el formato del CSV de metadata"""
    print("\n📄 Formato de metadata_all.csv:")
    print("=" * 100)
    
    csv_header = "filepath,label,source,tts_engine,text,split"
    
    examples = [
        ("data/processed/human/human_speaker_1_00001.wav", "bonafide", "human", "", "Hola, soy una persona real", "train"),
        ("data/processed/human/human_speaker_1_00002.wav", "bonafide", "human", "", "El clima está soleado", "train"),
        ("data/processed/siri/siri_es_Monica_00001.wav", "spoof", "siri", "macos_siri", "Hola, soy Siri", "train"),
        ("data/processed/siri/siri_es_Monica_00002.wav", "spoof", "siri", "macos_siri", "El tiempo está despejado", "dev"),
        ("data/processed/elevenlabs/elevenlabs_eleven_flash_v2_5_00001.wav", "spoof", "elevenlabs", "eleven_flash_v2_5", "Hola desde ElevenLabs", "train"),
        ("data/processed/elevenlabs/elevenlabs_eleven_flash_v2_5_00002.wav", "spoof", "elevenlabs", "eleven_flash_v2_5", "Tu pedido ha llegado", "test"),
    ]
    
    print(csv_header)
    print("-" * 100)
    for row in examples:
        print(','.join(f'"{item}"' if ',' in item or ' ' in item else item for item in row))
    print("=" * 100)


def show_audio_specs():
    """Muestra las especificaciones de audio"""
    print("\n🎵 Especificaciones de audio (archivos en processed/):")
    print("=" * 60)
    print("  Formato:      WAV")
    print("  Codec:        PCM 16-bit")
    print("  Sample rate:  16000 Hz (16 kHz)")
    print("  Canales:      1 (mono)")
    print("  Duración:     Variable (el modelo usa ventanas)")
    print("=" * 60)


def show_label_distribution():
    """Muestra distribución de labels recomendada"""
    print("\n📊 Distribución de labels recomendada:")
    print("=" * 60)
    print("  bonafide (humano):  ~40-50% del dataset")
    print("  spoof (sintético):  ~50-60% del dataset")
    print()
    print("  Dentro de spoof:")
    print("    - Siri:       ~25-30%")
    print("    - ElevenLabs: ~25-30%")
    print("=" * 60)


def show_split_distribution():
    """Muestra distribución de splits"""
    print("\n✂️  Distribución de splits recomendada:")
    print("=" * 60)
    print("  train: 70%  (para entrenar)")
    print("  dev:   15%  (para validar durante entrenamiento)")
    print("  test:  15%  (para evaluación final, nunca visto)")
    print("=" * 60)


def show_dataset_example():
    """Muestra un ejemplo de dataset balanceado"""
    print("\n💡 Ejemplo de dataset balanceado (600 muestras):")
    print("=" * 60)
    
    dataset = {
        "Humano (bonafide)": {
            "train": 210,
            "dev": 45,
            "test": 45,
            "total": 300
        },
        "Siri (spoof)": {
            "train": 105,
            "dev": 22,
            "test": 23,
            "total": 150
        },
        "ElevenLabs (spoof)": {
            "train": 105,
            "dev": 23,
            "test": 22,
            "total": 150
        }
    }
    
    print(f"{'Tipo':<25} {'Train':<10} {'Dev':<10} {'Test':<10} {'Total':<10}")
    print("-" * 60)
    for source, splits in dataset.items():
        print(f"{source:<25} {splits['train']:<10} {splits['dev']:<10} {splits['test']:<10} {splits['total']:<10}")
    
    print("-" * 60)
    total_train = sum(d['train'] for d in dataset.values())
    total_dev = sum(d['dev'] for d in dataset.values())
    total_test = sum(d['test'] for d in dataset.values())
    total_all = sum(d['total'] for d in dataset.values())
    print(f"{'TOTAL':<25} {total_train:<10} {total_dev:<10} {total_test:<10} {total_all:<10}")
    print("=" * 60)


def show_next_steps():
    """Muestra los siguientes pasos"""
    print("\n🚀 Siguientes pasos:")
    print("=" * 60)
    print("1. Generar muestras usando los scripts en src/data_collection/")
    print("   - generate_siri_samples.py (macOS)")
    print("   - generate_elevenlabs_samples.py (requiere API key)")
    print("   - record_human_samples.py (interactivo)")
    print()
    print("2. Convertir a formato estándar:")
    print("   python src/data_collection/convert_to_standard_format.py \\")
    print("       --input_dir data/raw/siri \\")
    print("       --output_dir data/processed/siri")
    print()
    print("3. Crear metadata_all.csv con splits (pendiente: script automático)")
    print()
    print("4. Entrenar:")
    print("   python src/training/train_custom.py")
    print("=" * 60)


def main():
    print("\n" + "=" * 100)
    print(" " * 30 + "🎙️  FORMATO DE DATOS PARA AASIST")
    print("=" * 100)
    
    show_directory_structure()
    show_csv_example()
    show_audio_specs()
    show_label_distribution()
    show_split_distribution()
    show_dataset_example()
    show_next_steps()
    
    print("\n" + "=" * 100)
    print("📚 Para más info:")
    print("   - QUICKSTART.md")
    print("   - src/data_collection/README.md")
    print("   - notebooks/01_data_exploration.ipynb")
    print("=" * 100 + "\n")


if __name__ == '__main__':
    main()
