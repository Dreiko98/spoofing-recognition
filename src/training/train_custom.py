"""Fine-tuning skeleton for AASIST

- Lee `config/paths.yaml` y `config/train_config.yaml`
- Carga dataset con `CustomSpoofDataset`
- Construye DataLoader
- Intenta cargar un modelo AASIST desde checkpoint (si existe la impl.)
- Entrena un número de epochs y guarda checkpoint + config de entrenamiento

Este archivo es intencionalmente flexible: adapta el loader de AASIST según tu instalación del paquete `aasist`.
"""

import os
import yaml
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from src.datasets.custom_dataset import CustomSpoofDataset, collate_fn


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def save_yaml(obj, path):
    with open(path, "w") as f:
        yaml.safe_dump(obj, f)


def try_load_aasist_model(checkpoint_path, device):
    """Intento genérico de cargar un checkpoint de AASIST.
    Si tienes `aasist` como paquete, reemplaza esta función por la carga oficial.
    """
    if not os.path.exists(checkpoint_path):
        print(f"Pretrained checkpoint not found: {checkpoint_path}")
        return None
    try:
        # Intentar cargar como state_dict
        state = torch.load(checkpoint_path, map_location=device)
        # Si dispones de la clase/model impl, deberías instanciarla y cargar state_dict
        print("Checkpoint loaded. Please adapt `try_load_aasist_model` to map weights into your model.")
        return state
    except Exception as e:
        print("Error cargando checkpoint:", e)
        return None


def train():
    root = Path(__file__).resolve().parents[2]
    paths = load_yaml(root / "config" / "paths.yaml")
    cfg = load_yaml(root / "config" / "train_config.yaml")

    device = torch.device(cfg.get("device", "cpu"))
    sample_rate = cfg.get("sample_rate", 16000)

    # Datasets
    metadata = paths.get("metadata_all")
    train_ds = CustomSpoofDataset(metadata, split="train", sample_rate=sample_rate)
    dev_ds = CustomSpoofDataset(metadata, split="dev", sample_rate=sample_rate)

    train_loader = DataLoader(train_ds, batch_size=cfg.get("batch_size", 16), shuffle=True, collate_fn=collate_fn)
    dev_loader = DataLoader(dev_ds, batch_size=cfg.get("batch_size", 16), shuffle=False, collate_fn=collate_fn)

    # Model (placeholder)
    pretrained = paths.get("pretrained_model")
    state = try_load_aasist_model(pretrained, device)

    # If you have a model class, instantiate and load state_dict here.
    # Ejemplo:
    model = None
    if state is None:
        print("No se cargó modelo preentrenado; entrenando un modelo dummy (logit random). Reemplaza con AASIST.")
        # Dummy model para que el script sea ejecutable
        model = nn.Sequential(nn.Conv1d(1, 8, kernel_size=3, stride=1), nn.AdaptiveAvgPool1d(1), nn.Flatten(), nn.Linear(8, 2))
    else:
        # Si state es un state_dict, debes instanciar tu modelo real e insertar load_state_dict
        # Por ahora, usamos dummy también
        model = nn.Sequential(nn.Conv1d(1, 8, kernel_size=3, stride=1), nn.AdaptiveAvgPool1d(1), nn.Flatten(), nn.Linear(8, 2))

    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.get("learning_rate", 1e-4), weight_decay=cfg.get("weight_decay", 1e-5))

    epochs = cfg.get("epochs", 1)
    out_dir = Path("models/checkpoints").absolute()
    out_dir.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, epochs + 1):
        model.train()
        pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{epochs}")
        running_loss = 0.0
        for batch in pbar:
            inputs, labels, _paths = batch
            inputs = inputs.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            pbar.set_postfix({"loss": running_loss / (pbar.n + 1)})

        # simple dev evaluation
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for batch in dev_loader:
                inputs, labels, _ = batch
                inputs = inputs.to(device)
                labels = labels.to(device)
                outputs = model(inputs)
                preds = outputs.argmax(dim=1)
                correct += (preds == labels).sum().item()
                total += labels.numel()
        acc = correct / total if total > 0 else 0.0
        print(f"Epoch {epoch} dev acc: {acc:.4f}")

        # Save checkpoint + config
        ts = time.strftime("%Y%m%d_%H%M%S")
        ckpt_name = f"aasist_ft_custom_epoch{epoch}_{ts}.pth"
        ckpt_path = out_dir / ckpt_name
        torch.save({
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "cfg": cfg,
            "paths": paths,
        }, ckpt_path)

        # save small config
        cfg_path = out_dir / f"{ckpt_name}_config.yaml"
        save_yaml({"epoch": epoch, "acc": acc, "train_cfg": cfg, "created_at": ts}, cfg_path)

    print("Entrenamiento terminado. Checkpoints guardados en:", out_dir)


if __name__ == "__main__":
    train()
