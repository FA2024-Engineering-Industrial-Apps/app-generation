from .app_generator import AppGenerator
from .promptfetcher import PromptFetcher
from typing import Dict

class IEAppGenerator(AppGenerator):
    def __init__(self, llm_model="LLaMA-3-Latest", api_key=""):
        super().__init__(llm_model, api_key)
        self.prompt_fetcher : PromptFetcher = PromptFetcher()
        self.artifacts : Dict[str,str] = dict()
    
    def _define_task_distribution(self) -> None:
        architecture_description = self.llm_client.get_response(self.prompt_fetcher.fetch('generate_task_distribution', self.artifacts['use_case']))
        self.artifacts.update({'architecture_description' : architecture_description})

    def _define_restful_api(self) -> None:
        restful_api_definition = self.llm_client.get_response(self.prompt_fetcher.fetch('define_restful_api', self.artifacts['architecture_description']))
        self.artifacts.update({'restful_api_definition'})

    def _generate_web_interface(self) -> None:
        web_interface_files = self.llm_client.get_response(self.prompt_fetcher.fetch('generate_web_interface_fb', self.artifacts['frontend_architecture_description'], self.artifacts['restful_api_definition'])).split(FRONTEND_FILE_SEPARATOR_STRING)
        if len(web_interface_files) == 3:
            index_html_text = web_interface_files[0]
            styles_css_text = web_interface_files[1]
            script_js_text = web_interface_files[2]
            
            
        else:
            raise Exception('The LLM failed to generate the frontend web interface files.')

    def _split_architecture_description(self) -> None:
        # Todo implement splitting of architecture description
        self.artifacts.update({'frontend_architecture_description' : None})
        self.artifacts.update({'backend_architecture_description' : None})

    def _define_backend_app_interface(self) -> None:
        backend_app_method_signatures = self.llm_client.get_response(self.prompt_fetcher.fetch('generate_backend_signatures', self.artifacts['restful_api_definition']))
        self.artifacts.update({'backend_app_method_signatures' : backend_app_method_signatures})

    def _generate_backend_http_server(self) -> None:
        backend_http_server_code = self.llm_client.get_response(self.prompt_fetcher.fetch('generate_backend_http', self.artifacts['restful_api_definition'], self.artifacts['backend_app_method_signatures']))
        self.artifacts.update({'backend_http_server_code' : backend_http_server_code})
        # Todo save http server code to file

    def _generate_backend_app(self) -> None:
        backend_app_code = self.llm_client.get_response(self.prompt_fetcher.fetch('generate_backend', self.artifacts['backend_app_method_signatures'], self.artifacts['backend_architecture_description']))
        self.artifacts.update({'backend_app_code' : backend_app_code})
        # Todo save backend app code to file

    def _package_backend_application(self) -> None:
        # Todo implement backend app packaging
        pass

    def _generate_dockerfile(self) -> None:
        # Todo implement dockerfile generation
        pass

    def _package_dockerfile(self) -> None:
        # Todo implement dockerfile packaging
        pass

    def _configure_docker_compose_file(self) -> None:
        # Todo implement docker compose generation
        pass
    
    def _generate_frontend_and_backend(self) -> None:
        self._define_task_distribution()
        self._define_restful_api()
        self._split_architecture_description()
        self._define_backend_app_interface()
        self._generate_backend_http_server()
        self._generate_web_interface()
        self._generate_backend_app()
        self._package_backend_application()
        
        self._generate_web_interface()
    
    def _generate_only_frontend(self) -> None:
        pass
    
    def _generate_only_backend(self) -> None:
        pass

    def run_pipeline(self, use_case_description):
        self.artifacts.update({'use_case' : use_case_description})
        generation_tasks = {
            'a' : self._generate_only_frontend,
            'b' : self._generate_only_backend,
            'c' : self._generate_frontend_and_backend
        }
        
        try:
            generation_tasks[self.llm_client.get_response(self.prompt_fetcher.fetch('determine_necessary_components', use_case_description)).lower().strip()]()
        except KeyError as e:
            print(f'The LLM has returned an invalid result.')
            