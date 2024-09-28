from typing import Dict, List
from . import config
import os
from enum import Enum

class AppArchitecture(Enum):
    FRONTEND_ONLY = 'frontend_only'
    BACKEND_ONLY = 'backend_only'
    FRONTEND_AND_BACKEND = 'frontend_and_backend'

class GenerationInstance():
    """
    Data copy of the file structure of the generated app
    """
    def __init__(self, app_name: str = "My IE App") -> None:
        self.name = app_name.strip()
        self.folder = self.name.replace(" ", "_").lower()
        self.root_path = os.path.join(config.DESTINATION_DIR, self.folder)
        self.artifacts: Dict[str, str] = dict()
        self.code_artifacts: Dict[str, str] = dict()
        self.file_list: List[str] = list()
        self.architecture: AppArchitecture = None
        
    def get_code_artifacts(self) -> Dict[str, str]:
        """
        Returns a list of all code artifacts of this generation instance.

        @return: Filename, code pairs of all code artifacts associated with
            this generation instance.
        """
        
        return self.app.code_artifacts.copy()

    def get_generated_files(self) -> List[str]:
        """
        Returns a list of files associated with this generation instance.

        @return: Filenames of files associated with this generation instance.
        """
        
        return self.app.file_list.copy()