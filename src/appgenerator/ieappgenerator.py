from .app_generator import AppGenerator
from .util.promptfetcher import PromptFetcher
from .util.filecopier import FileCopier
from .util.extractor import extract_imports_from_directory, extract_code
from typing import Dict, Tuple, List
import os
import traceback
from . import config
import shutil
import logging
from .llm_client import BadLLMResponseError, LLMClient
from .generation_instance import GenerationInstance, AppArchitecture

class IEAppGenerator(AppGenerator):
    def __init__(self, logger: logging.Logger, llm_client: LLMClient):
        super().__init__(logger, llm_client)
        self.prompt_fetcher: PromptFetcher = PromptFetcher()
        self.file_copier: FileCopier = FileCopier(config.TEMPLATE_FILES_DIR)
        self.app: GenerationInstance = None
        
    @staticmethod
    def _python_code_validator(response: str) -> str:
        code: str
        try:
            code = extract_code(response, "python")
        except ValueError:
            raise BadLLMResponseError("LLM returned code in non parsable form.")
        return code
    
    @staticmethod
    def _plaintext_validator(response: str) -> str:
        code: str
        try:
            code = extract_code(response, 'markdown')
        except ValueError:
            raise BadLLMResponseError('LLM returned code in non parsable form.')
        return code
    
    def _save_app_artifacts(self) -> None:
        if self.app:
            self._ensure_empty_folder(config.LOG_FOLDER)
            for artifact, text in self.app.artifacts.items():
                with open(
                    os.path.join(config.LOG_FOLDER, artifact + ".artifact"),
                    "w",
                    encoding="utf8"
                ) as file:
                    file.write(text)

    def _define_task_distribution(self) -> None:
        architecture_description = self.llm_client.get_response(
            self.prompt_fetcher.fetch(
                "define_task_distribution", self.app.artifacts["use_case"]
            )
        )
        self.app.artifacts.update({"architecture_description": architecture_description})

    def _define_restful_api(self) -> None:
        restful_api_definition = self.llm_client.get_response(
            self.prompt_fetcher.fetch(
                "define_restful_api", self.app.artifacts["architecture_description"]
            )
        )
        self.app.artifacts.update({"restful_api_definition": restful_api_definition})

    def _generate_web_interface(self, architecture: AppArchitecture) -> None:
        def validator(response: str) -> Tuple[str, str, str]:
            self.app.artifacts.update({"web_interface_files": response})
            web_interface_files = response.split(config.FRONTEND_FILE_SEPARATOR_STRING)
            html: str
            css: str
            js: str
            if len(web_interface_files) == 3:
                try:
                    html = extract_code(web_interface_files[0], "html")
                    css = extract_code(web_interface_files[1], "css")
                    js = extract_code(web_interface_files[2], "javascript")
                except ValueError:
                    self.logger.warning(
                        "LLM failed to return frontend in parsable form"
                    )
                    raise BadLLMResponseError(
                        "LLM failed to return frontend code in parsable form."
                    )
            else:
                self.logger.warning("LLM failed to return frontend in parsable form")
                raise BadLLMResponseError(
                    "LLM failed to return frontend code in parsable form."
                )
            return (html, css, js)

        if architecture == AppArchitecture.FRONTEND_AND_BACKEND:
            prompt = self.prompt_fetcher.fetch(
                "generate_web_interface_fb",
                self.app.artifacts["frontend_architecture_description"],
                self.app.artifacts["restful_api_definition"],
            )
        else:
            prompt = self.prompt_fetcher.fetch(
                "generate_web_interface_f",
                self.app.artifacts["use_case"],
            )
        (index_html_text, styles_css_text, script_js_text) = (
            self.llm_client.get_validated_response(prompt, validator, config.PROMPT_RERUN_LIMIT)
        )

        self.app.artifacts.update({"index_html": index_html_text})
        self.app.artifacts.update({"styles_css": styles_css_text})
        self.app.artifacts.update({"script_js": script_js_text})

        self.app.code_artifacts.update({"index.html": index_html_text})
        self.app.code_artifacts.update({"styles.css": styles_css_text})
        self.app.code_artifacts.update({"script.js": script_js_text})
        for file in ["index.html", "styles.css", "script.js"]:
            self.app.file_list.append(file)

        with open(
            os.path.join(
                self.app.root_path,
                config.IE_APP_FOLDER_STRUCTURE[architecture.value]["html"],
                "index.html",
            ),
            "w",
            encoding="utf8"
        ) as file:
            file.write(index_html_text)
        with open(
            os.path.join(
                self.app.root_path,
                config.IE_APP_FOLDER_STRUCTURE[architecture.value]["static"],
                "styles.css",
            ),
            "w",
            encoding="utf8"
        ) as file:
            file.write(styles_css_text)
        with open(
            os.path.join(
                self.app.root_path,
                config.IE_APP_FOLDER_STRUCTURE[architecture.value]["static"],
                "script.js",
            ),
            "w",
            encoding="utf8"
        ) as file:
            file.write(script_js_text)

    def _split_architecture_description(self) -> None:
        separated_architecture = self.app.artifacts["architecture_description"].split(
            config.FRONTEND_FILE_SEPARATOR_STRING
        )
        self.app.artifacts.update(
            {"frontend_architecture_description": separated_architecture[0]}
        )
        self.app.artifacts.update(
            {"backend_architecture_description": separated_architecture[1]}
        )

    def _define_backend_app_interface(self) -> None:
        backend_app_method_signatures = self.llm_client.get_response(
            self.prompt_fetcher.fetch(
                "generate_backend_signatures", self.app.artifacts["restful_api_definition"]
            )
        )
        self.app.artifacts.update(
            {"backend_app_method_signatures": backend_app_method_signatures}
        )

    def _generate_backend_http_server(self) -> None:
        backend_http_server_code = self.llm_client.get_validated_response(
            self.prompt_fetcher.fetch(
                "generate_backend_http",
                self.app.artifacts["restful_api_definition"],
                self.app.artifacts["backend_app_method_signatures"],
            ),
            self._python_code_validator,
            config.PROMPT_RERUN_LIMIT
        )

        self.app.artifacts.update({"backend_http_server_code": backend_http_server_code})
        self.app.code_artifacts.update({"server.py": backend_http_server_code})
        self.app.file_list.append("server.py")

        with open(
            os.path.join(
                self.app.root_path,
                config.IE_APP_FOLDER_STRUCTURE["frontend_and_backend"]["source"],
                "server.py",
            ),
            "w",
            encoding="utf8"
        ) as file:
            file.write(backend_http_server_code)

    def _generate_backend_app(self, architecture: AppArchitecture) -> None:
        if architecture == AppArchitecture.FRONTEND_AND_BACKEND:
            prompt = self.prompt_fetcher.fetch(
                "generate_backend",
                self.app.artifacts["backend_app_method_signatures"],
                self.app.artifacts["backend_architecture_description"],
            )
        else:
            prompt = self.prompt_fetcher.fetch(
                "generate_backend_b",
                self.app.artifacts["use_case"],
            )
        backend_app_code = self.llm_client.get_validated_response(
            prompt, self._python_code_validator, config.PROMPT_RERUN_LIMIT
        )

        self.app.artifacts.update({"backend_app_code": backend_app_code})
        self.app.code_artifacts.update({"backend.py": backend_app_code})
        self.app.file_list.append("backend.py")

        with open(
            os.path.join(
                self.app.root_path,
                config.IE_APP_FOLDER_STRUCTURE[architecture.value]["source"],
                "backend.py",
            ),
            "w",
            encoding="utf8"
        ) as file:
            file.write(backend_app_code)

    def _package_backend_application(self, architecture: AppArchitecture) -> None:
        self.file_copier.copy_and_insert(
            config.MQTT_LIB_FILENAME,
            os.path.join(
                self.app.root_path,
                config.IE_APP_FOLDER_STRUCTURE[architecture.value]["source"],
                "mqtt_lib.py",
            ),
        )

    def _package_dockerfile(self, architecture: AppArchitecture) -> None:
        dst_file = os.path.join(
            self.app.root_path,
            config.IE_APP_FOLDER_STRUCTURE[architecture.value]["root"],
            "Dockerfile",
        )
        self.file_copier.copy_and_insert("Dockerfile", dst_file, {})
        self.app.file_list.append("Dockerfile")

    def _generate_requirements(self, architecture: AppArchitecture) -> None:
        backend_dir = os.path.join(
            self.app.root_path,
            config.IE_APP_FOLDER_STRUCTURE[architecture.value]["source"],
        )
        imports = extract_imports_from_directory(backend_dir)
        import_list = ""
        for module in sorted(imports):
            import_list += f"{module}\n"
        self.app.artifacts.update({"import_list": import_list})
        package_list = self.llm_client.get_validated_response(
            self.prompt_fetcher.fetch(
                "generate_requirements", self.app.artifacts["import_list"]
            ),
            self._plaintext_validator,
            config.PROMPT_RERUN_LIMIT
        )
        dst_file = os.path.join(
            self.app.root_path,
            config.IE_APP_FOLDER_STRUCTURE[architecture.value]["root"],
            "requirements.txt",
        )
        self.file_copier.copy_and_insert(
            "requirements.txt", dst_file, {"package_list": package_list}
        )
        self.app.file_list.append("requirements.txt")

    def _configure_docker_compose_file(self) -> None:
        dst_file = os.path.join(self.app.root_path, "docker_compose.yml")
        self.file_copier.copy_and_insert(
            "docker-compose.yml",
            dst_file,
            {"image_name": self.app.name.replace(" ", "_").lower()},
        )
        self.app.file_list.append("docker-compose.yml")

    @staticmethod
    def _ensure_empty_folder(folder_path):
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        os.makedirs(folder_path, exist_ok=True)

    def _create_app_folder_structure(self, architecture: AppArchitecture) -> None:
        self._ensure_empty_folder(self.app.root_path)
        for folder in config.IE_APP_FOLDER_STRUCTURE[architecture.value].values():
            os.makedirs(os.path.join(self.app.root_path, folder), exist_ok=True)

    def _generate_frontend_and_backend(self) -> None:
        self.app.architecture = AppArchitecture.FRONTEND_AND_BACKEND
        self._create_app_folder_structure(AppArchitecture.FRONTEND_AND_BACKEND)
        self._define_task_distribution()
        self._define_restful_api()
        self._split_architecture_description()
        self._define_backend_app_interface()
        self._generate_backend_http_server()
        self._generate_web_interface(AppArchitecture.FRONTEND_AND_BACKEND)
        self._generate_backend_app(AppArchitecture.FRONTEND_AND_BACKEND)
        self._package_backend_application(AppArchitecture.FRONTEND_AND_BACKEND)

        self._package_dockerfile(AppArchitecture.FRONTEND_AND_BACKEND)
        self._generate_requirements(AppArchitecture.FRONTEND_AND_BACKEND)
        self._configure_docker_compose_file()

    def _generate_only_frontend(self) -> None:
        self.app.architecture = AppArchitecture.FRONTEND_ONLY
        self._create_app_folder_structure(AppArchitecture.FRONTEND_ONLY)
        self._generate_web_interface(AppArchitecture.FRONTEND_ONLY)
        self._package_dockerfile(AppArchitecture.FRONTEND_ONLY)
        self._configure_docker_compose_file()

    def _generate_only_backend(self) -> None:
        self.app.architecture = AppArchitecture.BACKEND_ONLY
        self._create_app_folder_structure(AppArchitecture.BACKEND_ONLY)
        self._generate_backend_app(AppArchitecture.BACKEND_ONLY)
        self._package_backend_application(AppArchitecture.BACKEND_ONLY)
        self._package_dockerfile(AppArchitecture.BACKEND_ONLY)
        self._generate_requirements(AppArchitecture.BACKEND_ONLY)
        self._configure_docker_compose_file()

    def generate_app(self, app_name: str, use_case_description: str) -> GenerationInstance:
        self.logger.info("Running IEAppGenerator pipeline...")
        self.app: GenerationInstance = GenerationInstance(app_name)
        self.app.artifacts.update({"use_case": use_case_description})
        generation_tasks = {
            "a": self._generate_only_frontend,
            "b": self._generate_only_backend,
            "c": self._generate_frontend_and_backend,
        }
        
        def response_validator(response: str) -> str:
            if response not in ["a", "b", "c"]:
                raise BadLLMResponseError('LLM response not in ["a", "b", "c"].')
            return response

        try:
            generation_tasks[
                self.llm_client.get_validated_response(
                    self.prompt_fetcher.fetch(
                        "determine_necessary_components", use_case_description
                    ),
                    response_validator,
                    config.PROMPT_RERUN_LIMIT
                )
                .lower()
                .strip()
            ]()
        except Exception:
            print(traceback.format_exc())
            raise
        finally:
            self._save_app_artifacts()
                    
        return self.app
