import re
import subprocess
import os
import json
import tarfile
import requests

with open('src/publisher/id_mapping.json', 'r') as json_file:
    id_mapping = json.load(json_file)

class Publisher:
    def __init__(self, ie_user, ie_pass , webaddress, ie_config_name = "my_config") -> None:
        self.ie_user = ie_user
        self.ie_pass = ie_pass
        self.ie_config_name = ie_config_name
        self.webaddress = webaddress
        self.env_variable = self.get_env_variables()
        
        
    def get_env_variables(self):
        return {
            "IE_USER" : self.ie_user,
            "IE_PASS" : self.ie_pass,
            "IE_CONFIG_NAME" : self.ie_config_name,
            "WEBADDRESS" : self.webaddress
        }
        
        
    @staticmethod
    def write_env_file(env_dict, file_path='../publish/.env'):
        with open(file_path, 'w') as f:
            for key, value in env_dict.items():
                f.write(f"{key}={value}\n")
        
        os.chmod(file_path, 0o755)
                

    def validate_version(self, version):
        """
        Validates a version number string based on semantic versioning rules.
        Valid format: X.Y.Z or X.Y.Z-<pre-release> or X.Y.Z+<build>
        
        Parameters:
        - version: str, version number to validate
        
        Returns:
        - bool: True if the version is valid, False otherwise
        """
        # Regular expression for semantic versioning
        pattern = r"^\d+\.\d+\.\d+$"
        
        # Match the version against the pattern
        if re.match(pattern, version):
            return True
        else:
            return False
        

    def publish(self, 
                app_name, 
                app_description, 
                version_number, 
                project_id, 
                category, 
                docker_compose_path, 
                app_path,
                redirect_url = 5000, 
                app_repo_name = None) -> None:
        if app_repo_name is None:
            app_repo_name = app_name.lower().replace(" ", "-")
        if not self.validate_version(version_number):
            raise ValueError("The version number should have the format x.x.x") 
        
        app_specific_variables = {
            "APP_NAME": app_name,
            "APP_REPO_NAME": app_repo_name,
            "APP_DESCRIPTION": app_description,
            "VERSION_NUMBER": version_number,
            "REDIRECT_URL": redirect_url,
            "PROJECT_ID": project_id,
            "CATEGORY_ID": id_mapping["app_category_id"][category],
            "DOCKER_COMPOSE_PATH" : docker_compose_path
        }
        ## Build the image 
        self.build_image(app_path, "http://127.0.0.1:2376", app_name, version_number)
        
        env_file_path: str = 'publish/.env'
        app_specific_variables.update(self.env_variable)
        self.write_env_file(app_specific_variables, file_path=env_file_path)
        
        try:
            result = subprocess.run(['bash', 'publish/publish-app-container.sh'])
            return True
        except:
            return False
            pass
        
    @staticmethod
    def build_image(app_path, docker_host_url, app_name, app_version):
        # Create a tarball of the application files
        with tarfile.open('app.tar', 'w') as tar:
            tar.add(os.path.join(app_path, 'Dockerfile'))
            tar.add(os.path.join(app_path, 'requirements.txt'))
            tar.add(os.path.join(app_path, "src","static"))
            tar.add(os.path.join(app_path, "src","templates"))
            tar.add(os.path.join(app_path, "src","backend.py"))
            tar.add(os.path.join(app_path, "src","mqtt_lib.py"))
            tar.add(os.path.join(app_path, "src","server.py"))


        # Read the tarball
        with open('app.tar', 'rb') as f:
            tar_data = f.read()
        
        # Set the Docker host and image name
        image_name = "my_ie_app"

        # Send POST request to build the image
        response = requests.post(f'{docker_host_url}/build?t={image_name}', data=tar_data,
                                headers={'Content-Type': 'application/x-tar'})
        print(response)

