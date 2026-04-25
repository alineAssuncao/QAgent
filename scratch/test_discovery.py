import glob
import os

repo_path = "projects/python-simple-rest-api"
base_dir = os.path.abspath(".")
repo_abs = os.path.abspath(repo_path)

all_py = glob.glob(os.path.join(repo_abs, "**", "*.py"), recursive=True)

exclude = ["test", "__init__", "setup", "conftest", "manage", 
    "migration", "wsgi", "asgi", "__pycache__", ".git",
    "docs", "examples", "venv", "node_modules"]

valid = []
for f in all_py:
    full_lower = f.lower().replace("\\", "/")
    if any(pat in full_lower for pat in exclude):
        continue
    rel = os.path.relpath(f, base_dir).replace("\\", "/")
    valid.append(rel)
    
print(f"Arquivos encontrados: {len(valid)}")
for v in valid:
    print(f"  - {v}")
