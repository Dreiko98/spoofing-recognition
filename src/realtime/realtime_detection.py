#!/usr/bin/env python3
"""
🎤 Detección de Deepfakes en Tiempo Real con AASIST
Graba audio desde el micrófono y detecta si es voz humana o sintética
"""

import os
import sys
import argparse
import time
import numpy as np
import torch
import sounddevice as sd
import soundfile as sf
from datetime import datetime
import librosa

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.models.AASIST import Model


class RealtimeDetector:
    """Detector de deepfakes en tiempo real"""
    
    def __init__(self, model_path, device='cpu', sample_rate=16000):
        """
        Args:
            model_path: Ruta al modelo fine-tuned
            device: 'cpu' o 'cuda'
            sample_rate: Frecuencia de muestreo (16kHz para AASIST)
        """
        self.device = device
        self.sample_rate = sample_rate
        
        # Cargar modelo
        print(f"🤖 Cargando modelo desde: {model_path}")
        
        # Configuración del modelo AASIST
        d_args = {
            'architecture': 'AASIST',
            'nb_samp': 64600,  # ~4 segundos a 16kHz
            'first_conv': 128,
            'filts': [70, [1, 32], [32, 32], [32, 64], [64, 64]],
            'gat_dims': [64, 32],
            'pool_ratios': [0.5, 0.7, 0.5, 0.5],
            'temperatures': [2.0, 2.0, 100.0, 100.0],
        }
        
        self.model = Model(d_args)
        checkpoint = torch.load(model_path, map_location=device)
        
        # El checkpoint puede tener solo el state_dict o un dict con más info
        if 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint, strict=False)
        
        self.model.to(device)
        self.model.eval()
        print(f"✅ Modelo cargado en: {device}\n")
    
    def record_audio(self, duration=3.0, show_countdown=True):
        """
        Graba audio desde el micrófono
        
        Args:
            duration: Duración en segundos
            show_countdown: Mostrar cuenta regresiva
        
        Returns:
            audio: Array numpy con el audio grabado
        """
        if show_countdown:
            print("🎤 Preparado para grabar...")
            for i in range(3, 0, -1):
                print(f"   {i}...")
                time.sleep(1)
            print("   🔴 GRABANDO!\n")
        
        # Grabar
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        if show_countdown:
            print("   ✅ Grabación completa\n")
        
        return audio.flatten()
    
    def preprocess_audio(self, audio):
        """
        Preprocesa audio para el modelo AASIST
        
        Args:
            audio: Array numpy con audio
        
        Returns:
            tensor: Tensor de PyTorch listo para el modelo
        """
        # Normalizar
        if np.abs(audio).max() > 0:
            audio = audio / np.abs(audio).max() * 0.9
        
        # Convertir a tensor
        audio_tensor = torch.FloatTensor(audio).unsqueeze(0).to(self.device)
        
        return audio_tensor
    
    def predict(self, audio):
        """
        Predice si el audio es bonafide (humano) o spoof (sintético)
        
        Args:
            audio: Array numpy con audio
        
        Returns:
            dict con predicción, probabilidad y confianza
        """
        # Preprocesar
        audio_tensor = self.preprocess_audio(audio)
        
        # Inferencia
        with torch.no_grad():
            output = self.model(audio_tensor)
            
            # AASIST puede devolver tuple (output, feat_loss)
            if isinstance(output, tuple):
                output = output[0]
            
            # Manejar diferentes dimensiones de output
            if output.dim() > 1:
                output = output.squeeze()
            if output.dim() > 1:
                output = output.mean(dim=1)
            # Asegurar que sea escalar
            if output.dim() > 0:
                output = output.mean()
            
            # Aplicar sigmoid para obtener probabilidad
            prob_spoof = torch.sigmoid(output).item()
            prob_bonafide = 1 - prob_spoof
        
        # Determinar predicción
        is_human = prob_bonafide > 0.5
        confidence = max(prob_bonafide, prob_spoof)
        
        return {
            'is_human': is_human,
            'label': 'HUMANO' if is_human else 'DEEPFAKE',
            'prob_human': prob_bonafide,
            'prob_deepfake': prob_spoof,
            'confidence': confidence
        }
    
    def save_audio(self, audio, prediction, output_dir='data/realtime_samples'):
        """Guarda el audio grabado con metadata"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        label = 'human' if prediction['is_human'] else 'deepfake'
        filename = f"{timestamp}_{label}_{int(prediction['confidence']*100)}.wav"
        filepath = os.path.join(output_dir, filename)
        
        # Guardar
        sf.write(filepath, audio, self.sample_rate)
        
        return filepath
    
    def print_results(self, prediction, verbose=True):
        """Imprime resultados de forma visual"""
        
        # Emoji y color según predicción
        if prediction['is_human']:
            emoji = '👤'
            status = '✅ VOZ HUMANA DETECTADA'
        else:
            emoji = '🤖'
            status = '⚠️  DEEPFAKE DETECTADO'
        
        print("=" * 70)
        print(f"  {emoji}  {status}")
        print("=" * 70)
        
        if verbose:
            print(f"\n📊 Probabilidades:")
            print(f"   🧑 Humano:    {prediction['prob_human']:.2%} {'█' * int(prediction['prob_human'] * 40)}")
            print(f"   🤖 Deepfake:  {prediction['prob_deepfake']:.2%} {'█' * int(prediction['prob_deepfake'] * 40)}")
            print(f"\n🎯 Confianza: {prediction['confidence']:.2%}")
        
        print("\n")


def interactive_mode(detector, duration=3.0, save_samples=False):
    """Modo interactivo: graba y analiza continuamente"""
    
    print("=" * 70)
    print("  🎤 MODO INTERACTIVO - DETECCIÓN EN TIEMPO REAL")
    print("=" * 70)
    print(f"\n⚙️  Configuración:")
    print(f"   • Duración de grabación: {duration}s")
    print(f"   • Sample rate: {detector.sample_rate} Hz")
    print(f"   • Guardar muestras: {'Sí' if save_samples else 'No'}")
    print(f"\n💡 Instrucciones:")
    print(f"   • Presiona ENTER para grabar")
    print(f"   • Presiona Ctrl+C para salir")
    print("\n" + "=" * 70 + "\n")
    
    session_count = 0
    
    try:
        while True:
            # Esperar input del usuario
            input("Presiona ENTER para grabar (o Ctrl+C para salir)...")
            
            # Grabar
            audio = detector.record_audio(duration=duration)
            
            # Predecir
            print("🔍 Analizando audio...\n")
            prediction = detector.predict(audio)
            
            # Mostrar resultados
            detector.print_results(prediction)
            
            # Guardar si está habilitado
            if save_samples:
                filepath = detector.save_audio(audio, prediction)
                print(f"💾 Muestra guardada: {filepath}\n")
            
            session_count += 1
            print(f"📝 Muestras procesadas en esta sesión: {session_count}\n")
            print("-" * 70 + "\n")
    
    except KeyboardInterrupt:
        print("\n\n👋 Sesión finalizada.")
        print(f"📊 Total de muestras procesadas: {session_count}")
        print("\n¡Hasta pronto!\n")


def batch_mode(detector, audio_files, save_results=False):
    """Modo batch: analiza archivos de audio existentes"""
    
    print("=" * 70)
    print("  📁 MODO BATCH - ANÁLISIS DE ARCHIVOS")
    print("=" * 70)
    print(f"\n📝 Archivos a procesar: {len(audio_files)}\n")
    
    results = []
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"[{i}/{len(audio_files)}] Procesando: {os.path.basename(audio_file)}")
        
        try:
            # Cargar audio
            audio, sr = librosa.load(audio_file, sr=detector.sample_rate, mono=True)
            
            # Predecir
            prediction = detector.predict(audio)
            prediction['filename'] = os.path.basename(audio_file)
            results.append(prediction)
            
            # Mostrar resultado
            label = prediction['label']
            conf = prediction['confidence']
            print(f"   → {label} (confianza: {conf:.2%})\n")
        
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            continue
    
    # Resumen
    print("\n" + "=" * 70)
    print("  📊 RESUMEN")
    print("=" * 70)
    
    if len(results) == 0:
        print("\n⚠️  No se procesaron archivos correctamente\n")
        return
    
    human_count = sum(1 for r in results if r['is_human'])
    deepfake_count = len(results) - human_count
    
    print(f"\n✅ Humanos detectados:   {human_count}/{len(results)} ({human_count/len(results)*100:.1f}%)")
    print(f"⚠️  Deepfakes detectados: {deepfake_count}/{len(results)} ({deepfake_count/len(results)*100:.1f}%)")
    print(f"\n🎯 Confianza promedio: {np.mean([r['confidence'] for r in results]):.2%}\n")
    
    # Guardar resultados
    if save_results:
        import json
        output_file = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Resultados guardados en: {output_file}\n")


def main():
    parser = argparse.ArgumentParser(
        description='🎤 Detección de Deepfakes en Tiempo Real',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Modo interactivo (por defecto)
  python src/realtime/realtime_detection.py --model models/aasist_fine_tuned/best_model.pth

  # Grabar y guardar muestras
  python src/realtime/realtime_detection.py --model models/aasist_fine_tuned/best_model.pth --save

  # Grabaciones de 5 segundos
  python src/realtime/realtime_detection.py --model models/aasist_fine_tuned/best_model.pth --duration 5

  # Analizar archivos existentes
  python src/realtime/realtime_detection.py --model models/aasist_fine_tuned/best_model.pth --files audio1.wav audio2.wav
        """
    )
    
    parser.add_argument('--model', type=str, 
                        default='models/aasist_fine_tuned/best_model.pth',
                        help='Ruta al modelo fine-tuned')
    parser.add_argument('--duration', type=float, default=3.0,
                        help='Duración de grabación en segundos (default: 3)')
    parser.add_argument('--save', action='store_true',
                        help='Guardar muestras grabadas')
    parser.add_argument('--files', nargs='+', type=str,
                        help='Archivos de audio para modo batch')
    parser.add_argument('--device', type=str, default='cpu',
                        choices=['cpu', 'cuda'],
                        help='Device (cpu o cuda)')
    
    args = parser.parse_args()
    
    # Verificar que existe el modelo
    if not os.path.exists(args.model):
        print(f"❌ Error: No se encuentra el modelo en {args.model}")
        print(f"\n💡 Asegúrate de haber ejecutado el fine-tuning primero:")
        print(f"   python src/training/train_aasist.py --csv data/metadata_processed.csv")
        return
    
    # Crear detector
    detector = RealtimeDetector(args.model, device=args.device)
    
    # Modo batch o interactivo
    if args.files:
        batch_mode(detector, args.files, save_results=True)
    else:
        interactive_mode(detector, duration=args.duration, save_samples=args.save)


if __name__ == '__main__':
    main()
