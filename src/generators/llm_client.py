import requests
from abc import ABC, abstractmethod
import logging

# Base class for LLM clients
class LLMClient(ABC):
    @abstractmethod
    def get_response(self, prompt : str) -> str:
        pass


# Siemens LLM client
class SiemensLLMClient(LLMClient):
    def __init__(self, logger : logging.Logger, api_key):
        self.logger = logger
        self.api_key = api_key
        self.model = "mistral-7b-instruct"
        self.url = "https://api.siemens.com/llm/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def get_response(self, prompt : str) -> str:

        payload = {
            "model": self.model,
            "max_tokens": 18000,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.6,
            "stream": False,
        }
        self.logger.debug(f'Prompting LLM with "{prompt}"')
        response = requests.post(self.url, json=payload, headers=self.headers)

        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"].strip()
            self.logger.debug(f'Received LLM response: "{result}"')
            return result
        else:
            raise Exception(f"Failed with status code: {response.status_code}")

# Workstation LLM client
class WorkstationLLMClient(LLMClient):
    def __init__(self, logger : logging.Logger, model_name):
        self.logger = logger
        self.url = "http://workstation.ferienakademie.de:11434/api/generate"
        self.available_models = {
            "Gemma-2": "gemma2:27b",
            "LLaMA-3-70B": "llama3.1:70b",
            "LLaMA-3-Latest": "llama3.1:latest",
            "LlaMa-3-Groq-Tool-Use": "llama3-groq-tool-use:latest",
            "Qwen-2.5": "qwen2.5:32b",
        }
        self.model = self.available_models[model_name]

    def get_response(self, prompt : str) -> str:
        payload = {
            "model": self.model,
            "max_tokens": 18000,
            "prompt": prompt,
            "temperature": 0.6,
            "stream": False,
        }
        self.logger.debug(f'Prompting LLM with "{prompt}"')
        response = requests.post(self.url, json=payload)
        if response.status_code == 200:
            result = response.json()["response"]
            self.logger.debug(f'Received LLM response: "{result}"')
            return result
        else:
            raise Exception(f"Failed with status code: {response.status_code}")

class FAPSLLMClient(LLMClient):
    def __init__(self, logger : logging.Logger):
        self.logger = logger
        self.model = "llama3.1:70b"
        self.url = ""

    def get_response(self, prompt : str) -> str:
        payload = {
            "model": self.model,
            "max_tokens": 18000,
            "prompt": prompt,
            "temperature": 0.6,
            "stream": False,
        }
        self.logger.debug(f'Prompting LLM with "{prompt}"')
        response = requests.post(self.url, json=payload)
        if response.status_code == 200:
            result = response.json()["response"]
            self.logger.debug(f'Received LLM response: "{result}"')
            return result
        else:
            raise Exception(f"Failed with status code: {response.status_code}")