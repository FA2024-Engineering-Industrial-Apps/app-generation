import os
import subprocess
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="artifacts/logs/lint/linting.log",
    filemode="w",
    encoding="utf-8",
    level=logging.DEBUG,
    format="[%(asctime)s][%(levelname)s] %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

def run_pylint_on_artifacts():
    # Define paths to directories
    static_dir = 'artifacts/preview/static'
    templates_dir = 'artifacts/preview/templates'
    
    # Create lint log directory if it doesn't exist
    lint_log_dir = 'artifacts/lint_logs'
    os.makedirs(lint_log_dir, exist_ok=True)

    # Linting function for different file types
    def lint_file(linter_command, file_path, log_file_name):
        logger.info(f'Running linter on {file_path}')
        try:
            result = subprocess.run(linter_command, capture_output=True, text=True)
            with open(os.path.join(lint_log_dir, log_file_name), 'w') as log_file:
                log_file.write(result.stdout)
                if result.stderr:
                    log_file.write(result.stderr)
        except Exception as e:
            logger.error(f'Error running linter on {file_path}: {e}')

    # Run eslint on JavaScript files
    for file_name in os.listdir(static_dir):
        if file_name.endswith('.js'):
            file_path = os.path.join(static_dir, file_name)
            lint_file(['eslint', file_path], file_path, f'{file_name}.log')

    # Run stylelint on CSS files
    for file_name in os.listdir(static_dir):
        if file_name.endswith('.css'):
            file_path = os.path.join(static_dir, file_name)
            lint_file(['stylelint', file_path], file_path, f'{file_name}.log')

    # Run htmlhint on HTML files
    for file_name in os.listdir(templates_dir):
        if file_name.endswith('.html'):
            file_path = os.path.join(templates_dir, file_name)
            lint_file(['htmlhint', file_path], file_path, f'{file_name}.log')

if __name__ == "__main__":
    run_pylint_on_artifacts()
