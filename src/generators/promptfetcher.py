import os
import re


class PromptFetcher:
    def __init__(self, path: str = "prompts/", place_holder="[%text%]") -> None:
        self.read_prompts(path)
        self.place_holder = place_holder

    def read_prompts(self, path) -> None:
        self.prompt_lib = {}
        for _, _, files_name in os.walk(path):
            for file in files_name:
                with open(f"{path}/{file}", "r") as f:
                    self.prompts_lib[os.path.splitext(file)[0]] = f.read()

    def fetch(self, prompt, *args) -> None:
        new_prompt = self.prompt_lib[prompt]
        for arg in args:
            new_prompt = new_prompt.replace(
                self.place_holder, arg, 1
            )  # Replace only the first occurrence
        return new_prompt
