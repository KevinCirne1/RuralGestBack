# Script para gerar um dump formatado apenas dos arquivos desejados
import os
from pathlib import Path
import fnmatch

ROOT_PATH = Path("/home/matheusserafim/RuralGestBack")
OUT_FILE = ROOT_PATH / "project_dump_filtered.txt"

# diretórios e padrões que queremos incluir
INCLUDE_DIRS = {"helpers", "models", "resources"}
ROOT_PATTERNS = ["schemas*", "commands*", ".env", "app.config", "requirements*", "requeriments*", ".gitignore"]

# diretórios a excluir explicitamente
EXCLUDE_DIRS = {".venv", ".vscode", "migrations", "venv", "env", "__pycache__"}

files = []
for root, dirs, filenames in os.walk(ROOT_PATH):
    # normalizar e pular dirs excluídos
    root_path = Path(root)
    if any(part in EXCLUDE_DIRS for part in root_path.parts):
        continue

    rel_root = root_path.relative_to(ROOT_PATH)
    # incluir arquivos dentro de helpers|models|resources
    if len(rel_root.parts) > 0 and rel_root.parts[0] in INCLUDE_DIRS:
        for fname in filenames:
            files.append(root_path / fname)
        continue

    # incluir arquivos na raiz que batam nos padrões
    if root_path == ROOT_PATH:
        for fname in filenames:
            for pat in ROOT_PATTERNS:
                if fnmatch.fnmatch(fname.lower(), pat.lower()) or fnmatch.fnmatch(fname, pat):
                    files.append(root_path / fname)
                    break

# ordenar e escrever saída no mesmo estilo do seu exemplo
files = sorted(set(files))
with OUT_FILE.open("w", encoding="utf-8", errors="replace") as out:
    for i, f in enumerate(files, start=1):
        rel = f.relative_to(ROOT_PATH)
        out.write("# " + "="*77 + "\n")
        out.write(f"# FICHEIRO {i}: {rel}\n")
        out.write("# " + "="*77 + "\n")
        out.write(f"```python:{f.name}:{rel}\n")
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            text = f"# ERRO AO LER O ARQUIVO: {e}\n"
        out.write(text)
        if not text.endswith("\n"):
            out.write("\n")
        out.write("```eof\n\n")

print(f"Gerado: {OUT_FILE}")