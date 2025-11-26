#!/bin/bash
# Script para mostrar estado del proyecto y ayuda rápida

BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${BOLD}======================================================================"
echo "  🎤 AASIST FINE-TUNING - ESTADO DEL PROYECTO"
echo -e "======================================================================${NC}"
echo ""

# Verificar datasets
echo -e "${BOLD}📊 DATASETS:${NC}"
if [ -f "data/metadata.csv" ]; then
    ORIGINAL_COUNT=$(wc -l < data/metadata.csv)
    echo -e "  ${GREEN}✓${NC} Dataset original: $((ORIGINAL_COUNT - 1)) muestras"
else
    echo -e "  ${RED}✗${NC} Dataset original no encontrado"
fi

if [ -d "data/raw/podcast_segments" ]; then
    PODCAST_COUNT=$(ls -1 data/raw/podcast_segments/*.wav 2>/dev/null | wc -l)
    echo -e "  ${GREEN}✓${NC} Segmentos de podcast: $PODCAST_COUNT clips"
else
    echo -e "  ${YELLOW}○${NC} Segmentos de podcast: No generados aún"
fi

if [ -d "data/raw/linux_tts" ]; then
    LINUX_TTS_COUNT=$(ls -1 data/raw/linux_tts/*.wav 2>/dev/null | wc -l)
    echo -e "  ${GREEN}✓${NC} Linux TTS: $LINUX_TTS_COUNT muestras"
else
    echo -e "  ${YELLOW}○${NC} Linux TTS: No generadas aún"
fi

if [ -d "data/raw/elevenlabs_extended" ]; then
    ELEVENLABS_COUNT=$(ls -1 data/raw/elevenlabs_extended/*.mp3 2>/dev/null | wc -l)
    echo -e "  ${GREEN}✓${NC} ElevenLabs extended: $ELEVENLABS_COUNT muestras"
else
    echo -e "  ${YELLOW}○${NC} ElevenLabs extended: No generadas aún"
fi

if [ -f "data/metadata_extended.csv" ]; then
    EXTENDED_COUNT=$(wc -l < data/metadata_extended.csv)
    echo -e "  ${GREEN}✓${NC} Metadata extendida: $((EXTENDED_COUNT - 1)) muestras totales"
else
    echo -e "  ${YELLOW}○${NC} Metadata extendida: No creada aún"
fi

# Verificar modelos
echo ""
echo -e "${BOLD}🤖 MODELOS:${NC}"
if [ -f "models/aasist_finetuned/best_model.pth" ]; then
    MODEL_SIZE=$(du -h models/aasist_finetuned/best_model.pth | cut -f1)
    echo -e "  ${GREEN}✓${NC} Modelo v1 (original): $MODEL_SIZE"
else
    echo -e "  ${RED}✗${NC} Modelo v1: No encontrado"
fi

if [ -f "models/aasist_v2_robust/best_model.pth" ]; then
    MODEL_V2_SIZE=$(du -h models/aasist_v2_robust/best_model.pth | cut -f1)
    echo -e "  ${GREEN}✓${NC} Modelo v2 (robusto): $MODEL_V2_SIZE"
else
    echo -e "  ${YELLOW}○${NC} Modelo v2: No entrenado aún"
fi

# Verificar validación
echo ""
echo -e "${BOLD}🧪 VALIDACIÓN:${NC}"
if [ -d "data/test_validation/whatsapp_processed" ]; then
    WHATSAPP_COUNT=$(ls -1 data/test_validation/whatsapp_processed/*.wav 2>/dev/null | wc -l)
    echo -e "  ${GREEN}✓${NC} Audios WhatsApp: $WHATSAPP_COUNT archivos procesados"
else
    echo -e "  ${YELLOW}○${NC} Audios WhatsApp: No hay datos de validación"
fi

# Verificar dependencias
echo ""
echo -e "${BOLD}🔧 DEPENDENCIAS:${NC}"

# Python packages
if python -c "import librosa" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} librosa instalado"
else
    echo -e "  ${RED}✗${NC} librosa no instalado"
fi

if python -c "import torch" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} PyTorch instalado"
else
    echo -e "  ${RED}✗${NC} PyTorch no instalado"
fi

# System tools
if command -v yt-dlp &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} yt-dlp instalado"
else
    echo -e "  ${YELLOW}○${NC} yt-dlp no instalado (pip install yt-dlp)"
fi

if command -v espeak &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} espeak instalado"
else
    echo -e "  ${YELLOW}○${NC} espeak no instalado (sudo apt install espeak)"
fi

# Git status
echo ""
echo -e "${BOLD}📦 GIT:${NC}"
if [ -d ".git" ]; then
    BRANCH=$(git branch --show-current)
    COMMITS=$(git rev-list --count HEAD)
    echo -e "  ${GREEN}✓${NC} Rama: $BRANCH"
    echo -e "  ${GREEN}✓${NC} Commits: $COMMITS"
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        CHANGED_FILES=$(git status --porcelain | wc -l)
        echo -e "  ${YELLOW}○${NC} Cambios sin commit: $CHANGED_FILES archivos"
    else
        echo -e "  ${GREEN}✓${NC} Working tree limpio"
    fi
else
    echo -e "  ${RED}✗${NC} No es un repositorio git"
fi

# Recomendaciones
echo ""
echo -e "${BOLD}======================================================================"
echo "  💡 PRÓXIMOS PASOS"
echo -e "======================================================================${NC}"
echo ""

if [ ! -d "data/raw/podcast_segments" ]; then
    echo -e "${YELLOW}1️⃣  Re-entrenar modelo con podcast:${NC}"
    echo "   ./scripts/download_and_retrain.sh"
    echo ""
    echo "   O paso a paso:"
    echo "   - Descargar: yt-dlp -x --audio-format mp3 URL -o data/raw/podcast/podcast.mp3"
    echo "   - Segmentar: python src/data_collection/segment_podcast.py data/raw/podcast/podcast.mp3"
    echo "   - Entrenar: python scripts/retrain_robust_model.py --podcast data/raw/podcast/podcast.mp3"
    echo ""
elif [ ! -f "models/aasist_v2_robust/best_model.pth" ]; then
    echo -e "${YELLOW}1️⃣  Generar TTS y re-entrenar:${NC}"
    echo "   python scripts/retrain_robust_model.py --podcast data/raw/podcast/podcast.mp3"
    echo ""
else
    echo -e "${GREEN}✅ Modelo v2 entrenado!${NC}"
    echo ""
    echo -e "${BLUE}📊 Validar modelo:${NC}"
    echo "   python src/data_collection/test_whatsapp_audios.py --model models/aasist_v2_robust/best_model.pth"
    echo ""
    echo -e "${BLUE}🎤 Usar en tiempo real:${NC}"
    echo "   python src/realtime/realtime_detection.py --model models/aasist_v2_robust/best_model.pth"
    echo ""
fi

echo -e "${BLUE}📖 Ver documentación completa:${NC}"
echo "   cat QUICK_START_RETRAIN.md"
echo "   cat PROJECT_STATUS.md"
echo ""

echo -e "${BLUE}🔄 Sincronizar con GitHub:${NC}"
echo "   git add ."
echo "   git commit -m \"Update: Re-training infrastructure ready\""
echo "   git push origin main"
echo ""
