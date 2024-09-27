import requests
from abc import ABC, abstractmethod
import logging
import openai


# Base class for LLM clients
class LLMClient(ABC):
    def select_model(self, model_name: str):
        self.model = self.available_models[model_name]

    @abstractmethod
    def get_response(self, prompt: str) -> str:
        pass


# Siemens LLM client
class SiemensLLMClient(LLMClient):
    def __init__(self, logger: logging.Logger, api_key):
        self.logger = logger
        self.api_key = api_key
        self.url = "https://api.siemens.com/llm/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.available_models = {
            "mistral-7b-instruct": "mistral-7b-instruct",
            "starcoder2-3b": "starcoder2-3b",
            "bge-m3": "bge-m3",
        }
        # set default model
        self.model = "mistral-7b-instruct"

    def get_response(self, prompt: str) -> str:
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
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.url = "http://workstation.ferienakademie.de:11434/api/generate"
        self.available_models = {
            "LLaMA-3-70B": "llama3.1:70b",
            "LLaMA-3-Latest": "llama3.1:latest",
            "Gemma-2": "gemma2:27b",
            "LlaMa-3-Groq-Tool-Use": "llama3-groq-tool-use:latest",
            "Qwen-2.5": "qwen2.5:32b",
        }
        # set default model
        self.model = "llama3.1:70b"

    def get_response(self, prompt: str) -> str:
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
    def __init__(self, logger: logging.Logger, url: str):
        self.logger = logger
        self.url = url
        self.available_models = {
            "Llama3.1-70B": "llama3.1:70b",
            "Llama3.1-405B": "llama3.1:405b",
            "Llama3.2-Latest": "llama3.2:latest",
            "Gemma2-27B": "gemma2:27b",
            "Gemma2-Latest": "gemma2:latest",
            "Qwen-2.5-32B": "qwen2.5:32b",
            "Qwen-2.5-Latest": "qwen2.5:latest",
            "Mixtral-8x7B": "mixtral:8x7b",
            "Mixtral-8x22B": "mixtral:8x22b",
            "Mixtral-Latest": "mixtral:latest",
        }
        # Set default model
        self.model = "llama3.1:70b"

    def get_response(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "options": {"temperature": 0.6},
            "stream": False,
        }
        self.logger.debug(f'Prompting LLM with "{prompt}"')
        response = requests.post(self.url + "/api/generate", json=payload)
        if response.status_code == 200:
            result = response.json()["response"]
            self.logger.debug(f'Received LLM response: "{result}"')
            return result
        else:
            raise Exception(f"Failed with status code: {response.status_code}")


class OpenAILLMClient(LLMClient):
    def __init__(self, logger: logging.Logger, api_key: str, model="gpt-4o-mini"):
        self.logger = logger
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        self.available_models = {
            "GPT 4o mini": "gpt-4o-mini",
            "GPT 3.5 Turbo": "gpt-3.5-turbo",
            "Text Embedding 3 small": "text-embedding-3-small",
            "Dall-e 3": "dall-e-3",
            "TTS 1": "tts-1",
            "Whisper 1": "whisper-1",
        }
        # set default model
        self.model = "gpt-4o-mini"

    def get_response(self, prompt: str) -> str:
        self.logger.debug(f'Prompting LLM with "{prompt}"')
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        if response.status_code == 200:
            result = response["choices"][0]["message"]["content"].strip()
            self.logger.debug(f'Received LLM response: "{result}"')
            return result
        else:
            raise Exception(f"Failed with status code: {response.status_code}")
