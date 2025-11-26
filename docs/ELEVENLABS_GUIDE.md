# 🎙️ Guía: Generar Muestras con ElevenLabs

## 📋 Requisitos previos

1. **Cuenta en ElevenLabs**: https://elevenlabs.io
2. **API Key**: Obtén tu clave en https://elevenlabs.io/app/settings/api-keys
3. **Créditos**: Verifica que tengas créditos disponibles en tu cuenta

---

## ⚙️ Configuración inicial

### 1. Instalar el paquete de ElevenLabs

```bash
source .venv/bin/activate
pip install elevenlabs
```

### 2. Configurar la API Key

```bash
# Exportar la variable de entorno
export ELEVENLABS_API_KEY="tu_clave_aqui"

# Verificar que esté configurada
echo $ELEVENLABS_API_KEY
```

**⚠️ IMPORTANTE:** La API key debe exportarse en cada sesión de terminal, o puedes añadirla a tu `~/.bashrc` o `~/.zshrc`:

```bash
# Añadir al final de ~/.bashrc
echo 'export ELEVENLABS_API_KEY="tu_clave_aqui"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Verificar configuración

```bash
python3 src/data_collection/check_elevenlabs_config.py
```

Deberías ver:
```
✅ API Key configurada: sk_xxxxx...xxxx
✅ Cliente ElevenLabs importado correctamente
✅ Conexión exitosa! Encontradas 21 voces disponibles
```

---

## 🚀 Uso del generador

### Listar voces disponibles

```bash
python3 src/data_collection/generate_elevenlabs_samples.py --list_voices
```

### Generar muestras (básico)

```bash
# 10 muestras con configuración por defecto
python3 src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs \
    --num_samples 10
```

### Generar muestras (avanzado)

```bash
# Con voz específica y modelo específico
python3 src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs \
    --num_samples 50 \
    --model eleven_flash_v2_5 \
    --voice_id 2EiwWnXFnvU5JabPnv8n \
    --rate_limit 1.5
```

**Parámetros disponibles:**
- `--output_dir`: Carpeta de salida (default: `data/raw/elevenlabs`)
- `--num_samples`: Número de muestras (default: 50)
- `--model`: Modelo TTS (opciones: `eleven_flash_v2_5`, `eleven_multilingual_v2`, `eleven_turbo_v2_5`)
- `--voice_id`: ID de voz específica (opcional, si no se especifica usa una aleatoria)
- `--rate_limit`: Segundos entre requests (default: 1.0) - aumenta si recibes rate limit errors

---

## 📊 Modelos disponibles

| Modelo | Características | Uso recomendado |
|--------|-----------------|------------------|
| `eleven_flash_v2_5` | Rápido, eficiente, calidad alta | **Recomendado** para datasets |
| `eleven_multilingual_v2` | Soporte multiidioma | Textos en múltiples idiomas |
| `eleven_turbo_v2_5` | Ultra rápido | Grandes volúmenes, menor calidad |

---

## 🎯 Voces recomendadas (en inglés)

Para variar el dataset, usa diferentes voces:

```bash
# Voz masculina (Clyde)
python3 src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs \
    --num_samples 25 \
    --voice_id 2EiwWnXFnvU5JabPnv8n

# Voz femenina (Sarah)
python3 src/data_collection/generate_elevenlabs_samples.py \
    --output_dir data/raw/elevenlabs \
    --num_samples 25 \
    --voice_id EXAVITQu4vr4xnSDxMaL
```

---

## ⚠️ Troubleshooting

### Error: "needs_authorization"

```
❌ Error generando audio: ... status_code: 401 ... 'needs_authorization'
```

**Solución:** API key no configurada o incorrecta
```bash
export ELEVENLABS_API_KEY="tu_clave_correcta"
python3 src/data_collection/check_elevenlabs_config.py
```

### Error: "quota_exceeded"

```
❌ Error generando audio: ... 'quota_exceeded'
```

**Solución:** Sin créditos en la cuenta
- Verifica tus créditos en: https://elevenlabs.io/app/usage
- Planes gratis tienen límite mensual (~10k caracteres)

### Error: "rate_limit_exceeded"

```
❌ Error generando audio: ... 'rate_limit_exceeded'
```

**Solución:** Demasiadas requests por segundo
```bash
# Aumenta el rate_limit
python3 src/data_collection/generate_elevenlabs_samples.py \
    --rate_limit 2.0  # espera 2 segundos entre requests
```

### Error: "Import 'elevenlabs' could not be resolved"

**Solución:** Paquete no instalado
```bash
source .venv/bin/activate
pip install elevenlabs
```

---

## 💰 Costos y límites

### Plan Gratuito
- **10,000 caracteres/mes**
- ~3-5 minutos de audio
- Suficiente para ~50-100 muestras cortas

### Cálculo de caracteres
Una frase promedio de 10 palabras ≈ 50-70 caracteres

**Ejemplo:**
- 100 muestras × 60 caracteres = 6,000 caracteres
- Costo: Gratis (dentro del límite)

---

## 📁 Siguiente paso: Conversión

Una vez generadas las muestras, conviértelas a formato estándar:

```bash
python3 src/data_collection/convert_to_standard_format.py \
    --input_dir data/raw/elevenlabs \
    --output_dir data/processed/elevenlabs
```

---

## 🔗 Enlaces útiles

- **Dashboard:** https://elevenlabs.io/app
- **API Docs:** https://elevenlabs.io/docs/api-reference
- **Límites y planes:** https://elevenlabs.io/pricing
- **Voces disponibles:** https://elevenlabs.io/voice-library

---

## ✅ Checklist rápido

- [ ] Cuenta creada en ElevenLabs
- [ ] API key obtenida
- [ ] `pip install elevenlabs` ejecutado
- [ ] `export ELEVENLABS_API_KEY="..."` configurado
- [ ] Verificación con `check_elevenlabs_config.py` exitosa
- [ ] Generadas muestras de prueba (3-5 muestras)
- [ ] Generado dataset completo (50-100 muestras)
- [ ] Convertido a WAV 16kHz mono
