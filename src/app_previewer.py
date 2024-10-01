from flask import Flask, send_from_directory
import appgenerator.config as config
from appgenerator.generation_instance import GenerationInstance, AppArchitecture
from appgenerator.util.filecopier import FileCopier
import shutil
import os

PREVIEW_SRC_FOLDER = os.path.join('artifacts', 'preview')

server = Flask(__name__)
server_running: bool = False

@server.route('/', methods=['GET'])
def index():
    """
    Renders the index page for the server.

    @return: The rendered 'index.html' template.
    """
    
    return send_from_directory(directory=os.path.join('..', PREVIEW_SRC_FOLDER), path='index.html')


@server.route('/<content>', methods=['GET'])
def files(content):
    """
    Returns the file requested.

    @return: The file requested.
    """
    
    return send_from_directory(directory=os.path.join('..', PREVIEW_SRC_FOLDER), path=content)


@server.route('/static/<content>', methods=['GET'])
def static_files(content):
    """
    Returns the static file requested.

    @return: The static file requested.
    """
    
    return send_from_directory(directory=os.path.join('..', PREVIEW_SRC_FOLDER, 'static'), path=content)


def ensure_empty_folder(folder_path):
    """
    Ensures that the specified folder is empty by removing and recreating it.

    @param folder_path: The path of the folder to be cleared and recreated.
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    os.makedirs(folder_path, exist_ok=True)
    

def start_preview(app: GenerationInstance) -> None:
    """
    Starts the application preview by serving the frontend using a local Flask server.

    This method prepares the necessary files for preview by copying HTML, CSS, and JS files
    into the preview folder and runs the server if it is not already running.

    @param app: The GenerationInstance representing the application to preview.

    @raise Exception: If the application architecture is not frontend-only or frontend-and-backend.
    """
    if app.architecture not in [AppArchitecture.FRONTEND_ONLY, AppArchitecture.FRONTEND_AND_BACKEND]:
        raise Exception("Can't preview headless app.")
    
    ensure_empty_folder(PREVIEW_SRC_FOLDER)
    
    copier: FileCopier = FileCopier(app.root_path)
    copier.copy_and_insert(os.path.join(config.IE_APP_FOLDER_STRUCTURE[app.architecture.value]['html'], 'index.html'), os.path.join(PREVIEW_SRC_FOLDER, 'index.html'))
    if app.architecture == AppArchitecture.FRONTEND_ONLY:
        copier.copy_and_insert(os.path.join(config.IE_APP_FOLDER_STRUCTURE[app.architecture.value]['static'], 'styles.css'), os.path.join(PREVIEW_SRC_FOLDER, 'styles.css'))
        copier.copy_and_insert(os.path.join(config.IE_APP_FOLDER_STRUCTURE[app.architecture.value]['static'], 'script.js'), os.path.join(PREVIEW_SRC_FOLDER, 'script.js'))
    else:
        os.makedirs(os.path.join(PREVIEW_SRC_FOLDER, 'static'))
        copier.copy_and_insert(os.path.join(config.IE_APP_FOLDER_STRUCTURE[app.architecture.value]['static'], 'styles.css'), os.path.join(PREVIEW_SRC_FOLDER, 'static', 'styles.css'))
        copier.copy_and_insert(os.path.join(config.IE_APP_FOLDER_STRUCTURE[app.architecture.value]['static'], 'script.js'), os.path.join(PREVIEW_SRC_FOLDER, 'static', 'script.js'))
    
    global server_running
    if not server_running:
        server.run(host='127.0.0.1', port=7654)
        server_running = True
    