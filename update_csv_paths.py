#!/usr/bin/env python3
"""Actualiza las rutas del CSV para apuntar a archivos procesados"""

import pandas as pd
from pathlib import Path

# Leer CSV original
df = pd.read_csv('data/metadata_all.csv')

print("=" * 70)
print("         🔄 ACTUALIZANDO RUTAS A ARCHIVOS PROCESADOS")
print("=" * 70)
print()

# Actualizar rutas: data/raw -> data/processed y cambiar extensión a .wav
df['filepath_original'] = df['filepath']
df['filepath'] = df['filepath'].str.replace('data/raw/', 'data/processed/', regex=False)
df['filepath'] = df['filepath'].str.replace('.mp3', '.wav', regex=False)

# Verificar que los archivos existen
missing = []
for idx, row in df.iterrows():
    if not Path(row['filepath']).exists():
        missing.append(row['filepath'])

if missing:
    print(f"⚠️  {len(missing)} archivos no encontrados:")
    for f in missing[:5]:
        print(f"   - {f}")
    if len(missing) > 5:
        print(f"   ... y {len(missing) - 5} más")
else:
    print(f"✅ Todos los {len(df)} archivos existen en data/processed")

# Guardar CSV actualizado
output_path = 'data/metadata_processed.csv'
df_final = df[['filepath', 'label', 'source', 'tts_engine', 'text', 'split']]
df_final.to_csv(output_path, index=False)

print()
print("=" * 70)
print(f"✅ CSV actualizado guardado en: {output_path}")
print("=" * 70)
print()
print("📊 Resumen:")
print(f"   Total de muestras: {len(df)}")
print(f"   Bonafide: {len(df[df['label'] == 'bonafide'])}")
print(f"   Spoof: {len(df[df['label'] == 'spoof'])}")
print()
print("📂 Splits:")
for split in ['train', 'dev', 'test']:
    count = len(df[df['split'] == split])
    print(f"   {split}: {count} muestras")
print()
print("=" * 70)
print("🎯 TODO LISTO PARA ENTRENAR!")
print("=" * 70)
