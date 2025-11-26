#!/usr/bin/env python3
"""
Evalúa el modelo AASIST pre-entrenado en tu dataset personalizado

Este script:
1. Carga el modelo AASIST pre-entrenado
2. Evalúa en tus 222 muestras
3. Muestra métricas de rendimiento
"""

import sys
import argparse
import pandas as pd
import torch
import torchaudio
from pathlib import Path
from tqdm import tqdm
import numpy as np
from sklearn.metrics import roc_auc_score, accuracy_score, confusion_matrix

# Añadir path para importar AASIST
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.AASIST import Model as AASISTModel


def load_audio(filepath, target_sr=16000):
    """Carga audio y lo convierte a tensor"""
    try:
        import librosa
        import numpy as np
        
        # Cargar con librosa (más compatible)
        waveform, sr = librosa.load(filepath, sr=target_sr, mono=True)
        
        # Convertir a tensor de PyTorch
        waveform = torch.from_numpy(waveform).float()
        
        return waveform
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def evaluate_model(model_path, csv_path, device='cpu', split='test'):
    """Evalúa el modelo en el dataset"""
    
    print("=" * 70)
    print("    🔍 EVALUACIÓN DE AASIST PRE-ENTRENADO")
    print("=" * 70)
    print()
    
    # Cargar CSV
    print(f"📄 Cargando metadata: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Filtrar por split si se especifica
    if split:
        df = df[df['split'] == split]
        print(f"   Evaluando en split: {split}")
    
    print(f"   Total de muestras: {len(df)}")
    print()
    
    # Cargar modelo
    print(f"🤖 Cargando modelo: {model_path}")
    device = torch.device(device)
    
    # Inicializar modelo AASIST
    model = AASISTModel({
        'architecture': 'AASIST',
        'nb_samp': 64600,  # ~4 segundos a 16kHz
        'first_conv': 128,
        'filts': [70, [1, 32], [32, 32], [32, 64], [64, 64]],
        'gat_dims': [64, 32],
        'pool_ratios': [0.5, 0.7, 0.5, 0.5],
        'temperatures': [2.0, 2.0, 100.0, 100.0],
    })
    
    # Cargar pesos
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint, strict=False)
    model.to(device)
    model.eval()
    
    print(f"   ✅ Modelo cargado en: {device}")
    print()
    
    # Evaluar
    print("🔄 Evaluando muestras...")
    predictions = []
    true_labels = []
    scores = []
    
    with torch.no_grad():
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Procesando"):
            # Cargar audio
            audio = load_audio(row['filepath'])
            if audio is None:
                continue
            
            # Ajustar longitud (pad o truncate)
            target_len = 64600
            if len(audio) < target_len:
                # Pad con zeros
                audio = torch.nn.functional.pad(audio, (0, target_len - len(audio)))
            else:
                # Truncate
                audio = audio[:target_len]
            
            # Añadir batch dimension
            audio = audio.unsqueeze(0).to(device)
            
            # Forward pass
            output = model(audio)
            
            # El modelo puede devolver tuple (output, hidden) o solo output
            if isinstance(output, tuple):
                output = output[0]  # Tomar solo el output
            
            # Aplanar si tiene múltiples dimensiones y tomar la media
            if output.numel() > 1:
                output = output.mean()
            
            score = torch.sigmoid(output).item()
            
            # Label: bonafide=0, spoof=1
            true_label = 1 if row['label'] == 'spoof' else 0
            pred_label = 1 if score > 0.5 else 0
            
            predictions.append(pred_label)
            true_labels.append(true_label)
            scores.append(score)
    
    # Calcular métricas
    print()
    print("=" * 70)
    print("    📊 RESULTADOS")
    print("=" * 70)
    print()
    
    accuracy = accuracy_score(true_labels, predictions)
    try:
        auc = roc_auc_score(true_labels, scores)
    except:
        auc = -1
    
    cm = confusion_matrix(true_labels, predictions)
    
    print(f"🎯 Accuracy: {accuracy * 100:.2f}%")
    if auc != -1:
        print(f"📈 AUC-ROC:  {auc:.4f}")
    print()
    
    print("📋 Confusion Matrix:")
    print("                Predicted")
    print("              Bonafide  Spoof")
    print(f"Actual Bonafide   {cm[0][0]:3d}     {cm[0][1]:3d}")
    print(f"       Spoof      {cm[1][0]:3d}     {cm[1][1]:3d}")
    print()
    
    # Desglose por tipo
    df['prediction'] = predictions
    df['score'] = scores
    df['true_label'] = true_labels
    
    print("📊 Rendimiento por fuente:")
    for source in df['source'].unique():
        source_df = df[df['source'] == source]
        source_acc = accuracy_score(source_df['true_label'], source_df['prediction'])
        print(f"   {source:15s}: {source_acc * 100:5.2f}% ({len(source_df):3d} muestras)")
    
    print()
    print("=" * 70)
    print("💡 INTERPRETACIÓN:")
    print("=" * 70)
    print()
    
    if accuracy > 0.9:
        print("🎉 ¡Excelente! El modelo pre-entrenado funciona muy bien en tus datos")
    elif accuracy > 0.7:
        print("✅ Buen rendimiento. El fine-tuning puede mejorarlo aún más")
    else:
        print("⚠️  Rendimiento bajo. El fine-tuning con tu dataset es MUY recomendado")
    
    print()
    print("🎯 Próximo paso:")
    print("   python src/training/train_aasist.py \\")
    print("       --csv data/metadata_processed.csv \\")
    print(f"       --pretrained {model_path} \\")
    print("       --output_dir models/aasist_fine_tuned")
    print()
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Evaluar AASIST pre-entrenado')
    parser.add_argument('--model', type=str, default='models/weights/AASIST.pth',
                        help='Ruta al modelo pre-entrenado')
    parser.add_argument('--csv', type=str, default='data/metadata_processed.csv',
                        help='Ruta al CSV con metadata')
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu',
                        help='Device (cuda/cpu)')
    parser.add_argument('--split', type=str, default='test',
                        choices=['train', 'dev', 'test', 'all'],
                        help='Split a evaluar')
    args = parser.parse_args()
    
    if args.split == 'all':
        args.split = None
    
    evaluate_model(args.model, args.csv, args.device, args.split)


if __name__ == '__main__':
    main()
