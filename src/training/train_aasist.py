#!/usr/bin/env python3
"""
Fine-tuning de AASIST con dataset personalizado

Este script:
1. Carga el modelo AASIST pre-entrenado
2. Hace fine-tuning con tus 222 muestras
3. Guarda el modelo personalizado
4. Evalúa en test set
"""

import sys
import argparse
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from tqdm import tqdm
import numpy as np
import librosa
from sklearn.metrics import accuracy_score, roc_auc_score
import json

# Añadir path para importar AASIST
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.AASIST import Model as AASISTModel


class AudioDataset(Dataset):
    """Dataset para cargar audios"""
    
    def __init__(self, csv_path, split='train', target_sr=16000, max_len=64600):
        self.df = pd.read_csv(csv_path)
        self.df = self.df[self.df['split'] == split]
        self.target_sr = target_sr
        self.max_len = max_len
        
        print(f"   {split}: {len(self.df)} muestras")
        
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        
        # Cargar audio
        audio, sr = librosa.load(row['filepath'], sr=self.target_sr, mono=True)
        
        # Ajustar longitud
        if len(audio) < self.max_len:
            # Pad
            audio = np.pad(audio, (0, self.max_len - len(audio)), 'constant')
        else:
            # Truncate
            audio = audio[:self.max_len]
        
        # Convertir a tensor
        audio = torch.FloatTensor(audio)
        
        # Label: bonafide=0, spoof=1
        label = 1 if row['label'] == 'spoof' else 0
        label = torch.LongTensor([label])
        
        return audio, label


def train_epoch(model, dataloader, criterion, optimizer, device):
    """Entrena una época"""
    model.train()
    total_loss = 0
    predictions = []
    true_labels = []
    
    pbar = tqdm(dataloader, desc="Training")
    for audio, labels in pbar:
        audio = audio.to(device)
        labels = labels.to(device).squeeze()
        
        # Forward
        optimizer.zero_grad()
        output = model(audio)
        
        # AASIST devuelve tuple (output, feat_loss)
        if isinstance(output, tuple):
            output, feat_loss = output
        else:
            feat_loss = torch.tensor(0.0, device=output.device)
        
        # Asegurar que output tenga la forma correcta [batch_size]
        if output.dim() > 1:
            output = output.squeeze()
        if output.dim() > 1:  # Si todavía tiene más de 1 dim, tomar media
            output = output.mean(dim=1)
        
        # Loss - SOLO usar CE loss, ignorar feat_loss para fine-tuning
        loss = criterion(output, labels.float())
        
        # Backward
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
        # Predicciones
        probs = torch.sigmoid(output)
        preds = (probs > 0.5).long()
        predictions.extend(preds.cpu().numpy().tolist())
        true_labels.extend(labels.cpu().numpy().tolist())
        
        # Actualizar barra
        pbar.set_postfix({'loss': loss.item()})
    
    avg_loss = total_loss / len(dataloader)
    accuracy = accuracy_score(true_labels, predictions)
    
    return avg_loss, accuracy


def evaluate(model, dataloader, criterion, device):
    """Evalúa el modelo"""
    model.eval()
    total_loss = 0
    predictions = []
    true_labels = []
    scores = []
    
    with torch.no_grad():
        for audio, labels in tqdm(dataloader, desc="Evaluating"):
            audio = audio.to(device)
            labels = labels.to(device).squeeze()
            
            # Forward
            output = model(audio)
            
            # AASIST devuelve tuple
            if isinstance(output, tuple):
                output = output[0]
            
            # Tomar media si necesario
            if output.numel() > len(labels):
                output = output.mean(dim=1)
            
            # Loss
            loss = criterion(output.squeeze(), labels.float())
            total_loss += loss.item()
            
            # Predicciones
            probs = torch.sigmoid(output.squeeze())
            preds = (probs > 0.5).long()
            
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
            scores.extend(probs.cpu().numpy())
    
    avg_loss = total_loss / len(dataloader)
    accuracy = accuracy_score(true_labels, predictions)
    
    try:
        auc = roc_auc_score(true_labels, scores)
    except:
        auc = 0.0
    
    return avg_loss, accuracy, auc


def main():
    parser = argparse.ArgumentParser(description='Fine-tuning de AASIST')
    parser.add_argument('--csv', type=str, default='data/metadata_processed.csv',
                        help='CSV con metadata')
    parser.add_argument('--pretrained', type=str, default='models/AASIST/models/weights/AASIST.pth',
                        help='Modelo pre-entrenado')
    parser.add_argument('--output_dir', type=str, default='models/aasist_finetuned',
                        help='Directorio de salida')
    parser.add_argument('--epochs', type=int, default=20,
                        help='Número de épocas')
    parser.add_argument('--batch_size', type=int, default=8,
                        help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001,
                        help='Learning rate')
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu',
                        help='Device (cuda/cpu)')
    args = parser.parse_args()
    
    # Crear directorio de salida
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("    🚀 FINE-TUNING DE AASIST")
    print("=" * 70)
    print()
    print(f"📄 Dataset: {args.csv}")
    print(f"🤖 Modelo base: {args.pretrained}")
    print(f"📁 Output: {args.output_dir}")
    print(f"⚙️  Configuración:")
    print(f"   - Epochs: {args.epochs}")
    print(f"   - Batch size: {args.batch_size}")
    print(f"   - Learning rate: {args.lr}")
    print(f"   - Device: {args.device}")
    print()
    
    # Cargar datasets
    print("📦 Cargando datasets...")
    train_dataset = AudioDataset(args.csv, split='train')
    dev_dataset = AudioDataset(args.csv, split='dev')
    test_dataset = AudioDataset(args.csv, split='test')
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=2)
    dev_loader = DataLoader(dev_dataset, batch_size=args.batch_size, shuffle=False, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=2)
    
    print()
    
    # Cargar modelo
    print("🤖 Inicializando modelo...")
    device = torch.device(args.device)
    
    model = AASISTModel({
        'architecture': 'AASIST',
        'nb_samp': 64600,
        'first_conv': 128,
        'filts': [70, [1, 32], [32, 32], [32, 64], [64, 64]],
        'gat_dims': [64, 32],
        'pool_ratios': [0.5, 0.7, 0.5, 0.5],
        'temperatures': [2.0, 2.0, 100.0, 100.0],
    })
    
    # Cargar pesos pre-entrenados
    print(f"   Cargando pesos de: {args.pretrained}")
    checkpoint = torch.load(args.pretrained, map_location=device)
    model.load_state_dict(checkpoint, strict=False)
    model.to(device)
    
    print(f"   ✅ Modelo cargado en: {device}")
    print()
    
    # Configurar entrenamiento
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=2, factor=0.5)
    
    # Entrenamiento
    print("=" * 70)
    print("    🏋️  ENTRENAMIENTO")
    print("=" * 70)
    print()
    
    best_dev_loss = float('inf')
    best_dev_acc = 0.0
    history = {
        'train_loss': [], 'train_acc': [],
        'dev_loss': [], 'dev_acc': [], 'dev_auc': []
    }
    
    for epoch in range(args.epochs):
        print(f"\n📍 Epoch {epoch + 1}/{args.epochs}")
        print("-" * 70)
        
        # Train
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        
        # Evaluate on dev
        dev_loss, dev_acc, dev_auc = evaluate(model, dev_loader, criterion, device)
        
        # Scheduler
        scheduler.step(dev_loss)
        
        # Guardar historia
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['dev_loss'].append(dev_loss)
        history['dev_acc'].append(dev_acc)
        history['dev_auc'].append(dev_auc)
        
        print(f"\n📊 Resultados Epoch {epoch + 1}:")
        print(f"   Train - Loss: {train_loss:.4f}, Acc: {train_acc * 100:.2f}%")
        print(f"   Dev   - Loss: {dev_loss:.4f}, Acc: {dev_acc * 100:.2f}%, AUC: {dev_auc:.4f}")
        
        # Guardar mejor modelo
        if dev_acc > best_dev_acc:
            best_dev_acc = dev_acc
            best_dev_loss = dev_loss
            
            # Guardar checkpoint
            checkpoint_path = output_dir / 'best_model.pth'
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'dev_loss': dev_loss,
                'dev_acc': dev_acc,
                'dev_auc': dev_auc,
            }, checkpoint_path)
            
            print(f"   💾 Mejor modelo guardado (Acc: {dev_acc * 100:.2f}%)")
    
    # Guardar historia
    with open(output_dir / 'training_history.json', 'w') as f:
        json.dump(history, f, indent=2)
    
    # Evaluación final en test
    print()
    print("=" * 70)
    print("    🎯 EVALUACIÓN FINAL EN TEST SET")
    print("=" * 70)
    print()
    
    # Cargar mejor modelo
    checkpoint = torch.load(output_dir / 'best_model.pth')
    model.load_state_dict(checkpoint['model_state_dict'])
    
    test_loss, test_acc, test_auc = evaluate(model, test_loader, criterion, device)
    
    print(f"\n📊 Resultados en Test Set:")
    print(f"   Loss: {test_loss:.4f}")
    print(f"   Accuracy: {test_acc * 100:.2f}%")
    print(f"   AUC-ROC: {test_auc:.4f}")
    print()
    
    # Guardar resultados
    results = {
        'test_loss': test_loss,
        'test_acc': test_acc,
        'test_auc': test_auc,
        'best_dev_acc': best_dev_acc,
        'best_dev_loss': best_dev_loss,
    }
    
    with open(output_dir / 'test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("=" * 70)
    print("    ✅ FINE-TUNING COMPLETADO")
    print("=" * 70)
    print()
    print(f"📁 Archivos guardados en: {output_dir}/")
    print(f"   • best_model.pth        - Mejor modelo")
    print(f"   • training_history.json - Historia de entrenamiento")
    print(f"   • test_results.json     - Resultados en test")
    print()
    
    # Comparación con baseline
    print("📊 Comparación con modelo pre-entrenado:")
    print(f"   Pre-entrenado: 69.44% accuracy")
    print(f"   Fine-tuned:    {test_acc * 100:.2f}% accuracy")
    
    if test_acc > 0.69:
        improvement = (test_acc - 0.69) * 100
        print(f"   🎉 Mejora de: +{improvement:.2f}%")
    
    print()
    print("=" * 70)
    print("🎯 Próximo paso: Usar el modelo para detección en tiempo real")
    print("   python src/realtime/realtime_detection.py \\")
    print(f"       --model {output_dir}/best_model.pth")
    print("=" * 70)


if __name__ == '__main__':
    main()
