#!/bin/bash
# Script de ejemplo para descargar podcast y re-entrenar

echo "======================================================================"
echo "  🎙️  DESCARGA Y RE-ENTRENAMIENTO AUTOMÁTICO"
echo "======================================================================"
echo ""

# URLs de ejemplo de podcasts buenos para entrenamiento
echo "📻 Podcasts recomendados:"
echo ""
echo "1. The Wild Project - Entrevista"
echo "   https://www.youtube.com/watch?v=XXXXXXX"
echo ""
echo "2. La Pija y la Quinqui - Conversación"
echo "   https://www.youtube.com/watch?v=XXXXXXX"
echo ""
echo "3. Entiende Tu Mente - Diálogo claro"
echo "   https://www.youtube.com/watch?v=XXXXXXX"
echo ""

read -p "🔗 Pega la URL del podcast de YouTube: " PODCAST_URL

if [ -z "$PODCAST_URL" ]; then
    echo "❌ No se proporcionó URL"
    exit 1
fi

echo ""
echo "⬇️  Descargando podcast..."

# Crear directorio si no existe
mkdir -p data/raw/podcast

# Descargar con yt-dlp
yt-dlp -x --audio-format mp3 "$PODCAST_URL" -o "data/raw/podcast/podcast.mp3"

if [ ! -f "data/raw/podcast/podcast.mp3" ]; then
    echo "❌ Error al descargar podcast"
    exit 1
fi

echo "✅ Podcast descargado: data/raw/podcast/podcast.mp3"

# Verificar duración
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 data/raw/podcast/podcast.mp3 2>/dev/null)
DURATION_MIN=$(echo "$DURATION / 60" | bc)

echo "⏱️  Duración: ${DURATION_MIN} minutos"

if [ $(echo "$DURATION_MIN < 10" | bc) -eq 1 ]; then
    echo "⚠️  Podcast muy corto (<10 min). Se recomienda 15-30 minutos."
    read -p "¿Continuar de todas formas? (s/N): " CONTINUE
    if [ "$CONTINUE" != "s" ] && [ "$CONTINUE" != "S" ]; then
        exit 0
    fi
fi

echo ""
echo "======================================================================"
echo "  🤖 OPCIONES DE TTS"
echo "======================================================================"
echo ""
echo "1. ElevenLabs (mejor calidad, requiere API key)"
echo "2. Linux TTS (gratis, calidad media)"
echo ""
read -p "Selecciona opción (1/2): " TTS_OPTION

SKIP_TTS=""
if [ "$TTS_OPTION" = "2" ]; then
    SKIP_TTS="--skip_tts"
    
    echo ""
    echo "🔧 Generando muestras con Linux TTS..."
    python src/data_collection/generate_linux_tts_samples.py \
        --output_dir data/raw/linux_tts \
        --num_samples 200
    
    if [ $? -ne 0 ]; then
        echo "❌ Error generando TTS"
        exit 1
    fi
elif [ "$TTS_OPTION" = "1" ]; then
    if [ -z "$ELEVENLABS_API_KEY" ]; then
        echo ""
        read -p "🔑 API Key de ElevenLabs: " API_KEY
        export ELEVENLABS_API_KEY="$API_KEY"
    fi
fi

echo ""
echo "======================================================================"
echo "  🚀 INICIANDO RE-ENTRENAMIENTO"
echo "======================================================================"
echo ""
read -p "Número de segmentos a extraer del podcast (default 150): " NUM_SEGMENTS
NUM_SEGMENTS=${NUM_SEGMENTS:-150}

read -p "Épocas de entrenamiento (default 20): " EPOCHS
EPOCHS=${EPOCHS:-20}

echo ""
echo "📊 Configuración:"
echo "  - Segmentos: $NUM_SEGMENTS"
echo "  - Muestras TTS: 200"
echo "  - Épocas: $EPOCHS"
echo "  - TTS Engine: $([ -z "$SKIP_TTS" ] && echo "ElevenLabs" || echo "Linux TTS")"
echo ""
read -p "⏸️  Presiona ENTER para continuar o Ctrl+C para cancelar..."

# Ejecutar script de re-entrenamiento
python scripts/retrain_robust_model.py \
    --podcast data/raw/podcast/podcast.mp3 \
    --segments $NUM_SEGMENTS \
    --tts_samples 200 \
    --epochs $EPOCHS \
    $SKIP_TTS

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "  ✅ RE-ENTRENAMIENTO COMPLETADO"
    echo "======================================================================"
    echo ""
    echo "📂 Modelo guardado en: models/aasist_v2_robust/"
    echo ""
    echo "🧪 Próximos pasos:"
    echo ""
    echo "1. Probar con audios de WhatsApp:"
    echo "   python src/data_collection/test_whatsapp_audios.py"
    echo ""
    echo "2. Comparar modelos:"
    echo "   python src/evaluation/compare_models.py"
    echo ""
    echo "3. Usar en tiempo real:"
    echo "   python src/realtime/realtime_detection.py --model models/aasist_v2_robust/best_model.pth"
    echo ""
else
    echo ""
    echo "❌ Error durante el re-entrenamiento"
    exit 1
fi
