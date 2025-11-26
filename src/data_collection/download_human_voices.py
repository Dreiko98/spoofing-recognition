#!/usr/bin/env python3
"""Descarga muestras de voz humana de datasets públicos (SIMPLIFICADO)

Usa VoxPopuli - dataset de discursos del Parlamento Europeo en español
"""

import argparse
import json
from pathlib import Path
from datasets import load_dataset
import soundfile as sf
from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser(description='Descargar muestras de voz humana')
    parser.add_argument('--num_samples', type=int, default=100,
                        help='Número de muestras a descargar')
    parser.add_argument('--output_dir', type=str, default='data/raw/human',
                        help='Directorio de salida')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("    🎤 DESCARGA DE VOCES HUMANAS - VoxPopuli (Español)")
    print("=" * 70)
    print()
    print("📥 Conectando a HuggingFace...")
    print(f"   Muestras a descargar: {args.num_samples}")
    print()

    try:
        # Intentar con VoxPopuli
        print("🔄 Descargando VoxPopuli (español)...")
        dataset = load_dataset(
            "facebook/voxpopuli",
            "es",
            split="train",
            streaming=True
        )
        
        metadata = []
        print(f"\n📋 Procesando {args.num_samples} muestras...")
        
        with tqdm(total=args.num_samples, desc="Descargando") as pbar:
            for i, sample in enumerate(dataset.take(args.num_samples)):
                try:
                    # Obtener audio
                    audio_data = sample['audio']
                    
                    # Nombre de archivo
                    filename = f"human_voxpopuli_{i:05d}.wav"
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
                        'text': sample.get('normalized_text', sample.get('raw_text', '')),
                        'speaker_id': f"voxpopuli_speaker_{i}",
                        'source': 'voxpopuli',
                        'gender': 'unknown',
                        'age': 'unknown',
                    })
                    
                    pbar.update(1)
                
                except Exception as e:
                    print(f"\n   ⚠️  Error en muestra {i}: {e}")
                    continue

    except Exception as e:
        print(f"\n❌ Error con VoxPopuli: {e}")
        print("\n💡 Probando método alternativo: LibriVox español...")
        
        try:
            dataset = load_dataset(
                "mozilla-foundation/common_voice_11_0",
                "es",
                split="train",
                streaming=True
            )
            
            metadata = []
            print(f"\n📋 Procesando {args.num_samples} muestras...")
            
            with tqdm(total=args.num_samples, desc="Descargando") as pbar:
                for i, sample in enumerate(dataset.take(args.num_samples)):
                    try:
                        audio_data = sample['audio']
                        filename = f"human_cv11_{i:05d}.wav"
                        audio_path = output_dir / filename
                        
                        sf.write(
                            str(audio_path),
                            audio_data['array'],
                            audio_data['sampling_rate']
                        )
                        
                        metadata.append({
                            'filename': filename,
                            'text': sample['sentence'],
                            'speaker_id': sample.get('client_id', f'speaker_{i}'),
                            'source': 'common_voice_11',
                            'gender': sample.get('gender', 'unknown'),
                            'age': sample.get('age', 'unknown'),
                        })
                        
                        pbar.update(1)
                    
                    except Exception as e:
                        print(f"\n   ⚠️  Error en muestra {i}: {e}")
                        continue
        
        except Exception as e2:
            print(f"\n❌ Error con Common Voice 11: {e2}")
            print("\n😞 No se pudo descargar automáticamente.")
            print("\n📝 ALTERNATIVA: Grabar tu propia voz")
            print("   python src/data_collection/record_human_samples.py \\")
            print("       --output_dir data/raw/human \\")
            print("       --num_samples 100")
            return

    # Guardar metadata
    if metadata:
        metadata_path = output_dir / 'metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"\n{'=' * 70}")
        print(f"✅ {len(metadata)} muestras descargadas exitosamente")
        print(f"{'=' * 70}")
        print(f"\n📁 Audios guardados en: {output_dir}")
        print(f"📄 Metadata guardada en: {metadata_path}")
        
        print(f"\n{'=' * 70}")
        print("🎯 Próximo paso: Actualizar el CSV de metadata")
        print()
        print("   python src/data_collection/create_metadata_csv.py \\")
        print("       --output data/metadata_all.csv")
        print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
