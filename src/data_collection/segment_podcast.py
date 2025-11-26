#!/usr/bin/env python3
"""
Segmentador de podcast en muestras de entrenamiento

Toma un archivo de audio largo (podcast, audiobook, etc.) y lo segmenta en
pequeños clips de duración fija para usar como datos de entrenamiento.
"""

import os
import sys
from pathlib import Path
import librosa
import soundfile as sf
import numpy as np
from tqdm import tqdm
import argparse

def detect_voice_activity(audio, sr, frame_length=2048, hop_length=512, threshold=0.02):
    """
    Detecta actividad de voz en el audio usando energía
    
    Args:
        audio: Array de audio
        sr: Sample rate
        frame_length: Tamaño de ventana
        hop_length: Salto entre ventanas
        threshold: Umbral de energía para considerar voz
    
    Returns:
        Array booleano indicando frames con voz
    """
    # Calcular energía RMS por frame
    rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
    
    # Frames con energía sobre el umbral
    voice_frames = rms > threshold
    
    return voice_frames

def segment_audio(audio_path, segment_duration=3.0, min_voice_ratio=0.7, 
                  max_segments=None, output_dir="data/podcast_segments",
                  prefix="podcast"):
    """
    Segmenta un audio largo en clips pequeños con voz
    
    Args:
        audio_path: Path al archivo de audio
        segment_duration: Duración de cada segmento en segundos
        min_voice_ratio: Ratio mínimo de voz en el segmento (0.7 = 70% con voz)
        max_segments: Número máximo de segmentos a extraer (None = todos)
        output_dir: Directorio de salida
        prefix: Prefijo para los archivos
    
    Returns:
        Lista de paths de segmentos creados
    """
    print(f"📁 Cargando audio: {audio_path}")
    
    # Cargar audio
    audio, sr = librosa.load(audio_path, sr=16000, mono=True)
    duration_total = len(audio) / sr
    
    print(f"⏱️  Duración total: {duration_total:.1f} segundos ({duration_total/60:.1f} minutos)")
    print(f"📊 Sample rate: {sr} Hz")
    print(f"✂️  Tamaño de segmentos: {segment_duration} segundos")
    print(f"🎤 Umbral de voz mínimo: {min_voice_ratio*100:.0f}%")
    
    # Crear directorio de salida
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Calcular parámetros
    samples_per_segment = int(segment_duration * sr)
    hop_samples = samples_per_segment // 2  # 50% overlap
    
    # Detectar actividad de voz
    print("\n🔍 Detectando actividad de voz...")
    voice_frames = detect_voice_activity(audio, sr)
    
    # Segmentar
    print(f"\n✂️  Segmentando audio...")
    segments_created = []
    segment_count = 0
    
    # Calcular número total de posibles segmentos
    total_possible = (len(audio) - samples_per_segment) // hop_samples + 1
    
    with tqdm(total=total_possible, desc="Procesando") as pbar:
        start_sample = 0
        
        while start_sample + samples_per_segment <= len(audio):
            end_sample = start_sample + samples_per_segment
            segment = audio[start_sample:end_sample]
            
            # Calcular ratio de voz en este segmento
            start_frame = int(start_sample / 512)
            end_frame = int(end_sample / 512)
            segment_voice_frames = voice_frames[start_frame:end_frame]
            voice_ratio = segment_voice_frames.sum() / len(segment_voice_frames) if len(segment_voice_frames) > 0 else 0
            
            # Solo guardar si tiene suficiente voz
            if voice_ratio >= min_voice_ratio:
                # Normalizar volumen
                if segment.max() > 0:
                    segment = segment / segment.max() * 0.9
                
                # Guardar
                segment_filename = f"{prefix}_{segment_count:04d}.wav"
                segment_path = output_path / segment_filename
                sf.write(segment_path, segment, sr)
                
                segments_created.append({
                    'path': str(segment_path),
                    'filename': segment_filename,
                    'duration': segment_duration,
                    'voice_ratio': voice_ratio,
                    'start_time': start_sample / sr,
                    'end_time': end_sample / sr
                })
                
                segment_count += 1
                
                # Límite de segmentos
                if max_segments and segment_count >= max_segments:
                    break
            
            # Avanzar con overlap
            start_sample += hop_samples
            pbar.update(1)
    
    print(f"\n✅ Segmentos creados: {len(segments_created)}")
    print(f"📁 Guardados en: {output_dir}")
    
    # Estadísticas
    if segments_created:
        voice_ratios = [s['voice_ratio'] for s in segments_created]
        print(f"\n📊 Estadísticas:")
        print(f"   • Voice ratio promedio: {np.mean(voice_ratios)*100:.1f}%")
        print(f"   • Voice ratio mínimo: {np.min(voice_ratios)*100:.1f}%")
        print(f"   • Voice ratio máximo: {np.max(voice_ratios)*100:.1f}%")
        print(f"   • Duración total extraída: {len(segments_created) * segment_duration:.1f} segundos")
    
    return segments_created

def create_metadata_csv(segments, output_file="data/podcast_segments/metadata.csv"):
    """Crea CSV con metadata de los segmentos"""
    import pandas as pd
    
    df = pd.DataFrame(segments)
    df['label'] = 'bonafide'  # Todos son humanos
    df['source'] = 'podcast'
    
    df.to_csv(output_file, index=False)
    print(f"\n💾 Metadata guardada en: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Segmenta podcast en clips de entrenamiento',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Segmentar podcast en clips de 3 segundos
  python src/data_collection/segment_podcast.py podcast.mp3 --duration 3

  # Extraer máximo 100 segmentos de 5 segundos
  python src/data_collection/segment_podcast.py podcast.mp3 --duration 5 --max_segments 100

  # Segmentar con ratio de voz más estricto (80%)
  python src/data_collection/segment_podcast.py podcast.mp3 --voice_ratio 0.8

  # Especificar directorio de salida
  python src/data_collection/segment_podcast.py podcast.mp3 --output data/new_humans --prefix human_podcast
        """
    )
    
    parser.add_argument('audio_file', type=str,
                        help='Archivo de audio a segmentar (MP3, WAV, etc.)')
    parser.add_argument('--duration', type=float, default=3.0,
                        help='Duración de cada segmento en segundos (default: 3)')
    parser.add_argument('--voice_ratio', type=float, default=0.7,
                        help='Ratio mínimo de voz en segmento (0-1, default: 0.7)')
    parser.add_argument('--max_segments', type=int, default=None,
                        help='Número máximo de segmentos a extraer (default: todos)')
    parser.add_argument('--output', type=str, default='data/podcast_segments',
                        help='Directorio de salida (default: data/podcast_segments)')
    parser.add_argument('--prefix', type=str, default='podcast',
                        help='Prefijo para archivos (default: podcast)')
    parser.add_argument('--no_metadata', action='store_true',
                        help='No crear archivo metadata.csv')
    
    args = parser.parse_args()
    
    # Verificar que existe el archivo
    if not os.path.exists(args.audio_file):
        print(f"❌ Error: No se encuentra el archivo {args.audio_file}")
        return
    
    print("=" * 70)
    print("  ✂️  SEGMENTADOR DE PODCAST")
    print("=" * 70)
    print()
    
    # Segmentar
    segments = segment_audio(
        audio_path=args.audio_file,
        segment_duration=args.duration,
        min_voice_ratio=args.voice_ratio,
        max_segments=args.max_segments,
        output_dir=args.output,
        prefix=args.prefix
    )
    
    # Crear metadata
    if segments and not args.no_metadata:
        metadata_file = os.path.join(args.output, 'metadata.csv')
        create_metadata_csv(segments, metadata_file)
    
    print("\n" + "=" * 70)
    print("  ✅ SEGMENTACIÓN COMPLETADA")
    print("=" * 70)
    print(f"\n💡 Próximos pasos:")
    print(f"   1. Verifica los segmentos en: {args.output}")
    print(f"   2. Genera muestras TTS equivalentes:")
    print(f"      python src/data_collection/generate_new_elevenlabs_samples.py")
    print(f"   3. Crea metadata combinada:")
    print(f"      python src/data_collection/create_metadata_csv.py")
    print(f"   4. Re-entrena el modelo:")
    print(f"      python src/training/train_aasist.py --csv data/metadata_extended.csv")
    print()

if __name__ == '__main__':
    main()
