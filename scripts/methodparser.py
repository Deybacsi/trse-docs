# TRSE method parser script
import os
import re
import requests

# --- 1. Download (if needed) ---
def download_file(url, dest_folder, filename):
    """
    Downloads a file from a URL to a given folder.
    """
    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, filename)
    r = requests.get(url)
    r.raise_for_status()
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(r.text)
    return dest_path

# --- 2. Parameter decoding ---
PARAM_MAP = {
    's': 'string', 'b': 'byte', 'i': 'integer', 'a': 'address',
    'n': 'number', 'ib': 'integer or byte', 'p': 'procedure', 'ai': 'address or integer', 'l': 'long'
}
def decode_params(paramstr):
    """
    Converts short parameter codes to human-readable strings.
    """
    if not paramstr.strip():
        return ''
    params = [p.strip() for p in paramstr.split(',')]
    readable = []
    for p in params:
        val = PARAM_MAP.get(p, p)
        readable.append(val)
    return ', '.join(readable)

# --- 3. File parsing ---
def parse_methods(filepath):
    """
    Parses the syntax.txt file and extracts all methods.
    Returns a list of dictionaries: name, category, compatibility, params.
    If the folder in the filepath does not exist, it will be created automatically.
    """
    # Ensure the folder exists
    folder = os.path.dirname(filepath)
    if folder and folder != '' and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    methods = []
    current_section = ''
    """
    Parses the syntax.txt file and extracts all methods.
    Returns a list of dictionaries: name, category, compatibility, params.
    """
    methods = []
    current_section = ''
    section_re = re.compile(r"^#*\s*([\w\s\*]+ROUTINES|functions|methods|routines|INIT METHODS|CALL METHODS|STUFF|IRQ routines|IO ports|Screen routines|Math routines|Other routines|Sound/Music routines|Sprite routines|Charset routines)", re.I)
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            # Section/category detection
            sec = section_re.search(line)
            if sec:
                current_section = sec.group(1).strip().capitalize()
            # Only method lines (m; ...)
            if line.startswith('m;') or line.startswith('M;'):
                parts = line.split(';')
                if len(parts) < 3:
                    continue
                name = parts[1].strip()
                compatibility = parts[2].strip()
                params = parts[3].strip() if len(parts) > 3 else ''
                methods.append({
                    'name': name,
                    'category': current_section,
                    'compatibility': compatibility,
                    'params': decode_params(params)
                })
    return methods

# --- 4. Output formatting ---
def methods_to_list(methods, sep='; '):
    """
    Formats the method list into a string, with one method per line.
    """
    lines = []
    for m in methods:
        lines.append(f"{m['name']}{sep}{m['category']}{sep}{m['compatibility']}{sep}{m['params']}")
    return '\n'.join(lines)

# --- 5. Example main program ---
if __name__ == "__main__":
    url = "https://github.com/leuat/TRSE/raw/master/resources/text/syntax.txt"
    file_path = download_file(url, "assets", "syntax.txt")
    methods = parse_methods(file_path)
    print(methods_to_list(methods))
