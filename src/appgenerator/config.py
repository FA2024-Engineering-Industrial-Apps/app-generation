import os
from typing import Dict, Any

FRONTEND_FILE_SEPARATOR_STRING : str = '<<++>>'
DESTINATION_DIR : str = os.path.join('artifacts', 'dist')
TEMPLATE_FILES_DIR : str = os.path.join('resources', 'templates')
PROMPTS_DIR: str = os.path.join('resources', 'prompts')
PROMPT_PLACEHOLDER_STRING: str = '[%text%]'
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
        'static' : os.path.join('program', 'html')
        },
    'backend_only' : {
        'root' : 'program',
        'source' : os.path.join('program', 'src'),
        }
    }
FOLDER_STRUCTURE_FOR_DOC : Dict[str, Dict[str, Any]] = {
    'frontend_and_backend' : {
        'root' : 'program',
		'Dockerfile' : 'program',
		'README.md' : 'program',
		'requirements.txt' : 'program',
		'main.py' : os.path.join('program', 'src'),
		'mqtt_lib.py' : os.path.join('program', 'src'),
        'index.html' : os.path.join('program', 'src', 'templates'),
        'script.js' : os.path.join('program', 'src', 'static'),
		'styles.css' : os.path.join('program', 'src', 'static'),
        },
    'frontend_only' : {
        'root' : 'program',		
		'Dockerfile' : 'program',
        'nginx.conf' : 'program',
		'README.md' : 'program',
        'index.html' : os.path.join('program', 'html'),
        'script.js' : os.path.join('program', 'html'),
		'styles.css' : os.path.join('program', 'html'),
        },
    'backend_only' : {
        'root' : 'program',
		'Dockerfile' : 'program',
		'README.md' : 'program',
		'requirements.txt' : 'program',
		'main.py' : os.path.join('program', 'src'),
		'mqtt_lib.py' : os.path.join('program', 'src'),   
        }
    }

DOC_OUTPUT_PATH : str = os.path.join('program')
LOG_FOLDER : str = os.path.join('artifacts', 'logs')
PROMPT_RERUN_LIMIT: int = 5

PYTHON_DOCKERFILE_TEMPLATE_NAME: str = 'Dockerfile_python.template'
NGINX_DOCKERFILE_TEMPLATE_NAME: str = 'Dockerfile_nginx.template'
DOCKER_COMPOSE_TEMPLATE_NAME: str = 'docker_compose.yml.template'
NGINX_CONFIG_TEMPLATE_NAME: str = 'nginx_config.template'