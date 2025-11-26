#!/usr/bin/env python3
"""Convertidor de audio a formato estándar para AASIST

Convierte audios de cualquier formato a:
- WAV PCM 16-bit
- 16 kHz
- mono

Uso:
    # Convertir una carpeta completa
    python convert_to_standard_format.py --input_dir data/raw/siri --output_dir data/processed/siri

    # Convertir un archivo individual
    python convert_to_standard_format.py --input_file audio.mp3 --output_file audio_16k.wav

Requiere: pip install librosa soundfile
"""

import argparse
from pathlib import Path
import librosa
import soundfile as sf
from tqdm import tqdm


TARGET_SR = 16000  # 16 kHz


def convert_audio_file(input_path, output_path, target_sr=TARGET_SR):
    """Convierte un archivo de audio al formato estándar
    
    Args:
        input_path: ruta del archivo de entrada
        output_path: ruta del archivo de salida
        target_sr: sample rate objetivo (por defecto 16000)
    
    Returns:
        True si la conversión fue exitosa, False en caso contrario
    """
    try:
        # Cargar audio
        audio, sr = librosa.load(input_path, sr=None, mono=False)
        
        # Convertir a mono si es necesario
        if audio.ndim > 1:
            audio = librosa.to_mono(audio)
        
        # Resamplear si es necesario
        if sr != target_sr:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
        
        # Normalizar a [-1, 1] si está fuera de rango
        if audio.max() > 1.0 or audio.min() < -1.0:
            audio = audio / max(abs(audio.max()), abs(audio.min()))
        
        # Guardar como WAV PCM 16-bit
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, audio, target_sr, subtype='PCM_16')
        
        return True
    
    except Exception as e:
        print(f"Error procesando {input_path}: {e}")
        return False


def convert_directory(input_dir, output_dir, target_sr=TARGET_SR, recursive=True):
    """Convierte todos los archivos de audio en un directorio
    
    Args:
        input_dir: directorio de entrada
        output_dir: directorio de salida
        target_sr: sample rate objetivo
        recursive: si True, procesa subdirectorios recursivamente
    
    Returns:
        tuple (exitosos, fallidos)
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    # Extensiones de audio soportadas
    audio_extensions = {'.wav', '.mp3', '.flac', '.aiff', '.aif', '.m4a', '.ogg'}
    
    # Buscar archivos
    if recursive:
        audio_files = [f for f in input_dir.rglob('*') if f.suffix.lower() in audio_extensions]
    else:
        audio_files = [f for f in input_dir.glob('*') if f.suffix.lower() in audio_extensions]
    
    if not audio_files:
        print(f"No se encontraron archivos de audio en {input_dir}")
        return 0, 0
    
    print(f"Encontrados {len(audio_files)} archivos de audio")
    print(f"Convirtiendo a formato estándar (WAV 16kHz mono)...\n")
    
    successful = 0
    failed = 0
    
    for input_path in tqdm(audio_files, desc="Procesando"):
        # Mantener estructura de subdirectorios si es recursivo
        if recursive:
            rel_path = input_path.relative_to(input_dir)
            output_path = output_dir / rel_path.with_suffix('.wav')
        else:
            output_path = output_dir / input_path.with_suffix('.wav').name
        
        if convert_audio_file(input_path, output_path, target_sr):
            successful += 1
        else:
            failed += 1
    
    return successful, failed


def main():
    parser = argparse.ArgumentParser(
        description='Convertir audio a formato estándar para AASIST (WAV 16kHz mono)'
    )
    
    # Modo archivo individual
    parser.add_argument('--input_file', type=str, help='Archivo de audio de entrada')
    parser.add_argument('--output_file', type=str, help='Archivo de audio de salida')
    
    # Modo directorio
    parser.add_argument('--input_dir', type=str, help='Directorio de entrada')
    parser.add_argument('--output_dir', type=str, help='Directorio de salida')
    parser.add_argument('--recursive', action='store_true', default=True,
                        help='Procesar subdirectorios recursivamente')
    
    # Parámetros
    parser.add_argument('--target_sr', type=int, default=TARGET_SR,
                        help=f'Sample rate objetivo (por defecto {TARGET_SR})')
    
    args = parser.parse_args()
    
    # Modo archivo individual
    if args.input_file and args.output_file:
        input_path = Path(args.input_file)
        output_path = Path(args.output_file)
        
        if not input_path.exists():
            print(f"ERROR: {input_path} no existe")
            return
        
        print(f"Convirtiendo {input_path} -> {output_path}")
        if convert_audio_file(input_path, output_path, args.target_sr):
            print("✅ Conversión exitosa")
        else:
            print("❌ Error en la conversión")
        return
    
    # Modo directorio
    if args.input_dir and args.output_dir:
        input_dir = Path(args.input_dir)
        output_dir = Path(args.output_dir)
        
        if not input_dir.exists():
            print(f"ERROR: {input_dir} no existe")
            return
        
        successful, failed = convert_directory(
            input_dir, output_dir, args.target_sr, args.recursive
        )
        
        print(f"\n{'=' * 60}")
        print(f"✅ Exitosos: {successful}")
        print(f"❌ Fallidos: {failed}")
        print(f"📁 Archivos guardados en: {output_dir}")
        print("=" * 60)
        return
    
    # Si no se especificó ningún modo
    print("ERROR: Debes especificar --input_file/--output_file o --input_dir/--output_dir")
    parser.print_help()


if __name__ == '__main__':
    main()
