#!/usr/bin/env python3
"""Fix Markdown lint errors in documentation files."""

import re
import os

def fix_markdown_file(filename):
    """Fix common Markdown lint errors in a file."""
    if not os.path.exists(filename):
        print(f"⏭️  Skip: {filename} (not found)")
        return False
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix MD022: Headings should be surrounded by blank lines
    # Aggiungi riga vuota dopo heading se seguita da lista
    content = re.sub(r'(^###? .*$)\n(- )', r'\1\n\n\2', content, flags=re.MULTILINE)
    
    # Fix MD032: Lists should be surrounded by blank lines
    lines = content.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        # Aggiungi blank line prima di lista se manca
        if (line.strip().startswith('- ') and 
            i > 0 and 
            fixed_lines and 
            fixed_lines[-1].strip() and
            not fixed_lines[-1].strip().startswith('-') and
            not fixed_lines[-1].strip().startswith('#') and
            not fixed_lines[-1] == ''):
            fixed_lines.append('')
        
        fixed_lines.append(line)
        
        # Aggiungi blank line dopo lista se manca
        if (line.strip().startswith('- ') and 
            i < len(lines) - 1 and 
            lines[i+1].strip() and
            not lines[i+1].strip().startswith('- ') and
            not lines[i+1].startswith('  ') and
            not lines[i+1].startswith('#')):
            fixed_lines.append('')
    content = '\n'.join(fixed_lines)
    
    # Fix MD031: Fenced code blocks should be surrounded by blank lines
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check if starting code block
        if stripped.startswith('```') and not in_code_block:
            # Add blank line before if needed
            if i > 0 and fixed_lines and fixed_lines[-1].strip():
                fixed_lines.append('')
            fixed_lines.append(line)
            in_code_block = True
            continue
        
        # Check if ending code block
        if stripped.startswith('```') and in_code_block:
            fixed_lines.append(line)
            # Add blank line after if needed
            if i < len(lines) - 1 and lines[i+1].strip():
                fixed_lines.append('')
            in_code_block = False
            continue
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Fix MD034: Bare URLs should be wrapped in < >
    # Solo per URL non già in markdown link
    content = re.sub(r'^```\n(\S)', r'```text\n\1', content, flags=re.MULTILINE)
    
    # Fix indented code blocks (need language)
    content = re.sub(r'(   )```\n', r'\1```bash\n', content)
    def replace_url(match):
        url = match.group(0)
        # Non sostituire se già in link markdown [text](url)
        return f'<{url}>'
    
    # Match URL solo se non preceduta da ( e non seguita da )
    content = re.sub(r'(?<!\()(https?://[^\s\)]+)(?!\))', replace_url, content)
    
    # Fix MD040: Fenced code blocks should have a language specified
    # Find all table separator lines and fix them
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Match table separator line like |---|---|---|
        if '|' in line and re.search(r'-{2,}', line):
            # Split by pipe, keeping empty strings
            parts = line.split('|')
            # Process each part
            fixed_parts = []
            for part in parts:
                stripped = part.strip()
                # If it's a dash sequence, add spaces
                if stripped and re.match(r'^-+$', stripped):
                    fixed_parts.append(f' {stripped} ')
                else:
                    fixed_parts.append(part)
            lines[i] = '|'.join(fixed_parts)
    content = '\n'.join(lines)
    
    # Fix indented code blocks
    lines = content.split('\n')
    fixed_lines = []
    in_list = False
    for i, line in enumerate(lines):
        # Detect if we're in a numbered/bullet list context
        if line.strip() and (line.lstrip().startswith(('1. ', '- '))):
            in_list = True
        elif line.strip() and not line.startswith((' ', '\t')):
            in_list = False
        
        # Fix indented code blocks (3+ spaces + ```)
        if in_list and re.match(r'^   ```\s*$', line):
            # Add blank line before if needed
            if i > 0 and fixed_lines and fixed_lines[-1].strip():
                fixed_lines.append('')
            # Add language if missing
            if i < len(lines) - 1 and lines[i+1].strip():
                line = '   ```bash'
            fixed_lines.append(line)
            # Check if we need blank line after closing ```
            if i < len(lines) - 2:
                next_line = lines[i+1]
                # Find closing ```
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip() == '```':
                        # If next line after ``` has content, add blank
                        if j < len(lines) - 1 and lines[j+1].strip():
                            lines[j] = lines[j] + '\n'
                        break
        else:
            fixed_lines.append(line)
    content = '\n'.join(fixed_lines)
    
    if content != original_content:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✅ Fixed: {filename}')
        return True
    else:
        print(f'⏭️  No changes needed: {filename}')
        return False

if __name__ == '__main__':
    files_to_fix = [
        'WORKFLOW_AGGIORNAMENTO.md',
        'GUIDA_OPERATIVA_FASE1.md',
        'FASE1_QUICK_START.md',
        'FASE1_IMPLEMENTATA.md',
        'FASE1_DEPLOY_STATUS.md',
        'WORKFLOW_FASE1_COMPLETO.md',
        'PRODUCTION_READY.md',
        'MIGLIORAMENTI_IMPLEMENTATI.md',
        'README.md',
        'CERTIFICAZIONE_DATI_REALI.md',
        'DEPLOY_RENDER.md',
        'RENDER_FREE_TIER_SETUP.md',
        'VERIFICA_STATO.md',
        'RIEPILOGO_OTTIMIZZAZIONE.md',
        'REPORT_PRESENTAZIONE.md'
    ]
    
    fixed_count = 0
    for filename in files_to_fix:
        if fix_markdown_file(filename):
            fixed_count += 1
    
    print(f'\n📊 Summary: Fixed {fixed_count}/{len(files_to_fix)} files')
