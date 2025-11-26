#!/usr/bin/env python3
"""
Analizar resultados de batch con diferentes umbrales
"""

import json
from pathlib import Path

# Leer último resultado
result_files = sorted(Path(".").glob("batch_results_*.json"))
if not result_files:
    print("No se encontraron archivos de resultados")
    exit(1)

latest_result = result_files[-1]
print(f"📊 Analizando: {latest_result}\n")

with open(latest_result, 'r') as f:
    results = json.load(f)

print("=" * 70)
print("  🔍 ANÁLISIS CON DIFERENTES UMBRALES")
print("=" * 70)

# Probar diferentes umbrales
umbrales = [0.50, 0.60, 0.70, 0.75, 0.80]

for umbral in umbrales:
    print(f"\n📊 Umbral: {umbral:.0%} (>= {umbral:.0%} = DEEPFAKE)")
    print("-" * 70)
    
    humanos_detectados = 0
    deepfakes_detectados = 0
    
    for result in results:
        filename = result['filename']
        prob_deepfake = result['prob_deepfake']
        
        # Clasificar con este umbral
        es_deepfake = prob_deepfake >= umbral
        
        if es_deepfake:
            deepfakes_detectados += 1
            emoji = "🤖"
        else:
            humanos_detectados += 1
            emoji = "👤"
        
        print(f"  {emoji} {filename:40s} → {prob_deepfake:.2%}")
    
    print(f"\n  ✅ HUMANOS:   {humanos_detectados}/{len(results)} ({humanos_detectados/len(results)*100:.1f}%)")
    print(f"  ⚠️  DEEPFAKES: {deepfakes_detectados}/{len(results)} ({deepfakes_detectados/len(results)*100:.1f}%)")

print("\n" + "=" * 70)
print("💡 RECOMENDACIÓN:")
print("=" * 70)
print("""
Para audios de WhatsApp (comprimidos), usar umbral más alto:
• Umbral 70%: Más permisivo con compresión
• Umbral 80%: Solo clasificar como deepfake si hay alta certeza

Para audios de alta calidad (WAV sin compresión):
• Umbral 50%: Funciona bien
""")
