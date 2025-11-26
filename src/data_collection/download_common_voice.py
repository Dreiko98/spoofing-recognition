#!/usr/bin/env python3
"""Descarga muestras de voz humana de Common Voice (Mozilla)

Common Voice es un dataset público de voces reales en español.
Este script descarga y prepara automáticamente las muestras.

Uso:
    python download_common_voice.py --num_samples 100 --output_dir data/raw/human

Nota: Requiere ~500MB de descarga para el dataset completo de español
"""

import argparse
import json
import os
import random
import shutil
import subprocess
from pathlib import Path
import urllib.request
import tarfile
import csv


# URLs de Common Voice (español)
COMMON_VOICE_ES_URL = "https://mozilla-common-voice-datasets.s3.dualstack.us-west-2.amazonaws.com/cv-corpus-13.0-2023-03-09/cv-corpus-13.0-2023-03-09-es.tar.gz"


def download_file(url, output_path, show_progress=True):
    """Descarga un archivo con barra de progreso"""
    print(f"📥 Descargando desde: {url}")
    print(f"   Destino: {output_path}")
    
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(100, (downloaded / total_size) * 100)
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        if show_progress and block_num % 50 == 0:
            print(f"   Descargado: {mb_downloaded:.1f}MB / {mb_total:.1f}MB ({percent:.1f}%)", end='\r')
    
    try:
        urllib.request.urlretrieve(url, output_path, report_progress)
        print()  # Nueva línea después de la barra de progreso
        print(f"✅ Descarga completada")
        return True
    except Exception as e:
        print(f"\n❌ Error descargando: {e}")
        return False


def extract_tar_gz(tar_path, extract_to):
    """Extrae archivo tar.gz"""
    print(f"📦 Extrayendo {tar_path}...")
    try:
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(path=extract_to)
        print(f"✅ Extracción completada")
        return True
    except Exception as e:
        print(f"❌ Error extrayendo: {e}")
        return False


def load_common_voice_metadata(cv_dir):
    """Carga el metadata de Common Voice"""
    # Buscar el archivo validated.tsv
    validated_file = None
    for root, dirs, files in os.walk(cv_dir):
        if 'validated.tsv' in files:
            validated_file = Path(root) / 'validated.tsv'
            break
    
    if not validated_file or not validated_file.exists():
        print(f"❌ No se encontró validated.tsv en {cv_dir}")
        return None, None
    
    print(f"📄 Leyendo metadata: {validated_file}")
    
    # Leer TSV
    clips_dir = validated_file.parent / 'clips'
    samples = []
    
    with open(validated_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            audio_file = clips_dir / row['path']
            if audio_file.exists():
                samples.append({
                    'path': audio_file,
                    'text': row['sentence'],
                    'age': row.get('age', 'unknown'),
                    'gender': row.get('gender', 'unknown'),
                    'accent': row.get('accent', 'unknown'),
                })
    
    print(f"✅ Encontradas {len(samples)} muestras validadas")
    return samples, clips_dir


def select_diverse_samples(samples, num_samples):
    """Selecciona muestras diversas (diferentes hablantes, géneros, etc.)"""
    # Mezclar y seleccionar
    random.shuffle(samples)
    selected = samples[:num_samples]
    
    # Estadísticas
    genders = {}
    for s in selected:
        gender = s['gender']
        genders[gender] = genders.get(gender, 0) + 1
    
    print(f"\n📊 Distribución de género en las {len(selected)} muestras:")
    for gender, count in genders.items():
        print(f"   {gender}: {count}")
    
    return selected


def main():
    parser = argparse.ArgumentParser(description='Descargar muestras de Common Voice')
    parser.add_argument('--num_samples', type=int, default=100,
                        help='Número de muestras a extraer')
    parser.add_argument('--output_dir', type=str, default='data/raw/human',
                        help='Directorio de salida')
    parser.add_argument('--download_dir', type=str, default='data/downloads',
                        help='Directorio temporal para descargas')
    parser.add_argument('--skip_download', action='store_true',
                        help='Saltar descarga si ya existe')
    parser.add_argument('--cleanup', action='store_true',
                        help='Eliminar archivos temporales después')
    args = parser.parse_args()

    download_dir = Path(args.download_dir)
    output_dir = Path(args.output_dir)
    
    download_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("        📥 DESCARGA DE COMMON VOICE (Voces Humanas)")
    print("=" * 70)
    print()

    # Archivo descargado
    tar_file = download_dir / "common_voice_es.tar.gz"
    extract_dir = download_dir / "common_voice_extracted"

    # Descargar si no existe
    if not tar_file.exists() or not args.skip_download:
        print("⚠️  NOTA: Esta descarga es de ~500MB y puede tardar varios minutos")
        print()
        
        # Opción alternativa: usar datasets de HuggingFace (más rápido)
        print("💡 TIP: Si la descarga es muy lenta, presiona Ctrl+C")
        print("   y usaremos HuggingFace datasets (más rápido)")
        print()
        
        if not download_file(COMMON_VOICE_ES_URL, tar_file):
            print("\n❌ Error en descarga. Probando método alternativo...")
            return try_huggingface_method(args)
    else:
        print(f"✅ Archivo ya descargado: {tar_file}")

    # Extraer
    if not extract_dir.exists():
        if not extract_tar_gz(tar_file, extract_dir):
            return
    else:
        print(f"✅ Ya extraído en: {extract_dir}")

    # Cargar metadata
    samples, clips_dir = load_common_voice_metadata(extract_dir)
    
    if not samples:
        print("❌ No se pudieron cargar las muestras")
        return

    # Seleccionar muestras diversas
    if len(samples) < args.num_samples:
        print(f"⚠️  Solo hay {len(samples)} muestras disponibles (pediste {args.num_samples})")
        args.num_samples = len(samples)
    
    selected_samples = select_diverse_samples(samples, args.num_samples)

    # Copiar archivos y crear metadata
    metadata = []
    print(f"\n📋 Copiando {len(selected_samples)} muestras...")
    
    for i, sample in enumerate(selected_samples):
        # Copiar archivo de audio
        source_path = sample['path']
        filename = f"human_commonvoice_{i:05d}.mp3"
        dest_path = output_dir / filename
        
        shutil.copy2(source_path, dest_path)
        
        metadata.append({
            'filename': filename,
            'text': sample['text'],
            'speaker_id': f"cv_{sample.get('gender', 'unknown')}_{i}",
            'source': 'common_voice',
            'gender': sample.get('gender', 'unknown'),
            'age': sample.get('age', 'unknown'),
            'accent': sample.get('accent', 'unknown'),
        })
        
        if (i + 1) % 20 == 0:
            print(f"   Copiadas {i + 1}/{len(selected_samples)}...")

    # Guardar metadata
    metadata_path = output_dir / 'metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"✅ {len(selected_samples)} muestras descargadas exitosamente")
    print(f"📁 Audios guardados en: {output_dir}")
    print(f"📄 Metadata guardada en: {metadata_path}")
    print(f"{'=' * 70}")

    # Cleanup
    if args.cleanup:
        print(f"\n🧹 Limpiando archivos temporales...")
        shutil.rmtree(extract_dir)
        tar_file.unlink()
        print(f"✅ Limpieza completada")
    else:
        print(f"\n💡 Para eliminar archivos temporales (~500MB), ejecuta:")
        print(f"   rm -rf {download_dir}")

    print(f"\n🎯 Próximo paso: Actualizar el CSV de metadata")
    print(f"   python src/data_collection/create_metadata_csv.py --output data/metadata_all.csv")


def try_huggingface_method(args):
    """Método alternativo usando HuggingFace datasets"""
    print("\n" + "=" * 70)
    print("        🤗 MÉTODO ALTERNATIVO: HUGGINGFACE DATASETS")
    print("=" * 70)
    print()
    
    try:
        from datasets import load_dataset
    except ImportError:
        print("❌ Se requiere instalar: pip install datasets")
        print("\nEjecuta:")
        print("   source .venv/bin/activate")
        print("   pip install datasets")
        return
    
    print("📥 Descargando Common Voice desde HuggingFace...")
    print("   (Esto es más rápido y eficiente)")
    print()
    
    # Cargar dataset
    dataset = load_dataset("mozilla-foundation/common_voice_13_0", "es", split="validated", streaming=True)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    metadata = []
    print(f"📋 Extrayendo {args.num_samples} muestras...")
    
    for i, sample in enumerate(dataset.take(args.num_samples)):
        # Guardar audio
        audio = sample['audio']
        filename = f"human_commonvoice_{i:05d}.mp3"
        audio_path = output_dir / filename
        
        # Guardar array de audio
        import soundfile as sf
        sf.write(audio_path, audio['array'], audio['sampling_rate'])
        
        metadata.append({
            'filename': filename,
            'text': sample['sentence'],
            'speaker_id': f"cv_{sample.get('gender', 'unknown')}_{i}",
            'source': 'common_voice',
            'gender': sample.get('gender', 'unknown'),
            'age': sample.get('age', 'unknown'),
        })
        
        if (i + 1) % 10 == 0:
            print(f"   Procesadas {i + 1}/{args.num_samples}...")
    
    # Guardar metadata
    metadata_path = output_dir / 'metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 70}")
    print(f"✅ {len(metadata)} muestras descargadas exitosamente")
    print(f"📁 Audios guardados en: {output_dir}")
    print(f"📄 Metadata guardada en: {metadata_path}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
