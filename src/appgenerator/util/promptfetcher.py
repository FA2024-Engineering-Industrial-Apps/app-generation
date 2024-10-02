import os


class PromptFetcher:
    """
    Utility class to fetch and format prompts for LLM interactions.

    This class reads prompt templates from a specified directory, replaces placeholders
    with provided arguments, and returns the formatted prompts.
    
    @ivar prompt_lib: A dictionary containing prompt templates loaded from files.
    @ivar place_holder: The placeholder string to be replaced in the prompt templates.
    """
    
    def __init__(self, path: str, place_holder: str) -> None:
        """
        Initializes the PromptFetcher with the given path and placeholder.

        @param path: The directory path where prompt templates are stored.
        @param place_holder: The placeholder to be replaced with dynamic content in the prompts.
        """
        self.read_prompts(path)
        self.place_holder = place_holder
        

    def read_prompts(self, path) -> None:
        """
        Reads prompt templates from the specified directory and stores them in a dictionary.

        @param path: The directory path where prompt templates are located.
        """
        self.prompt_lib = {}
        for _, _, files_name in os.walk(path):
            for file in files_name:
                with open(f"{path}/{file}", "r") as f:
                    self.prompt_lib[os.path.splitext(file)[0]] = f.read()
                    

    def fetch(self, prompt, *args) -> None:
        """
        Fetches a prompt by its name and replaces placeholders with provided arguments.
        
        Placeholders are replaced one after another with the provided arguments. The first
        placeholder is replaced with the first argument, the second with the second, etc...

        @param prompt: The name of the prompt template to fetch.
        @param args: The dynamic arguments to replace placeholders in the prompt.

        @return: The formatted prompt string with placeholders replaced by the provided arguments.

        @raise KeyError: If the specified prompt name does not exist in the prompt library.
        """
        new_prompt = self.prompt_lib[prompt]
        for arg in args:
            new_prompt = new_prompt.replace(
                self.place_holder, arg, 1
            )  # Replace only the first occurrence
        return new_prompt
