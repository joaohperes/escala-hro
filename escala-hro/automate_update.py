#!/usr/bin/env python3
"""
Script de automação para atualizar escala diariamente
1. Extrai dados da escala
2. Gera o dashboard HTML
3. Faz commit e push para GitHub Pages
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, description):
    """Executa um comando e retorna o resultado"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    print(f"Comando: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Função principal de automação"""

    print(f"""
    ╔════════════════════════════════════════════════════════╗
    ║   AUTOMAÇÃO DE ATUALIZAÇÃO DE ESCALA - HRO            ║
    ║   Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}                    ║
    ╚════════════════════════════════════════════════════════╝
    """)

    # Diretório do projeto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    steps = [
        ("Extração de dados", ["python3", "extracao_3_datas.py"]),
        ("Geração do dashboard", ["python3", "gerar_dashboard_executivo.py"]),
    ]

    for description, cmd in steps:
        if not run_command(cmd, description):
            print(f"\n❌ Falha em: {description}")
            print("⏹️  Parando automação")
            return False

    # Atualizar o arquivo de GitHub Pages
    print(f"\n{'='*60}")
    print("📌 Atualizando repositório GitHub Pages")
    print(f"{'='*60}\n")

    github_pages_dir = "escala-hro/escala-hro"
    if os.path.exists(github_pages_dir):
        # Copiar arquivo gerado
        if not run_command(["cp", "index.html", f"{github_pages_dir}/index.html"],
                          "Copiando HTML para GitHub Pages"):
            return False
    else:
        print(f"⚠️  Diretório {github_pages_dir} não encontrado")
        print("Pulando cópia de arquivos")

    # Fazer commit e push
    os.chdir(github_pages_dir)

    commands = [
        (["git", "add", "index.html", "last-update.txt"], "Adicionando arquivos ao git"),
        (["git", "commit", "-m", f"Atualização automática - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"],
         "Criando commit"),
        (["git", "push", "origin", "main"], "Fazendo push para GitHub"),
    ]

    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print(f"⚠️  Falha em: {desc} (pode ser normal se não há mudanças)")

    print(f"""
    ╔════════════════════════════════════════════════════════╗
    ║   ✅ AUTOMAÇÃO CONCLUÍDA COM SUCESSO                  ║
    ║   Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}                    ║
    ║   Página: https://joaohperes.github.io/escala-hro/    ║
    ╚════════════════════════════════════════════════════════╝
    """)

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
