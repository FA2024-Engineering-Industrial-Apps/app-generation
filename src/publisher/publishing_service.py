import re

class Publisher:
    def __init__(self, IE_USER, IE_PASS, IE_CONFIG_NAME , WEBADDRESS) -> None:
        self.ie_user = IE_USER
        self.ie_pass = IE_PASS
        self.ie_config_name = IE_CONFIG_NAME
        self.webaddress = WEBADDRESS
        self.env_variable = self.get_env_variables()
    def get_env_variables(self):
        return {
            "IE_USER" : self.ie_user,
            "IE_PASS" : self.ie_pass,
            "IE_CONFIG_NAME" : self.ie_config_name,
            "WEBADDRESS" : self.webaddress
        }
    def write_env_file(env_dict, file_path='../publish/.env'):
        with open(file_path, 'w') as f:
            for key, value in env_dict.items():
                f.write(f"{key}={value}\n")

    def validate_version(version):
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

    def publish(self, app_name, app_description, icon_path, version_number, redirect_url, project_id, category, app_repo_name = None):
        if (app_repo_name is None):
            app_repo_name = app_name.lower().replace(" ", "-")
        if (not self.validate_version_number(version_number)):
            raise ValueError("The version number should have the format x.x.x") 
        app_specific_variables = {
            "APP_NAME": app_name,
            "APP_REPO_NAME" : app_repo_name,
            "VERSION_NUMBER" : version_number
            
        }