import requests
from abc import ABC, abstractmethod
import logging
import openai
from typing import Callable, Any, Dict

class BadLLMResponseError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# Base class for LLM clients
class LLMClient(ABC):
    def __init__(self, logger: logging.Logger) -> None:
        super().__init__()
        self.logger: logging.Logger = logger
        self.secret: str = None
    
    @property
    def secret_name(self) -> str:
        pass
    
    @property
    def available_models(self) -> Dict[str, str]:
        pass
    
    def select_model(self, model_name: str):
        self.model = self.available_models[model_name]

    def set_secret(self, secret: str):
        if secret:
            self.secret = secret
        else:
            raise Exception("No secret (API key or URL) for LLM provided.")

    @abstractmethod
    def get_response(self, prompt: str) -> str:
        pass

    def get_validated_response(
        self, prompt: str, validator: Callable[[str], Any], tries=3
    ) -> Any:
        """
        Prompts the LLM and calls the validator method. Retries the prompt if the validator raises
        a BadLLMResponseError.

        @param prompt: Prompt to send to the LLM.
        @param validator: Function with arbitrary return value. Should raise a BadLLMResponseError if validation failed.
        @param tries: Maximum number of attempts before the error is propagated.
        @return: Return value of the validator function if it does not raise an exception.
        """
        attempt: int = 0
        succeeded: bool = False
        result: Any
        while (not succeeded) and (attempt < tries):
            try:
                result = validator(self.get_response(prompt))
                succeeded = True
            except BadLLMResponseError:
                if attempt == (tries - 1):
                    raise
            attempt = attempt + 1

        return result


# Siemens LLM client
class SiemensLLMClient(LLMClient):
    
    available_models = {
        "mistral-7b-instruct": "mistral-7b-instruct",
        "starcoder2-3b": "starcoder2-3b",
        "bge-m3": "bge-m3",
    }
    
    secret_name = 'Siemens API key'
    
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        self.url = "https://api.siemens.com/llm/v1/chat/completions"
        # set default model
        self.model = "mistral-7b-instruct"

    def get_response(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.secret}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 18000,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.6,
            "stream": False,
        }
        self.logger.debug(f'Prompting LLM with "{prompt}"')
        response = requests.post(self.url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"].strip()
            self.logger.debug(f'Received LLM response: "{result}"')
            return result
        else:
            raise Exception(f"Failed with status code: {response.status_code}")


# Workstation LLM client
class WorkstationLLMClient(LLMClient):
    
    available_models = {
        "LLaMA-3-70B": "llama3.1:70b",
        "LLaMA-3-Latest": "llama3.1:latest",
        "Gemma-2": "gemma2:27b",
        "LlaMa-3-Groq-Tool-Use": "llama3-groq-tool-use:latest",
        "Qwen-2.5": "qwen2.5:32b",
    }
    
    secret_name = None
    
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        self.url = "http://workstation.ferienakademie.de:11434/api/generate"
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
    
    available_models = {
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
    
    secret_name = 'FAPS LLM URL'
    
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
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
        response = requests.post(self.secret + "/api/generate", json=payload)
        if response.status_code == 200:
            result = response.json()["response"]
            self.logger.debug(f'Received LLM response: "{result}"')
            return result
        else:
            raise Exception(f"Failed with status code: {response.status_code}")


class OpenAILLMClient(LLMClient):
    
    available_models = {
        "GPT 4o": "gpt-4o",
        "GPT 4o mini": "gpt-4o-mini",
        "GPT 4 turbo": "gpt-4-turbo",
        "GPT 3.5 turbo": "gpt-3.5-turbo",
    }
    
    secret_name = 'OpenAI API key'
    
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        self.client: openai.OpenAI = None

    def set_secret(self, secret: str):
        self.secret = secret
        self.client = openai.OpenAI(api_key=self.secret)

    def get_response(self, prompt: str) -> str:
        if not self.client:
            raise Exception('API key not provided.')
            
        self.logger.debug(f'Prompting LLM with "{prompt}"')
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )

        result = completion.choices[0].message.content
        self.logger.debug(f'Received LLM response: "{result}"')
        return result
