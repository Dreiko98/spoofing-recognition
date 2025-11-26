#!/usr/bin/env python3
"""Script de verificación de configuración de ElevenLabs

Verifica que la API key esté configurada y funcione correctamente.
"""

import os
import sys


def check_api_key():
    """Verifica que la API key esté configurada"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    print("=" * 60)
    print("🔑 Verificación de ElevenLabs API Key")
    print("=" * 60)
    
    if not api_key:
        print("\n❌ ERROR: Variable de entorno ELEVENLABS_API_KEY no configurada\n")
        print("Para configurarla:")
        print("  1. Obtén tu API key en: https://elevenlabs.io/app/settings/api-keys")
        print("  2. Exporta la variable:\n")
        print("     export ELEVENLABS_API_KEY='tu_clave_aqui'\n")
        print("  3. Verifica:")
        print("     echo $ELEVENLABS_API_KEY\n")
        return False
    
    print(f"\n✅ API Key configurada: {api_key[:8]}...{api_key[-4:]}")
    print(f"   Longitud: {len(api_key)} caracteres\n")
    
    # Intentar importar cliente
    try:
        from elevenlabs.client import ElevenLabs
        print("✅ Cliente ElevenLabs importado correctamente\n")
        
        # Intentar listar voces
        try:
            client = ElevenLabs(api_key=api_key)
            voices = client.voices.get_all()
            print(f"✅ Conexión exitosa! Encontradas {len(voices.voices)} voces disponibles\n")
            print("Primeras 5 voces:")
            for i, voice in enumerate(voices.voices[:5], 1):
                print(f"  {i}. {voice.name} (ID: {voice.voice_id})")
            print("\n" + "=" * 60)
            print("✅ Todo configurado correctamente!")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"❌ Error al conectar con ElevenLabs API:\n   {e}\n")
            print("Posibles causas:")
            print("  - API key incorrecta o expirada")
            print("  - Sin créditos en la cuenta")
            print("  - Problemas de red")
            return False
            
    except ImportError:
        print("❌ ERROR: Paquete 'elevenlabs' no instalado\n")
        print("Instálalo con:")
        print("  pip install elevenlabs\n")
        return False


def show_usage_examples():
    """Muestra ejemplos de uso"""
    print("\n📚 Ejemplos de uso:")
    print("=" * 60)
    print("\n1. Listar voces disponibles:")
    print("   python3 src/data_collection/generate_elevenlabs_samples.py --list_voices\n")
    print("2. Generar 10 muestras:")
    print("   python3 src/data_collection/generate_elevenlabs_samples.py \\")
    print("       --output_dir data/raw/elevenlabs \\")
    print("       --num_samples 10 \\")
    print("       --rate_limit 1.5\n")
    print("3. Usar una voz específica:")
    print("   python3 src/data_collection/generate_elevenlabs_samples.py \\")
    print("       --output_dir data/raw/elevenlabs \\")
    print("       --num_samples 10 \\")
    print("       --voice_id 2EiwWnXFnvU5JabPnv8n  # Clyde\n")
    print("=" * 60)


if __name__ == '__main__':
    success = check_api_key()
    
    if not success:
        show_usage_examples()
        sys.exit(1)
    else:
        show_usage_examples()
        sys.exit(0)
