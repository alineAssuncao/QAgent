import os
import yaml
import re

def _parse_skill_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL | re.MULTILINE)
            if match:
                yaml_content = match.group(1)
                yaml.safe_load(yaml_content)
                return "OK"
            else:
                return "REGEX_FAIL"
    except Exception as e:
        return f"ERROR: {str(e)}"

skills_dir = "agents/skills"
for folder in sorted(os.listdir(skills_dir)):
    fp = os.path.join(skills_dir, folder, "SKILL.md")
    if os.path.exists(fp):
        res = _parse_skill_file(fp)
        print(f"{folder}: {res}")
