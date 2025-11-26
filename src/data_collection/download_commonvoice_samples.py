#!/usr/bin/env python3
"""Descarga y procesa muestras de Common Voice (Mozilla)

Common Voice es un dataset público de voces humanas en múltiples idiomas.
Este script facilita la descarga y preparación de muestras en español.

Uso:
    1. Descarga el dataset manualmente desde:
       https://commonvoice.mozilla.org/es/datasets
       
    2. Extrae el archivo .tar.gz en data/raw/commonvoice/
    
    3. Ejecuta este script:
       python download_commonvoice_samples.py \\
           --input_dir data/raw/commonvoice/cv-corpus-*-es \\
           --output_dir data/raw/human \\
           --num_samples 100

Requiere: pip install pandas
"""

import argparse
import pandas as pd
from pathlib import Path
import shutil
import random
import json


def extract_commonvoice_samples(cv_dir, output_dir, num_samples=100, split='validated'):
    """Extrae muestras aleatorias de Common Voice
    
    Args:
        cv_dir: directorio con datos de Common Voice (ej: cv-corpus-18.0-2024-06-14/es)
        output_dir: directorio de salida
        num_samples: número de muestras a extraer
        split: split a usar ('train', 'dev', 'test', 'validated', 'other')
    """
    cv_path = Path(cv_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Buscar el archivo TSV
    tsv_file = cv_path / f'{split}.tsv'
    
    if not tsv_file.exists():
        # Intentar con otros nombres comunes
        alternatives = ['validated.tsv', 'train.tsv', 'clips.tsv']
        for alt in alternatives:
            alt_path = cv_path / alt
            if alt_path.exists():
                tsv_file = alt_path
                print(f"ℹ️  Usando {alt} en lugar de {split}.tsv")
                break
    
    if not tsv_file.exists():
        print(f"❌ No se encontró {tsv_file}")
        print(f"Archivos disponibles en {cv_path}:")
        for f in cv_path.glob('*.tsv'):
            print(f"  • {f.name}")
        return False
    
    print(f"📂 Leyendo metadata de: {tsv_file}")
    
    # Leer TSV
    df = pd.read_csv(tsv_file, sep='\t')
    
    print(f"📊 Total de muestras disponibles: {len(df)}")
    
    # Filtrar muestras válidas (con upvotes, sin downvotes)
    if 'up_votes' in df.columns and 'down_votes' in df.columns:
        df_valid = df[(df['up_votes'] >= 2) & (df['down_votes'] == 0)]
        print(f"✅ Muestras validadas: {len(df_valid)}")
    else:
        df_valid = df
    
    # Seleccionar muestras aleatorias
    if len(df_valid) < num_samples:
        print(f"⚠️  Solo hay {len(df_valid)} muestras disponibles, usando todas")
        selected = df_valid
    else:
        selected = df_valid.sample(n=num_samples, random_state=42)
    
    print(f"\n🎯 Extrayendo {len(selected)} muestras...")
    
    # Directorio de clips
    clips_dir = cv_path / 'clips'
    
    if not clips_dir.exists():
        print(f"❌ No se encontró el directorio de clips: {clips_dir}")
        return False
    
    metadata = []
    successful = 0
    
    for idx, row in selected.iterrows():
        clip_filename = row['path']
        clip_path = clips_dir / clip_filename
        
        if not clip_path.exists():
            print(f"  ⚠️  Audio no encontrado: {clip_filename}")
            continue
        
        # Nuevo nombre para el archivo
        new_filename = f"human_commonvoice_{successful:05d}.mp3"
        output_file = output_path / new_filename
        
        # Copiar archivo
        shutil.copy2(clip_path, output_file)
        
        # Guardar metadata
        metadata.append({
            'filename': new_filename,
            'text': row.get('sentence', ''),
            'speaker_id': row.get('client_id', 'unknown'),
            'age': row.get('age', ''),
            'gender': row.get('gender', ''),
            'accent': row.get('accent', ''),
            'source': 'commonvoice'
        })
        
        successful += 1
        
        if successful % 10 == 0:
            print(f"  ✅ Copiadas {successful}/{len(selected)}...")
    
    # Guardar metadata
    metadata_file = output_path / 'metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 60}")
    print(f"✅ Extraídas {successful} muestras exitosamente")
    print(f"📁 Audios guardados en: {output_path}")
    print(f"📄 Metadata guardada en: {metadata_file}")
    print(f"{'=' * 60}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Extraer muestras de Common Voice')
    parser.add_argument('--input_dir', type=str, required=True,
                        help='Directorio con datos de Common Voice (ej: data/raw/commonvoice/cv-corpus-*-es)')
    parser.add_argument('--output_dir', type=str, default='data/raw/human',
                        help='Directorio de salida')
    parser.add_argument('--num_samples', type=int, default=100,
                        help='Número de muestras a extraer')
    parser.add_argument('--split', type=str, default='validated',
                        choices=['train', 'dev', 'test', 'validated', 'other'],
                        help='Split de Common Voice a usar')
    args = parser.parse_args()

    print("=" * 70)
    print("     📥 EXTRAYENDO MUESTRAS DE COMMON VOICE")
    print("=" * 70)
    print()
    
    success = extract_commonvoice_samples(
        args.input_dir,
        args.output_dir,
        args.num_samples,
        args.split
    )
    
    if success:
        print("\n✨ Siguiente paso: Regenerar el CSV con las nuevas muestras")
        print("   Comando:")
        print("   python src/data_collection/create_metadata_csv.py \\")
        print("       --output data/metadata_all.csv")
    else:
        print("\n❌ No se pudieron extraer las muestras")
        print("\n💡 INSTRUCCIONES PARA DESCARGAR COMMON VOICE:")
        print("   1. Ve a: https://commonvoice.mozilla.org/es/datasets")
        print("   2. Crea una cuenta gratuita")
        print("   3. Descarga el dataset en español (Spanish)")
        print("   4. Extrae el archivo .tar.gz en data/raw/commonvoice/")
        print("   5. Ejecuta este script de nuevo")


if __name__ == '__main__':
    main()
