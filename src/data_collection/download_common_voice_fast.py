#!/usr/bin/env python3
"""Descarga muestras de Common Voice usando HuggingFace Datasets (RÁPIDO)"""

import argparse
import json
from pathlib import Path
from datasets import load_dataset
import soundfile as sf


def main():
    parser = argparse.ArgumentParser(description='Descargar muestras de Common Voice')
    parser.add_argument('--num_samples', type=int, default=100,
                        help='Número de muestras a descargar')
    parser.add_argument('--output_dir', type=str, default='data/raw/human',
                        help='Directorio de salida')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("    🤗 DESCARGA DE COMMON VOICE (Método HuggingFace - RÁPIDO)")
    print("=" * 70)
    print()
    print("📥 Conectando a HuggingFace...")
    print("   Dataset: Common Voice 13.0 (Español)")
    print(f"   Muestras: {args.num_samples}")
    print()

    # Cargar dataset en modo streaming (no descarga todo, solo lo necesario)
    print("🔄 Cargando dataset en modo streaming...")
    dataset = load_dataset(
        "mozilla-foundation/common_voice_13_0",
        "es",
        split="validated",
        streaming=True,
        trust_remote_code=True
    )

    metadata = []
    print(f"\n📋 Descargando y procesando {args.num_samples} muestras...")
    print("   (Esto puede tardar 2-5 minutos dependiendo de tu conexión)")
    print()

    for i, sample in enumerate(dataset.take(args.num_samples)):
        try:
            # Obtener audio
            audio_data = sample['audio']
            
            # Nombre de archivo
            filename = f"human_commonvoice_{i:05d}.wav"
            audio_path = output_dir / filename
            
            # Guardar como WAV
            sf.write(
                str(audio_path),
                audio_data['array'],
                audio_data['sampling_rate']
            )
            
            # Guardar metadata
            metadata.append({
                'filename': filename,
                'text': sample['sentence'],
                'speaker_id': sample.get('client_id', f'speaker_{i}'),
                'source': 'common_voice',
                'gender': sample.get('gender', 'unknown'),
                'age': sample.get('age', 'unknown'),
                'accent': sample.get('accent', 'unknown'),
            })
            
            # Progreso
            if (i + 1) % 10 == 0 or i == 0:
                print(f"   ✅ {i + 1}/{args.num_samples} muestras procesadas...")
        
        except Exception as e:
            print(f"   ⚠️  Error en muestra {i}: {e}")
            continue

    # Guardar metadata
    metadata_path = output_dir / 'metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"✅ {len(metadata)} muestras descargadas exitosamente")
    print(f"{'=' * 70}")
    print(f"\n📁 Audios guardados en: {output_dir}")
    print(f"📄 Metadata guardada en: {metadata_path}")
    
    # Estadísticas
    genders = {}
    for m in metadata:
        gender = m.get('gender', 'unknown')
        genders[gender] = genders.get(gender, 0) + 1
    
    print(f"\n📊 Distribución de género:")
    for gender, count in sorted(genders.items()):
        print(f"   {gender}: {count} muestras")
    
    print(f"\n{'=' * 70}")
    print("🎯 Próximo paso: Actualizar el CSV de metadata")
    print()
    print("   python src/data_collection/create_metadata_csv.py \\")
    print("       --output data/metadata_all.csv")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
