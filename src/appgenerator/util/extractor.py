import os
import re
import markdown
from xhtml2pdf import pisa

def extract_code(text : str, file_type : str) -> str:
    """
    Extracts the source code of a specified file type from LLM-generated text.

    This function looks for code enclosed between triple backticks (```) with an optional
    language identifier (e.g., `python`, `javascript`). It first attempts to extract code
    enclosed with the given file type, and if it fails, it tries to extract any enclosed code.

    @param text: The input text generated by the LLM that potentially contains code.
    @param file_type: The expected type of code to extract (e.g., 'python', 'javascript').

    @return: The extracted code block from the text.

    @raise ValueError: If no code block is found in the provided text.
    """
    match = re.search(r'```' + file_type + r'(.*)```', text, re.DOTALL)
    if match == None:
        match = re.search(r'```(.*)```', text, re.DOTALL)
    if match == None:
        raise ValueError(f'No source code found in the provided text.')
    return match.group(1)


def extract_imports_from_file(file_path):
    """
    Extracts all imports from a given Python file.

    This function reads the provided Python file line by line and uses regular expressions
    to find import statements. It filters out standard library imports and certain
    predefined internal modules.

    @param file_path: Path to the Python file from which imports are to be extracted.

    @return: A set of unique package names imported in the file.
    """
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
    """
    Extracts all imports from Python files in the specified directory.

    This function recursively traverses the directory, identifies Python files,
    and aggregates the imports found in each file.

    @param directory: The directory path to search for Python files.

    @return: A set of unique imports from all Python files within the directory.
    """
    all_imports = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                all_imports.update(extract_imports_from_file(file_path))
    return all_imports


def extract_pdf_from_markdown(md_content: str, output_path: str) -> None:
    # Define CSS styles
    styles = """
    <style>
    body {
        font-family: Arial, sans-serif;
        font-size: 12pt;
    }
    pre {
        background-color: #f5f5f5;
        padding: 10px;
        border: 1px solid #e0e0e0;
        overflow: auto;
    }
    code {
        font-family: Courier, monospace;
    }
    ul, ol {
        margin-left: 20px;
    }
    li {
        margin-bottom: 5px;
    }
    </style>
    """

    # Convert Markdown to HTML with extensions
    html_body = markdown.markdown(
        md_content,
        extensions=['fenced_code']
    )

    # Combine styles and HTML body
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        {styles}
    </head>
    <body>{html_body}</body>
    </html>
    """

    # Convert HTML to PDF
    with open(output_path, 'wb') as pdf_file:
        pisa_status = pisa.CreatePDF(
            html_content,
            dest=pdf_file
        )
