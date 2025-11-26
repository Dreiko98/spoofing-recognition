#!/usr/bin/env python3
"""Crea el archivo metadata CSV consolidado para entrenamiento de AASIST

Este script:
1. Lee los metadatos JSON de cada fuente (ElevenLabs, Linux TTS, humanas)
2. Convierte los audios al formato estándar (WAV 16kHz mono)
3. Genera el CSV con formato: filepath,label,source,tts_engine,text,split

Uso:
    python create_metadata_csv.py --output data/metadata_all.csv
"""

import argparse
import json
import pandas as pd
from pathlib import Path
import random


def load_elevenlabs_metadata(base_dir='data/raw'):
    """Carga metadata de todas las carpetas de ElevenLabs"""
    base_path = Path(base_dir)
    records = []
    
    # Buscar todas las carpetas que contienen muestras de ElevenLabs
    elevenlabs_dirs = list(base_path.glob('elevenlabs*'))
    
    for elev_dir in elevenlabs_dirs:
        metadata_file = elev_dir / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item in data:
                # Convertir a formato CSV
                filename = item['filename']
                # Ruta relativa al directorio de datos
                filepath = str(elev_dir / filename)
                
                records.append({
                    'filepath': filepath,
                    'label': 'spoof',  # ElevenLabs es sintético
                    'source': 'elevenlabs',
                    'tts_engine': item.get('tts_engine', 'elevenlabs'),
                    'text': item.get('text', ''),
                    'voice_name': item.get('voice_name', ''),
                    'model': item.get('model', ''),
                })
    
    print(f"✅ ElevenLabs: {len(records)} muestras cargadas")
    return records


def load_linux_tts_metadata(base_dir='data/raw/linux_tts'):
    """Carga metadata de Linux TTS (espeak)"""
    base_path = Path(base_dir)
    metadata_file = base_path / 'metadata.json'
    records = []
    
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            filename = item['filename']
            filepath = str(base_path / filename)
            
            records.append({
                'filepath': filepath,
                'label': 'spoof',  # Linux TTS es sintético
                'source': 'linux_tts',
                'tts_engine': item.get('tts_engine', 'espeak'),
                'text': item.get('text', ''),
                'voice_name': item.get('voice', ''),
                'model': 'espeak',
            })
    
    print(f"✅ Linux TTS: {len(records)} muestras cargadas")
    return records


def load_human_metadata(base_dir='data/raw/human'):
    """Carga metadata de grabaciones humanas"""
    base_path = Path(base_dir)
    records = []
    
    # Buscar todos los archivos metadata_*.json en el directorio
    metadata_files = list(base_path.glob('metadata*.json'))
    
    if not metadata_files:
        return records
    
    for metadata_file in metadata_files:
        print(f"📄 Leyendo: {metadata_file.name}")
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            filename = item['filename']
            filepath = str(base_path / filename)
            
            records.append({
                'filepath': filepath,
                'label': 'bonafide',  # Voz humana real
                'source': 'human',
                'tts_engine': 'none',
                'text': item.get('text', item.get('prompt', '')),
                'voice_name': item.get('speaker_id', 'unknown'),
                'model': 'human',
            })
    
    print(f"✅ Humanas: {len(records)} muestras cargadas")
    return records


def assign_splits(df, train_ratio=0.7, dev_ratio=0.15, test_ratio=0.15):
    """Asigna las muestras a train/dev/test de forma balanceada
    
    Args:
        df: DataFrame con las muestras
        train_ratio: proporción para entrenamiento
        dev_ratio: proporción para desarrollo/validación
        test_ratio: proporción para test
    
    Returns:
        DataFrame con columna 'split' añadida
    """
    assert abs(train_ratio + dev_ratio + test_ratio - 1.0) < 0.01, "Ratios deben sumar 1.0"
    
    splits = []
    
    # Asignar splits por label (para mantener balance)
    for label in df['label'].unique():
        label_df = df[df['label'] == label].copy()
        n = len(label_df)
        
        # Calcular índices de corte
        train_end = int(n * train_ratio)
        dev_end = train_end + int(n * dev_ratio)
        
        # Asignar splits
        label_splits = ['train'] * train_end + ['dev'] * (dev_end - train_end) + ['test'] * (n - dev_end)
        
        # Mezclar aleatoriamente
        random.shuffle(label_splits)
        splits.extend(label_splits)
    
    df['split'] = splits
    
    # Mostrar estadísticas
    print("\n📊 Distribución de splits:")
    for split in ['train', 'dev', 'test']:
        split_df = df[df['split'] == split]
        bonafide_count = len(split_df[split_df['label'] == 'bonafide'])
        spoof_count = len(split_df[split_df['label'] == 'spoof'])
        total = len(split_df)
        print(f"  {split:5s}: {total:3d} muestras (bonafide: {bonafide_count:3d}, spoof: {spoof_count:3d})")
    
    return df


def main():
    parser = argparse.ArgumentParser(description='Crear metadata CSV consolidado')
    parser.add_argument('--output', type=str, default='data/metadata_all.csv',
                        help='Ruta del archivo CSV de salida')
    parser.add_argument('--base_dir', type=str, default='data/raw',
                        help='Directorio base con los datos raw')
    parser.add_argument('--train_ratio', type=float, default=0.7,
                        help='Proporción para entrenamiento (default: 0.7)')
    parser.add_argument('--dev_ratio', type=float, default=0.15,
                        help='Proporción para desarrollo (default: 0.15)')
    parser.add_argument('--test_ratio', type=float, default=0.15,
                        help='Proporción para test (default: 0.15)')
    parser.add_argument('--no_shuffle', action='store_true',
                        help='No mezclar aleatoriamente las muestras')
    args = parser.parse_args()

    print("=" * 70)
    print("         📋 CREANDO METADATA CSV CONSOLIDADO")
    print("=" * 70)
    print()

    # Cargar todas las fuentes de datos
    all_records = []
    
    # ElevenLabs
    elevenlabs_records = load_elevenlabs_metadata(args.base_dir)
    all_records.extend(elevenlabs_records)
    
    # Linux TTS
    linux_tts_records = load_linux_tts_metadata(Path(args.base_dir) / 'linux_tts')
    all_records.extend(linux_tts_records)
    
    # Humanas
    human_records = load_human_metadata(Path(args.base_dir) / 'human')
    all_records.extend(human_records)
    
    if not all_records:
        print("\n❌ No se encontraron muestras. Verifica los directorios de datos.")
        return
    
    print(f"\n📦 Total: {len(all_records)} muestras")
    
    # Crear DataFrame
    df = pd.DataFrame(all_records)
    
    # Estadísticas por label
    print("\n📊 Distribución por label:")
    for label in df['label'].unique():
        count = len(df[df['label'] == label])
        print(f"  {label:10s}: {count:3d} muestras")
    
    # Estadísticas por fuente
    print("\n📊 Distribución por fuente:")
    for source in df['source'].unique():
        count = len(df[df['source'] == source])
        print(f"  {source:15s}: {count:3d} muestras")
    
    # Mezclar aleatoriamente (importante para entrenamiento)
    if not args.no_shuffle:
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        print("\n🔀 Muestras mezcladas aleatoriamente")
    
    # Asignar splits
    df = assign_splits(df, args.train_ratio, args.dev_ratio, args.test_ratio)
    
    # Seleccionar columnas finales en el orden correcto
    df_final = df[['filepath', 'label', 'source', 'tts_engine', 'text', 'split']]
    
    # Guardar CSV
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(output_path, index=False)
    
    print(f"\n{'=' * 70}")
    print(f"✅ CSV guardado en: {output_path}")
    print(f"{'=' * 70}")
    print(f"\n📋 Formato del CSV:")
    print(df_final.head(3).to_string(index=False))
    print(f"\n... ({len(df_final)} filas en total)")
    
    # Crear CSV por split (opcional, útil para debugging)
    for split in ['train', 'dev', 'test']:
        split_df = df_final[df_final['split'] == split]
        split_path = output_path.parent / f"metadata_{split}.csv"
        split_df.to_csv(split_path, index=False)
        print(f"  ✅ {split_path.name}: {len(split_df)} muestras")
    
    print(f"\n{'=' * 70}")
    print("🎯 Próximo paso: Convertir audios a formato estándar (WAV 16kHz mono)")
    print("   Comando:")
    print("   python src/data_collection/convert_to_standard_format.py \\")
    print(f"       --csv {output_path} \\")
    print("       --output_dir data/processed")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
