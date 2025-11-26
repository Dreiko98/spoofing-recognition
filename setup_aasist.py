#!/usr/bin/env python3
"""
Descarga e integra el modelo AASIST pre-entrenado desde el repositorio oficial

Este script:
1. Clona el repo oficial de AASIST
2. Descarga el modelo pre-entrenado
3. Prepara todo para usar con nuestro dataset
"""

import os
import subprocess
from pathlib import Path
import urllib.request
import shutil


def run_command(cmd, cwd=None):
    """Ejecuta un comando y muestra el output"""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    return True


def main():
    print("=" * 70)
    print("    🔽 DESCARGANDO E INTEGRANDO AASIST")
    print("=" * 70)
    print()

    base_dir = Path.cwd()
    models_dir = base_dir / "models"
    models_dir.mkdir(exist_ok=True)

    # 1. Clonar repositorio oficial de AASIST
    aasist_repo = models_dir / "AASIST"
    
    if not aasist_repo.exists():
        print("📥 Clonando repositorio oficial de AASIST...")
        print("   Repo: https://github.com/clovaai/aasist")
        print()
        
        if not run_command(
            "git clone https://github.com/clovaai/aasist.git AASIST",
            cwd=models_dir
        ):
            print("\n❌ Error clonando repositorio")
            print("💡 Intenta manualmente:")
            print("   cd models && git clone https://github.com/clovaai/aasist.git")
            return
    else:
        print("✅ Repositorio AASIST ya existe")
    
    # 2. Descargar modelo pre-entrenado
    print("\n📥 Descargando modelo pre-entrenado...")
    print("   Modelo: AASIST entrenado en ASVspoof 2019 LA")
    print()
    
    # URL del modelo pre-entrenado (del repo oficial)
    model_url = "https://github.com/clovaai/aasist/releases/download/v1.0/AASIST.pth"
    model_path = aasist_repo / "pretrained" / "AASIST.pth"
    model_path.parent.mkdir(exist_ok=True)
    
    if not model_path.exists():
        print(f"   Descargando desde: {model_url}")
        try:
            urllib.request.urlretrieve(model_url, model_path)
            print(f"   ✅ Descargado: {model_path}")
        except Exception as e:
            print(f"   ❌ Error descargando: {e}")
            print("\n   💡 Descárgalo manualmente:")
            print(f"      wget {model_url} -O {model_path}")
            return
    else:
        print(f"   ✅ Modelo ya descargado: {model_path}")
    
    # 3. Copiar archivos necesarios a nuestro proyecto
    print("\n📋 Integrando AASIST en el proyecto...")
    
    # Copiar model.py
    src_model = aasist_repo / "models" / "AASIST.py"
    dst_model = base_dir / "src" / "models" / "AASIST.py"
    dst_model.parent.mkdir(exist_ok=True, parents=True)
    
    if src_model.exists():
        shutil.copy2(src_model, dst_model)
        print(f"   ✅ Copiado: {dst_model.name}")
    else:
        print(f"   ⚠️  No encontrado: {src_model}")
    
    # Copiar RawNet3.py (dependencia de AASIST)
    src_rawnet = aasist_repo / "models" / "RawNet3.py"
    dst_rawnet = base_dir / "src" / "models" / "RawNet3.py"
    
    if src_rawnet.exists():
        shutil.copy2(src_rawnet, dst_rawnet)
        print(f"   ✅ Copiado: {dst_rawnet.name}")
    
    # Crear __init__.py
    init_file = dst_model.parent / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Models package\n")
        print(f"   ✅ Creado: __init__.py")
    
    print("\n" + "=" * 70)
    print("✅ AASIST INTEGRADO CORRECTAMENTE")
    print("=" * 70)
    print()
    print("📁 Archivos importantes:")
    print(f"   • Modelo pre-entrenado: {model_path}")
    print(f"   • Código del modelo:    {dst_model}")
    print()
    print("=" * 70)
    print("🎯 PRÓXIMO PASO:")
    print("=" * 70)
    print()
    print("Opción 1 - Probar modelo pre-entrenado:")
    print("   python src/evaluation/evaluate_pretrained.py \\")
    print("       --model models/AASIST/pretrained/AASIST.pth \\")
    print("       --csv data/metadata_processed.csv")
    print()
    print("Opción 2 - Fine-tuning con tu dataset:")
    print("   python src/training/train_aasist.py \\")
    print("       --csv data/metadata_processed.csv \\")
    print("       --pretrained models/AASIST/pretrained/AASIST.pth \\")
    print("       --output_dir models/aasist_custom")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
