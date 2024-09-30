import os
import subprocess
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a log directory for linting if needed
lint_log_dir = 'artifacts/lint_logs'
os.makedirs(lint_log_dir, exist_ok=True)

def log_to_file(file_path, message):
    # Log messages to the respective file
    with open(file_path, 'a') as log_file:
        log_file.write(message + '\n')

def run_pylint_on_artifacts():
    # Define paths to directories
    static_dir = 'artifacts/preview/static'
    templates_dir = 'artifacts/preview/templates'
    
    # Linting function for different file types
    def lint_file(linter_command, file_path):
        logger.info(f'Running linter on {file_path}')
        try:
            result = subprocess.run(linter_command, capture_output=True, text=True)
            log_message = f"Results for {file_path}:\n{result.stdout}"
            if result.stderr:
                log_message += f"\nErrors:\n{result.stderr}"
            if result.returncode != 0:
                logger.error(f'Linter failed for {file_path} with error: {result.stderr}')
                
            # Determine the log file path based on the linter used
            if 'eslint' in linter_command[0]:  # JavaScript
                log_to_file(os.path.join(lint_log_dir, 'js.log'), log_message)
            elif 'stylelint' in linter_command[0]:  # CSS
                log_to_file(os.path.join(lint_log_dir, 'css.log'), log_message)
            elif 'htmlhint' in linter_command[0]:  # HTML
                log_to_file(os.path.join(lint_log_dir, 'html.log'), log_message)

        except Exception as e:
            logger.error(f'Error running linter on {file_path}: {e}')

    # Run eslint on JavaScript files
    for file_name in os.listdir(static_dir):
        if file_name.endswith('.js'):
            file_path = os.path.join(static_dir, file_name)
            lint_file(['eslint', file_path], file_path)

    # Run stylelint on CSS files
    for file_name in os.listdir(static_dir):
        if file_name.endswith('.css'):
            file_path = os.path.join(static_dir, file_name)
            lint_file(['stylelint', file_path], file_path)

    # Run htmlhint on HTML files
    for file_name in os.listdir(templates_dir):
        if file_name.endswith('.html'):
            file_path = os.path.join(templates_dir, file_name)
            lint_file(['htmlhint', file_path], file_path)

if __name__ == "__main__":
    run_pylint_on_artifacts()