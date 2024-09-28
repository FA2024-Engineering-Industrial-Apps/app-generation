import os
import re


def extract_code(text : str, file_type : str) -> str:
    """
        Extracts the source code of a file with the given type from an LLM generated text.
        
        Returns the code between ```file_type and ``` of the input text. LLM's typically output code enclosed in this way.
        Attempts to extract the code between ``` and ``` if the previous extraction failed.
        
        @raise: ValueError If parsing fails.
    """
    match = re.search(r'```' + file_type + r'(.*)```', text, re.DOTALL)
    if match == None:
        match = re.search(r'```(.*)```', text, re.DOTALL)
    if match == None:
        raise ValueError(f'No source code found in the provided text.')
    return match.group(1)

def extract_imports_from_file(file_path):
    """Extract all imports from a given Python file."""
    imports = set()
    with open(file_path, 'r', encoding="utf8") as file:
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
