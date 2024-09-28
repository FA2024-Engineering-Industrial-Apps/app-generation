from abc import ABC, abstractmethod
from .llm_client import (
    SiemensLLMClient,
    WorkstationLLMClient,
    FAPSLLMClient,
    OpenAILLMClient,
)
from logging import Logger
from . import config
import os


# Base class for LLM clients
class AppGenerator(ABC):
    @abstractmethod
    def __init__(
        self,
        logger: Logger,
        app_name: str = "My_IE_App",
        llm_model: str = "LLaMA-3-Latest",
    ):
        self.logger = logger
        self.prompt = ""
        self.app_name = app_name.strip()
        self.app_folder = self.app_name.replace(" ", "_").lower()
        self.app_root_path = os.path.join(config.DESTINATION_DIR, self.app_folder)
        self.select_llm_client(llm_model)

    def select_llm_client(self, llm_model):
        """Select the appropriate LLM client based on user choice."""
        if llm_model == "Siemens LLM":
            self.llm_client = SiemensLLMClient(self.logger)
        elif llm_model == "FAPS LLM":
            self.llm_client = FAPSLLMClient(self.logger)
        elif llm_model == "ChatGPT":
            self.llm_client = OpenAILLMClient(self.logger)
        else:
            self.llm_client = WorkstationLLMClient(self.logger)

    def get_requirements(self, prompt):
        pass

    def run_pipeline(self, prompt):
        pass

    def preview(self, code):
        pass

    def deploy(self, code):
        pass

    def stop(self):
        pass
