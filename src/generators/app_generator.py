from abc import ABC, abstractmethod
from .llm_client import SiemensLLMClient, WorkstationLLMClient

# Base class for LLM clients
class AppGenerator(ABC):
    @abstractmethod
    def __init__(self, app_name : str = 'My IE App', llm_model : str = "LLaMA-3-Latest", api_key : str = ""):
        self.prompt = ""
        self.app_name = app_name.strip()
        self.app_folder = self.app_name.replace(' ', '_').lower()
        self.select_llm_client(llm_model, api_key)

    def select_llm_client(self, llm_model, api_key=""):
        """Select the appropriate LLM client based on user choice."""
        if llm_model == "Siemens LLM":
            if api_key:
                api_key = api_key
                self.llm_client = SiemensLLMClient(api_key)
            else:
                raise Exception("No API Key.")
        else:
            self.llm_client = WorkstationLLMClient(llm_model)

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

