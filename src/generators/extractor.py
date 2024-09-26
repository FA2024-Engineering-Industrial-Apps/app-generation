import os
import re


def extract_imports_from_file(file_path):
    """Extract all imports from a given Python file."""
    imports = set()
    with open(file_path, 'r') as file:
        for line in file:
            # Match regular import statements: import x or from x import y
            match = re.match(r'^\s*(import|from)\s+([\w\.]+)', line)
            if match:
                package_name = match.group(2).split('.')[0]
                if package_name not in ['backend', 'mqtt_lib', 'server', "flask", "paho"]:
                    imports.add(package_name)
    return imports

def extract_imports_from_directory(directory):
    """Extract imports from all Python files in the given directory."""
    all_imports = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                all_imports.update(extract_imports_from_file(file_path))
    return all_imports

def write_requirements_txt(imports, output_file='requirements.txt'):
    """Write the collected imports to a requirements.txt file."""
    with open(output_file, 'w') as f:
        for module in sorted(imports):
            f.write(f"{module}\n")

if __name__ == "__main__":
    directory = "./"
    imports = extract_imports_from_directory(directory)
    write_requirements_txt(imports)
