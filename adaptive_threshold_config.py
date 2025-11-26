"""
Configuración de umbrales adaptativos según tipo de audio
"""

UMBRALES = {
    # Para audios de alta calidad (grabados directamente, sin compresión)
    'high_quality': {
        'threshold': 0.50,  # 50%
        'description': 'Audios WAV grabados directamente, sin compresión',
        'use_cases': ['Grabaciones de micrófono', 'Archivos WAV/FLAC', 'Audio profesional']
    },
    
    # Para audios comprimidos (WhatsApp, llamadas, streaming)
    'compressed': {
        'threshold': 0.70,  # 70%
        'description': 'Audios con compresión lossy (WhatsApp, MP3, llamadas)',
        'use_cases': ['WhatsApp', 'Telegram', 'Llamadas telefónicas', 'MP3', 'Streaming']
    },
    
    # Modo conservador (solo clasificar como deepfake si hay alta certeza)
    'conservative': {
        'threshold': 0.80,  # 80%
        'description': 'Modo conservador - evitar falsos positivos',
        'use_cases': ['Aplicaciones críticas', 'Verificación de identidad']
    }
}

# Interpretación de confianza
CONFIDENCE_LEVELS = {
    'very_high': (0.90, 1.00),   # 90-100%: Muy alta certeza
    'high': (0.75, 0.90),        # 75-90%: Alta certeza
    'moderate': (0.60, 0.75),    # 60-75%: Certeza moderada
    'low': (0.50, 0.60),         # 50-60%: Baja certeza (zona gris)
    'very_low': (0.00, 0.50),    # 0-50%: Muy baja certeza
}

def get_recommendation(prob_deepfake, audio_type='high_quality'):
    """
    Obtiene recomendación basada en probabilidad y tipo de audio
    
    Args:
        prob_deepfake: Probabilidad de ser deepfake (0-1)
        audio_type: 'high_quality', 'compressed', o 'conservative'
    
    Returns:
        dict con predicción y nivel de confianza
    """
    threshold = UMBRALES[audio_type]['threshold']
    is_deepfake = prob_deepfake >= threshold
    confidence = abs(prob_deepfake - 0.5) * 2  # 0 = indeciso, 1 = muy seguro
    
    # Determinar nivel de confianza
    conf_level = 'very_low'
    for level, (min_val, max_val) in CONFIDENCE_LEVELS.items():
        if min_val <= prob_deepfake < max_val:
            conf_level = level
            break
    
    return {
        'is_deepfake': is_deepfake,
        'label': 'DEEPFAKE' if is_deepfake else 'HUMANO',
        'probability': prob_deepfake,
        'confidence_level': conf_level,
        'threshold_used': threshold,
        'audio_type': audio_type,
        'recommendation': _get_action_recommendation(is_deepfake, conf_level, prob_deepfake, threshold)
    }

def _get_action_recommendation(is_deepfake, conf_level, prob, threshold):
    """Genera recomendación de acción"""
    if prob < threshold - 0.10:  # Claramente humano
        return "✅ Audio genuino - Proceder con confianza"
    elif prob > threshold + 0.10:  # Claramente deepfake
        return "⚠️ Posible deepfake - Revisar o rechazar"
    else:  # Zona gris
        return "🔍 Zona gris - Revisar manualmente o solicitar otra muestra"

# Ejemplo de uso
if __name__ == '__main__':
    # Audios de WhatsApp del test
    whatsapp_probs = [0.5168, 0.5047, 0.5203, 0.8640, 0.6716, 0.5082]
    
    print("=" * 70)
    print("  🎯 RECOMENDACIONES POR TIPO DE AUDIO")
    print("=" * 70)
    
    for i, prob in enumerate(whatsapp_probs, 1):
        print(f"\n📱 WhatsApp Audio {i} (prob: {prob:.2%})")
        print("-" * 70)
        
        # Probar diferentes configuraciones
        for audio_type in ['high_quality', 'compressed', 'conservative']:
            result = get_recommendation(prob, audio_type)
            print(f"  {audio_type:15s} → {result['label']:10s} | {result['recommendation']}")
