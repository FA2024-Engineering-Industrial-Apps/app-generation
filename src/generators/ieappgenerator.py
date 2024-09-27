from .app_generator import AppGenerator
from .promptfetcher import PromptFetcher
from .filecopier import FileCopier
from .extractor import extract_imports_from_directory, extract_code
from typing import Dict
import os
import traceback
from . import config
import shutil
import logging

class IEAppGenerator(AppGenerator):
    def __init__(self, logger : logging.Logger, app_name : str = 'My IE App', llm_model : str = "LLaMA-3-Latest", api_key : str = ""):
        super().__init__(logger, app_name, llm_model, api_key)
        self.prompt_fetcher : PromptFetcher = PromptFetcher()
        self.file_copier : FileCopier = FileCopier(config.TEMPLATE_FILES_DIR)
        self.artifacts : Dict[str,str] = dict()
    
    def _define_task_distribution(self) -> None:
        architecture_description = self.llm_client.get_response(self.prompt_fetcher.fetch('define_task_distribution', self.artifacts['use_case']))
        self.artifacts.update({'architecture_description' : architecture_description})

    def _define_restful_api(self) -> None:
        restful_api_definition = self.llm_client.get_response(self.prompt_fetcher.fetch('define_restful_api', self.artifacts['architecture_description']))
        self.artifacts.update({'restful_api_definition' : restful_api_definition})

    def _generate_web_interface(self) -> None:
        web_interface_files = self.llm_client.get_response(self.prompt_fetcher.fetch('generate_web_interface_fb', self.artifacts['frontend_architecture_description'], self.artifacts['restful_api_definition'])).split(config.FRONTEND_FILE_SEPARATOR_STRING)
        if len(web_interface_files) >= 3:
            index_html_text = extract_code(web_interface_files[0], 'html')
            styles_css_text = extract_code(web_interface_files[1], 'css')
            script_js_text = extract_code(web_interface_files[2], 'javascript')
            
            self.artifacts.update({'index_html' : index_html_text})
            self.artifacts.update({'styles_css' : styles_css_text})
            self.artifacts.update({'script_js' : script_js_text})
            
            with open(os.path.join(self.app_root_path, config.IE_APP_FOLDER_STRUCTURE['frontend_and_backend']['html'], 'index.html'), 'w') as file:
                file.write(index_html_text)
            with open(os.path.join(self.app_root_path, config.IE_APP_FOLDER_STRUCTURE['frontend_and_backend']['static'], 'styles.css'), 'w') as file:
                file.write(styles_css_text)
            with open(os.path.join(self.app_root_path, config.IE_APP_FOLDER_STRUCTURE['frontend_and_backend']['static'], 'script.js'), 'w') as file:
                file.write(script_js_text)
        else:
            raise Exception('The LLM failed to generate the frontend web interface files.')

    def _split_architecture_description(self) -> None:
        separated_architecture = self.artifacts['architecture_description'].split(config.FRONTEND_FILE_SEPARATOR_STRING)
        self.artifacts.update({'frontend_architecture_description' : separated_architecture[0]})
        self.artifacts.update({'backend_architecture_description' : separated_architecture[1]})

    def _define_backend_app_interface(self) -> None:
        backend_app_method_signatures = self.llm_client.get_response(self.prompt_fetcher.fetch('generate_backend_signatures', self.artifacts['restful_api_definition']))
        self.artifacts.update({'backend_app_method_signatures' : backend_app_method_signatures})

    def _generate_backend_http_server(self) -> None:
        backend_http_server_code = extract_code(self.llm_client.get_response(self.prompt_fetcher.fetch('generate_backend_http', self.artifacts['restful_api_definition'], self.artifacts['backend_app_method_signatures'])), 'python')
        self.artifacts.update({'backend_http_server_code' : backend_http_server_code})
        with open(os.path.join(self.app_root_path, config.IE_APP_FOLDER_STRUCTURE['frontend_and_backend']['source'], 'server.py'), 'w') as file:
            file.write(backend_http_server_code)

    def _generate_backend_app(self) -> None:
        backend_app_code = extract_code(self.llm_client.get_response(self.prompt_fetcher.fetch('generate_backend', self.artifacts['backend_app_method_signatures'], self.artifacts['backend_architecture_description'])), 'python')
        self.artifacts.update({'backend_app_code' : backend_app_code})
        with open(os.path.join(self.app_root_path, config.IE_APP_FOLDER_STRUCTURE['frontend_and_backend']['source'], 'backend.py'), 'w') as file:
            file.write(backend_app_code)

    def _package_backend_application(self) -> None:
        self.file_copier.copy_and_insert(config.MQTT_LIB_FILENAME, os.path.join(self.app_root_path, config.IE_APP_FOLDER_STRUCTURE['frontend_and_backend']['source']))

    def _package_dockerfile(self) -> None:
        dst_file = os.path.join(self.app_root_path, config.IE_APP_FOLDER_STRUCTURE['frontend_and_backend']['root'], "Dockerfile")
        self.file_copier.copy_and_insert('Dockerfile', dst_file, {})

    def _generate_requirements(self) -> None:
        backend_dir = os.path.join(self.app_root_path, config.IE_APP_FOLDER_STRUCTURE['frontend_and_backend']['source'])
        imports = extract_imports_from_directory(backend_dir)
        import_list = ""
        for module in sorted(imports):
            import_list += f"{module}\n"
        self.artifacts.update({'import_list' : import_list})
        package_list = self.llm_client.get_response(self.prompt_fetcher.fetch('generate_requirements', self.artifacts['import_list']))
        dst_file = os.path.join(self.app_root_path, config.IE_APP_FOLDER_STRUCTURE['frontend_and_backend']['root'], "Dockerfile")
        self.file_copier.copy_and_insert('requirements.txt', dst_file, {'package_list' : package_list})

    def _configure_docker_compose_file(self) -> None:
        dst_file = os.path.join(self.app_root_path, "docker_compose.yml")
        self.file_copier.copy_and_insert('docker-compose.yml', dst_file, {'image_name' : self.app_name})
    
    def _ensure_empty_folder(self, folder_path):
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        
        os.makedirs(folder_path, exist_ok=True)
        
    def _create_app_folder_structure(self, config_name : str) -> None:
        self._ensure_empty_folder(self.app_root_path)
        for folder in config.IE_APP_FOLDER_STRUCTURE[config_name].values():
            os.makedirs(os.path.join(self.app_root_path, folder), exist_ok=True)
    
    def _generate_frontend_and_backend(self) -> None:
        self._create_app_folder_structure('frontend_and_backend')
        self._define_task_distribution()
        self._define_restful_api()
        self._split_architecture_description()
        self._define_backend_app_interface()
        self._generate_backend_http_server()
        self._generate_web_interface()
        self._generate_backend_app()
        
        self._package_dockerfile()
        self._generate_requirements()
        self._configure_docker_compose_file()
    
    def _generate_only_frontend(self) -> None:
        self._create_app_folder_structure('frontend_only')
        pass
    
    def _generate_only_backend(self) -> None:
        self._create_app_folder_structure('backend_only')
        pass

    def run_pipeline(self, use_case_description):
        self.logger.debug('Running IEAppGenerator pipeline...')
        self.artifacts.update({'use_case' : use_case_description})
        generation_tasks = {
            'a' : self._generate_only_frontend,
            'b' : self._generate_only_backend,
            'c' : self._generate_frontend_and_backend
        }
        
        try:
            generation_tasks[self.llm_client.get_response(self.prompt_fetcher.fetch('determine_necessary_components', use_case_description)).lower().strip()]()
        except KeyError as e:
            print(traceback.format_exc())
            self.logger.error(f'The LLM has returned an invalid result.')
        except:
            print(traceback.format_exc())
        finally:
            self._ensure_empty_folder(config.LOG_FOLDER)
            for artifact, text in self.artifacts:
                with os.open(os.path.join(config.LOG_FOLDER, artifact + '.artifact', 'w')) as file:
                    file.write(text)