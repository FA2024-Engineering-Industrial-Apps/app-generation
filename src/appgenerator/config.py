import os
from typing import Dict, Any

FRONTEND_FILE_SEPARATOR_STRING : str = '<<++>>'
DESTINATION_DIR : str = 'dist'
TEMPLATE_FILES_DIR : str = 'template_files'
MQTT_LIB_FILENAME : str = 'mqtt_lib.py'
IE_APP_FOLDER_STRUCTURE : Dict[str, Dict[str, Any]] = {
    'frontend_and_backend' : {
        'root' : 'program',
        'source' : os.path.join('program', 'src'),
        'html' : os.path.join('program', 'src', 'templates'),
        'static' : os.path.join('program', 'src', 'static')
        },
    'frontend_only' : {
        'root' : 'program',
        'html' : os.path.join('program', 'html'),
        },
    'backend_only' : {
        'root' : 'program',
        'source' : os.path.join('program', 'src'),
        }
    }
LOG_FOLDER : str = 'logs'
PROMPT_RERUN_LIMIT: int = 5