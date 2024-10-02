from typing import Dict, List
from . import config
import os
from enum import Enum

class AppArchitecture(Enum):
    """
    Enum to define the architecture type of the generated app.
    
    Possible values:
    - FRONTEND_ONLY: Only frontend components.
    - BACKEND_ONLY: Only backend components.
    - FRONTEND_AND_BACKEND: Both frontend and backend components.
    """
    FRONTEND_ONLY = 'frontend_only'
    BACKEND_ONLY = 'backend_only'
    FRONTEND_AND_BACKEND = 'frontend_and_backend'

class GenerationInstance():
    """
    Represents the generated application's file structure and artifacts.

    This class holds the app's name, folder structure, and all artifacts 
    (both code and non-code) generated during the app's creation.
    
    @ivar name: The name of the generated application.
    @ivar folder: The folder name derived from the app name.
    @ivar root_path: The root path where the app is generated.
    @ivar artifacts: A dictionary holding artifacts like use case descriptions or architecture details.
    @ivar code_artifacts: A dictionary holding filenames and code as key-value pairs.
    @ivar file_list: A list of all files generated for the application.
    @ivar architecture: The app's architecture type (frontend-only, backend-only, or both).
    """
    
    def __init__(self, app_name: str = "My IE App") -> None:
        """
        Initializes a GenerationInstance with the given app name.
        
        @param app_name: The name of the application to generate.
        """
        self.name = app_name.strip()
        self.folder = self.name.replace(" ", "_").lower()
        self.root_path = os.path.join(config.DESTINATION_DIR, self.folder)
        self.artifacts: Dict[str, str] = dict()
        self.code_artifacts: Dict[str, str] = dict()
        self.file_list: List[str] = list()
        self.architecture: AppArchitecture = None
        self.placeholder_needed = False
        
        
    def get_code_artifacts(self) -> Dict[str, str]:
        """
        Returns a copy of the code artifacts of this generation instance.

        @return: A dictionary of filename-to-code mappings for all code artifacts
            associated with this generation instance.
        """
        
        return self.app.code_artifacts.copy()
    

    def get_generated_files(self) -> List[str]:
        """
        Returns a list of all the generated files for this generation instance.

        @return: A list of filenames associated with this generation instance.
        """
        
        return self.app.file_list.copy()