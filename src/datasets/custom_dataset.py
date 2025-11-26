"""CustomSpoofDataset

Cargador mínimo compatible con un pipeline de fine-tuning para AASIST.
- Lee un CSV de metadatos (`filepath,label,source,tts_engine,text,split`)
- Filtra por split
- Carga audio, remuestrea si hace falta a 16 kHz
- Devuelve (waveform, label)

Requisitos: pandas, soundfile, librosa, torch
"""

import os
from typing import Optional

import pandas as pd
import soundfile as sf
import librosa
import torch
from torch.utils.data import Dataset

LABEL_MAP = {"bonafide": 0, "spoof": 1}


class CustomSpoofDataset(Dataset):
    def __init__(self, metadata_csv: str, split: str = "train", sample_rate: int = 16000, max_duration: Optional[float] = None):
        self.df = pd.read_csv(metadata_csv)
        self.df = self.df[self.df["split"] == split].reset_index(drop=True)
        self.sample_rate = sample_rate
        self.max_duration = max_duration  # seconds, optional

    def __len__(self):
        return len(self.df)

    def _load_audio(self, path: str):
        # path may be relative to repo root
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        data, sr = sf.read(path, dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        if sr != self.sample_rate:
            data = librosa.resample(data, orig_sr=sr, target_sr=self.sample_rate)
        if self.max_duration is not None:
            max_len = int(self.sample_rate * self.max_duration)
            if len(data) > max_len:
                data = data[:max_len]
        return data

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        filepath = row["filepath"]
        label_str = str(row["label"]).strip()
        label = LABEL_MAP.get(label_str, 1)
        waveform = self._load_audio(filepath)
        waveform = torch.from_numpy(waveform).float()
        return waveform, label, filepath


def collate_fn(batch):
    # batch: list of (waveform, label, filepath)
    waves = [b[0] for b in batch]
    labels = torch.tensor([b[1] for b in batch], dtype=torch.long)
    paths = [b[2] for b in batch]
    # pad to max length
    max_len = max([w.shape[0] for w in waves])
    padded = torch.zeros((len(waves), max_len), dtype=torch.float)
    for i, w in enumerate(waves):
        padded[i, : w.shape[0]] = w
    # add channel dim if model expects (B, 1, T)
    padded = padded.unsqueeze(1)
    return padded, labels, paths
