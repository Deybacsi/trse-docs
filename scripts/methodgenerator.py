import os
import re
import shutil

INPUT_FILE = "assets/methods_list.txt"
OUTPUT_FOLDER = "../reference/methods"
CATEGORY_FOLDER = "../reference/categories"
REFERENCE_README = "../reference/README.md"

def read_methods_list(filepath):
    """
    Reads the methods list from the input file.
    Ensures all 5 columns (name, category, compatibility, params, URL) are handled.
    """
    methods = []
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split("; ")
            # Ensure exactly 5 columns, filling missing ones with empty strings
            while len(parts) < 5:
                parts.append('')
            methods.append({
                "name": parts[0],
                "category": parts[1],
                "compatibility": parts[2],
                "params": parts[3],
                "url": parts[4]  # Store the URL if present
            })
    return methods

def sanitize_filename(name):
    """
    Converts a method or category name into a valid filename by replacing spaces and special characters.
    """
    return re.sub(r"[^\w\-]", "_", name.replace(" ", "_").lower())

def clear_folder(folder_path):
    """
    Deletes all files and subfolders in the specified folder.
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)

def generate_method_file(method, output_folder, existing_files):
    """
    Generates a Markdown file for a single method with inline properties in the header.
    Handles duplicate filenames by appending a unique identifier.
    Includes the optional URL as a link if present.
    Makes the category a clickable link to its category page.
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

    # Add the optional URL as a link if present
    url_section = f"\n**Documentation Link:** [View Documentation]({method['url']})" if method['url'] else ""

    # Make the category a clickable link
    category_link = f"[{method['category']}](../categories/{sanitize_filename(method['category'])}.md)"

    content = f"""# {method['name']}

**Parameters:** {method['params']}  
**Category:** {category_link}  
**Compatibility:** {method['compatibility']}  
{url_section}

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
            method_file = f"../methods/{sanitize_filename(method['name'])}.md"
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
        method_file = f"methods/{sanitize_filename(method['name'])}.md"
        lines.append(f"- [{method['name']}]({method_file})")
    lines.append("\n## Categories\n")
    for category in categories:
        category_file = f"categories/{sanitize_filename(category)}.md"
        lines.append(f"- [{category}]({category_file})")
    with open(readme_path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

def list_folder_contents(folder_path):
    """
    Lists the contents of a folder and counts the number of files.
    """
    if not os.path.exists(folder_path):
        return [], 0
    files = os.listdir(folder_path)
    return files, len(files)

def main():
    # Clear output folders
    clear_folder(OUTPUT_FOLDER)
    clear_folder(CATEGORY_FOLDER)

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

    # List folder contents and compare counts
    method_files, method_count = list_folder_contents(OUTPUT_FOLDER)
    category_files, category_count = list_folder_contents(CATEGORY_FOLDER)

    print("\nFolder Contents:")
    print(f"Methods Folder ({OUTPUT_FOLDER}): {method_count} files")
    print(f"Categories Folder ({CATEGORY_FOLDER}): {category_count} files")

    print("\nComparison:")
    print(f"Total methods in list: {len(methods)}")
    print(f"Total categories in list: {len(categories)}")
    print(f"Generated method files: {method_count}")
    print(f"Generated category files: {category_count}")

    if method_count != len(methods):
        print(f"Warning: Mismatch in method files ({method_count}) and methods in list ({len(methods)})!")
    if category_count != len(categories):
        print(f"Warning: Mismatch in category files ({category_count}) and categories in list ({len(categories)})!")

    print(f"\nUpdated reference README.md at '{REFERENCE_README}'.")

if __name__ == "__main__":
    main()
