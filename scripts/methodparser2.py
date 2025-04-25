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

# --- 4. Documentation file matching ---
def get_rtf_files_from_github(url):
    """
    Downloads the GitHub HTML directory page and extracts .rtf filenames.
    Returns a set of method names (without .rtf extension) that have documentation.
    """
    import re
    r = requests.get(url)
    r.raise_for_status()
    # Extract all .rtf filenames
    files = set()
    for match in re.findall(r'href=["\'].*?/m/([a-zA-Z0-9_]+)\.rtf["\']', r.text):
        files.add(match)
    return files

# --- 5. Output formatting ---
def methods_to_list(methods, doc_methods=None, sep='; '):
    """
    Formats the method list into a string, with one method per line.
    If doc_methods is given (set of method names), an extra column is added with the doc link or empty.
    """
    lines = []
    for m in methods:
        doc_link = ''
        if doc_methods and m['name'] in doc_methods:
            doc_link = f"https://github.com/leuat/TRSE/raw/master/resources/text/help/m/{m['name']}.rtf"
        lines.append(f"{m['name']}{sep}{m['category']}{sep}{m['compatibility']}{sep}{m['params']}{sep}{doc_link}")
    return '\n'.join(lines)

# --- 6. Example main program ---
if __name__ == "__main__":
    url = "https://github.com/leuat/TRSE/raw/master/resources/text/syntax.txt"
    file_path = download_file(url, "assets", "syntax.txt")
    methods = parse_methods(file_path)

    doc_page_url = "https://github.com/leuat/TRSE/tree/master/resources/text/help/m"
    doc_methods = get_rtf_files_from_github(doc_page_url)
    print(methods_to_list(methods, doc_methods))
