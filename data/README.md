Carpeta `data/`:

- `external/` : datasets externos tal cual como ASVspoof.
- `raw/` : grabaciones originales, sin tocar.
- `processed/` : audio re-muestreado y convertido a WAV 16kHz mono PCM16.
- `metadata/` : CSVs con las rutas y labels. El maestro debe llamarse `metadata_all.csv`.

Formato recomendado en `processed/`:
- WAV PCM 16-bit
- 16 kHz
- mono

Ejemplo CSV en `metadata_all.csv`:

filepath,label,source,tts_engine,text,split
"data/processed/combined/train/human_00001.wav",bonafide,human,,"Hola",train
