import os


class PromptFetcher:
    def __init__(self, path: str = "prompts/") -> None:
        self.read_prompts(path)

    def read_prompts(self, path) -> None:
        self.prompt_lib = {}
        for _, _, files_name in os.walk(path):
            for file in files_name:
                with open(f"{path}/{file}", "r") as f:
                    self.prompts_lib[os.path.splitext(file)[0]] = f.read()

    def fetch(self, **kwargs) -> None:
        for name, content in kwargs.items():
            return self.prompts_lib[name].replace("[%text%]", content)
