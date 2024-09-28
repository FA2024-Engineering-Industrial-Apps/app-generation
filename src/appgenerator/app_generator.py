from .llm_client import (
    SiemensLLMClient,
    WorkstationLLMClient,
    FAPSLLMClient,
    OpenAILLMClient,
    LLMClient
)
from abc import ABC, abstractmethod
from logging import Logger
from .generation_instance import GenerationInstance
from . import config
import os


# Base class for LLM clients
class AppGenerator(ABC):
    @abstractmethod
    def __init__(self, logger: Logger, llm_client: LLMClient):
        self.logger: Logger = logger
        self.llm_client: LLMClient = llm_client

    def get_requirements(self, prompt):
        pass

    def generate_app(self, app_name: str, use_case_description: str) -> GenerationInstance:
        pass
