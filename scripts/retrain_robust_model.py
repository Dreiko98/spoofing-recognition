#!/usr/bin/env python3
"""
Script completo para re-entrenar modelo robusto

Automatiza:
1. Segmentación de podcast
2. Generación de TTS equivalente
3. Creación de metadata combinada
4. Conversión a formato estándar
5. Re-entrenamiento
6. Validación
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse

def run_command(cmd, description):
    """Ejecuta comando y muestra progreso"""
    print("\n" + "="*70)
    print(f"  {description}")
    print("="*70)
    print(f"Comando: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ Error en: {description}")
        return False
    
    print(f"\n✅ Completado: {description}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Re-entrena modelo con datos de podcast')
    parser.add_argument('--podcast', type=str, required=True,
                        help='Path al archivo de podcast (MP3, WAV, etc.)')
    parser.add_argument('--segments', type=int, default=150,
                        help='Número de segmentos a extraer del podcast (default: 150)')
    parser.add_argument('--tts_samples', type=int, default=200,
                        help='Número de muestras TTS nuevas a generar (default: 200)')
    parser.add_argument('--epochs', type=int, default=20,
                        help='Épocas de entrenamiento (default: 20)')
    parser.add_argument('--skip_segment', action='store_true',
                        help='Saltar segmentación (usar segmentos existentes)')
    parser.add_argument('--skip_tts', action='store_true',
                        help='Saltar generación de TTS')
    parser.add_argument('--skip_training', action='store_true',
                        help='Solo preparar datos, no entrenar')
    
    args = parser.parse_args()
    
    print("="*70)
    print("  🚀 RE-ENTRENAMIENTO DE MODELO ROBUSTO")
    print("="*70)
    print(f"\n📁 Podcast: {args.podcast}")
    print(f"✂️  Segmentos a extraer: {args.segments}")
    print(f"🤖 Muestras TTS nuevas: {args.tts_samples}")
    print(f"🏋️  Épocas: {args.epochs}")
    
    input("\n⏸️  Presiona ENTER para continuar o Ctrl+C para cancelar...")
    
    # Paso 1: Segmentar podcast
    if not args.skip_segment:
        if not run_command([
            'python', 'src/data_collection/segment_podcast.py',
            args.podcast,
            '--duration', '3',
            '--max_segments', str(args.segments),
            '--voice_ratio', '0.7',
            '--output', 'data/raw/podcast_segments',
            '--prefix', 'human_podcast'
        ], "📱 PASO 1: Segmentar Podcast"):
            return
    else:
        print("\n⏭️  Saltando segmentación de podcast")
    
    # Paso 2: Generar TTS
    if not args.skip_tts:
        print("\n💡 Nota: Asegúrate de tener ELEVENLABS_API_KEY configurada")
        if not run_command([
            'python', 'src/data_collection/generate_elevenlabs_samples.py',
            '--output_dir', 'data/raw/elevenlabs_extended',
            '--num_samples', str(args.tts_samples),
            '--rate_limit', '1.5'
        ], "🤖 PASO 2: Generar Muestras TTS"):
            print("\n⚠️  Si no tienes API key de ElevenLabs, puedes:")
            print("    - Usar --skip_tts y generar TTS manualmente")
            print("    - Usar solo Linux TTS: python src/data_collection/generate_linux_tts_samples.py")
            return
    else:
        print("\n⏭️  Saltando generación de TTS")
    
    # Paso 3: Crear metadata combinada
    if not run_command([
        'python', 'src/data_collection/create_metadata_csv.py',
        '--output', 'data/metadata_extended.csv'
    ], "📝 PASO 3: Crear Metadata Combinada"):
        return
    
    # Paso 4: Convertir a formato estándar
    if not run_command([
        'python', 'src/data_collection/convert_to_standard_format.py',
        '--csv', 'data/metadata_extended.csv',
        '--output_dir', 'data/processed_extended'
    ], "🔄 PASO 4: Convertir a Formato Estándar"):
        return
    
    # Paso 5: Re-entrenar
    if not args.skip_training:
        if not run_command([
            'python', 'src/training/train_aasist.py',
            '--csv', 'data/metadata_extended.csv',
            '--pretrained', 'models/AASIST/models/weights/AASIST.pth',
            '--output_dir', 'models/aasist_v2_robust',
            '--epochs', str(args.epochs),
            '--lr', '0.001',
            '--batch_size', '8'
        ], f"🏋️  PASO 5: Re-entrenar Modelo ({args.epochs} épocas)"):
            return
    else:
        print("\n⏭️  Saltando entrenamiento")
    
    # Paso 6: Validar
    print("\n" + "="*70)
    print("  ✅ PROCESO COMPLETADO")
    print("="*70)
    print("\n📊 Próximos pasos:")
    print("\n1️⃣  Validar con audios de WhatsApp:")
    print("    python src/data_collection/test_whatsapp_audios.py")
    print("\n2️⃣  Comparar modelos:")
    print("    python src/evaluation/compare_models.py")
    print("\n3️⃣  Probar en tiempo real:")
    print("    python src/realtime/realtime_detection.py \\")
    print("        --model models/aasist_v2_robust/best_model.pth")
    print()

if __name__ == '__main__':
    main()
