#!/usr/bin/env python3
"""
Script para generar nuevas muestras de ElevenLabs para validación
"""

import os
import json
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import save

def main():
    # Configuración
    output_dir = Path("data/test_validation/elevenlabs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # API Key (asegúrate de tenerla en variable de entorno)
    api_key = "2e180d88ba9986b26f37c8d1c7ef246f21b4f193fde6c031af2d4d49d5089638"
    if not api_key:
        print("❌ Error: No se encontró ELEVENLABS_API_KEY")
        print("💡 Exporta tu API key: export ELEVENLABS_API_KEY='tu_key_aqui'")
        return
    
    client = ElevenLabs(api_key=api_key)
    
    # Nuevas frases diferentes a las del entrenamiento
    frases_nuevas = [
        "Bienvenido al sistema de detección de deepfakes de audio",
        "Esta tecnología puede identificar voces sintéticas en tiempo real",
        "La seguridad de las comunicaciones es fundamental en la era digital",
        "Los asistentes virtuales utilizan síntesis de voz avanzada",
        "La autenticación por voz está revolucionando la ciberseguridad"
    ]
    
    # Voces públicas estándar de ElevenLabs (funcionan sin cuenta premium)
    voces = [
        "EXAVITQu4vr4xnSDxMaL",  # Bella (Mujer - Americano)
        "21m00Tcm4TlvDq8ikWAM",  # Rachel (Mujer - Americano)
    ]
    
    nombres_voces = ["bella", "rachel"]
    
    print("=" * 70)
    print("  🤖 GENERACIÓN DE MUESTRAS ELEVENLABS PARA VALIDACIÓN")
    print("=" * 70)
    print(f"\n📝 Generando {len(frases_nuevas)} frases nuevas")
    print(f"🎭 Usando {len(voces)} voces diferentes")
    print(f"📁 Output: {output_dir}\n")
    
    metadata = []
    count = 0
    
    for i, frase in enumerate(frases_nuevas, 1):
        # Alternar entre las dos voces
        voz_idx = (i - 1) % len(voces)
        voice_id = voces[voz_idx]
        voice_name = nombres_voces[voz_idx]
        
        print(f"[{i}/{len(frases_nuevas)}] Generando con voz {voice_name}...")
        print(f'   "{frase[:50]}..."')
        
        try:
            # Generar audio con la nueva API
            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                text=frase,
                model_id="eleven_flash_v2_5"
            )
            
            # Guardar
            filename = f"elevenlabs_validation_{i:02d}_{voice_name}.mp3"
            filepath = output_dir / filename
            save(audio, str(filepath))
            
            print(f"   ✅ Guardado: {filename}\n")
            
            metadata.append({
                "filename": filename,
                "text": frase,
                "voice": voice_name,
                "voice_id": voice_id
            })
            
            count += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            continue
    
    # Guardar metadata
    metadata_file = output_dir / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("=" * 70)
    print("  ✅ GENERACIÓN COMPLETADA")
    print("=" * 70)
    print(f"\n📊 Muestras generadas: {count}/{len(frases_nuevas)}")
    print(f"📁 Archivos en: {output_dir}")
    print(f"📝 Metadata: {metadata_file}")
    
    print("\n💡 Próximo paso:")
    print("   python src/data_collection/test_new_samples.py")

if __name__ == '__main__':
    main()
