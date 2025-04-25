import os
import re

INPUT_FILE = "assets/methods_list.txt"
OUTPUT_FOLDER = "../reference/methods"
CATEGORY_FOLDER = "../reference/categories"

def read_methods_list(filepath):
    """
    Reads the methods list from the input file.
    """
    methods = []
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split("; ")
            if len(parts) == 4:
                methods.append({
                    "name": parts[0],
                    "category": parts[1],
                    "compatibility": parts[2],
                    "params": parts[3]
                })
    return methods

def generate_method_file(method, output_folder):
    """
    Generates a Markdown file for a single method with inline properties in the header.
    """
    filename = f"{method['name']}.md"
    filepath = os.path.join(output_folder, filename)
    content = f"""# {method['name']}

**Parameters:** {method['params']}  
**Category:** {method['category']}  
**Compatibility:** {method['compatibility']}  

**Reference Link:**  
[Back to Methods List](../../SUMMARY.md)
"""
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)

def sanitize_filename(name):
    """
    Converts a category name into a valid filename by replacing spaces and special characters.
    """
    return re.sub(r"[^\w\-]", "_", name.replace(" ", "_").lower())

def generate_category_files(methods, category_folder, method_folder):
    """
    Generates a Markdown file for each category, listing all methods in that category.
    """
    os.makedirs(category_folder, exist_ok=True)
    categories = {}
    for method in methods:
        category = method['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(method)

    for category, methods in categories.items():
        filename = f"{sanitize_filename(category)}.md"
        filepath = os.path.join(category_folder, filename)
        lines = [f"# {category}\n"]
        for method in methods:
            method_file = f"{method_folder}/{method['name']}.md"
            lines.append(f"- [{method['name']}]({method_file})")
        with open(filepath, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

def main():
    # Ensure the output folders exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(CATEGORY_FOLDER, exist_ok=True)

    # Read methods list
    methods = read_methods_list(INPUT_FILE)

    # Generate files for each method
    for method in methods:
        generate_method_file(method, OUTPUT_FOLDER)

    # Generate files for each category
    generate_category_files(methods, CATEGORY_FOLDER, "../methods")

    print(f"Generated {len(methods)} method files in '{OUTPUT_FOLDER}'.")
    print(f"Generated category files in '{CATEGORY_FOLDER}'.")

if __name__ == "__main__":
    main()
