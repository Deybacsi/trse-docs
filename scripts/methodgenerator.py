import os
import re

INPUT_FILE = "assets/methods_list.txt"
OUTPUT_FOLDER = "../reference/methods"
CATEGORY_FOLDER = "../reference/categories"
REFERENCE_README = "../reference/README.md"

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

def sanitize_filename(name):
    """
    Converts a method or category name into a valid filename by replacing spaces and special characters.
    """
    return re.sub(r"[^\w\-]", "_", name.replace(" ", "_").lower())

def generate_method_file(method, output_folder, existing_files):
    """
    Generates a Markdown file for a single method with inline properties in the header.
    Handles duplicate filenames by appending a unique identifier.
    """
    sanitized_name = sanitize_filename(method['name'])
    filename = f"{sanitized_name}.md"
    filepath = os.path.join(output_folder, filename)

    # Handle duplicate filenames
    counter = 1
    while filename in existing_files:
        filename = f"{sanitized_name}_{counter}.md"
        filepath = os.path.join(output_folder, filename)
        counter += 1

    existing_files.add(filename)  # Track generated filenames

    content = f"""# {method['name']}

**Parameters:** {method['params']}  
**Category:** {method['category']}  
**Compatibility:** {method['compatibility']}  

**Reference Link:**  
[Back to Methods List](../../SUMMARY.md)
"""
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)

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

def update_reference_readme(methods, categories, readme_path):
    """
    Updates the reference README.md file with links to all generated files.
    """
    lines = ["# Reference Documentation\n"]
    lines.append("## Methods\n")
    for method in methods:
        method_file = f"methods/{method['name']}.md"
        lines.append(f"- [{method['name']}]({method_file})")
    lines.append("\n## Categories\n")
    for category in categories:
        category_file = f"categories/{sanitize_filename(category)}.md"
        lines.append(f"- [{category}]({category_file})")
    with open(readme_path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

def main():
    # Ensure the output folders exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(CATEGORY_FOLDER, exist_ok=True)

    # Read methods list
    methods = read_methods_list(INPUT_FILE)

    # Generate files for each method
    existing_files = set()
    skipped_methods = []
    for method in methods:
        try:
            generate_method_file(method, OUTPUT_FOLDER, existing_files)
        except Exception as e:
            skipped_methods.append((method['name'], str(e)))

    # Generate files for each category
    categories = {method['category'] for method in methods}
    generate_category_files(methods, CATEGORY_FOLDER, "../methods")

    # Update the reference README.md
    update_reference_readme(methods, categories, REFERENCE_README)

    # Log skipped methods
    if skipped_methods:
        print(f"Skipped {len(skipped_methods)} methods due to errors:")
        for name, error in skipped_methods:
            print(f"- {name}: {error}")

    print(f"Generated {len(existing_files)} method files in '{OUTPUT_FOLDER}'.")
    print(f"Generated category files in '{CATEGORY_FOLDER}'.")
    print(f"Updated reference README.md at '{REFERENCE_README}'.")

if __name__ == "__main__":
    main()
