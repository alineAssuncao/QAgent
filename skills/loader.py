import os
import yaml
import logging
import re
from typing import List, Dict, Optional

class SkillLoader:
    def __init__(self, skills_dir: str = "./agents/skills"):
        self.skills_dir = skills_dir
        self.skills = []

    def load_all_skills(self) -> List[Dict[str, Any]]:
        """Varre o diretório de skills em busca de arquivos SKILL.md e carrega os metadados."""
        self.skills = []
        if not os.path.exists(self.skills_dir):
            logging.warning(f"Diretório de skills não encontrado: {self.skills_dir}")
            return []

        for skill_folder in os.listdir(self.skills_dir):
            folder_path = os.path.join(self.skills_dir, skill_folder)
            if os.path.isdir(folder_path):
                skill_file = os.path.join(folder_path, "SKILL.md")
                if os.path.exists(skill_file):
                    skill_data = self._parse_skill_file(skill_file)
                    if skill_data:
                        skill_data['path'] = skill_file
                        self.skills.append(skill_data)
        
        logging.info(f"{len(self.skills)} Skills carregadas com sucesso.")
        return self.skills

    def _parse_skill_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extrai o YAML frontmatter do arquivo SKILL.md."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Regex para capturar conteúdo entre ---
                match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL | re.MULTILINE)
                if match:
                    yaml_content = match.group(1)
                    metadata = yaml.safe_load(yaml_content)
                    
                    # Conteúdo após o frontmatter
                    body = content[match.end():].strip()
                    metadata['full_instruction'] = body
                    return metadata
        except Exception as e:
            logging.error(f"Erro ao ler skill em {file_path}: {e}")
        return None

    def get_skill_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        for skill in self.skills:
            if skill.get('name') == name:
                return skill
        return None
