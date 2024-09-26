from abc import ABC, abstractmethod


class PromptAdapter(ABC):
    @abstractmethod
    def __init__(self, prompt: str = "") -> None:
        self.user_prompt = prompt

    def update_user_prompt(self, prompt: str) -> str:
        self.user_prompt = prompt


class StreamlitAppPromptAdapter(PromptAdapter):
    def __init__(self, prompt: str = "") -> None:
        super().__init__(prompt)

    def app_prompt(self) -> str:
        """Provide context to the prompt that can generate streamlit prompt."""
        return f"### System:\n You are an AI assistant that generates fully functional Streamlit Python apps based on the user's request. When the user provides a description or requirements, output only the complete Python code for a Streamlit app that fulfills the request. Do not include any explanations, comments, or text outside the code. Output only the raw code without any code blocks or formatting.\n### User:\n{self.user_prompt}\n"

    def requirement_prompt(self) -> str:
        return f"### System:\nYou are a decision maker for designing software architectures. Your task is to analyze a prompt given by a user to determine which components are needed in a system. The user gives a prompt that includes what kind of industrial edge app from Siemens he wants. The system can have one of two components or both. The possible components are a user web interface and a data analytics component. The user web interface serves just for displaying (output) the data from the data analytics component or interacting with it. The data analytics component fetches data from a MQTT data bus to interact with the machines or process the data. Your task is now to decide on what component is needed based on the user prompt so that it fulfills the user's needs. You have to write ‘a’, if we only need a web interface.\nWrite ‘b’, if we only need a data analytics app without a web interface for the user.\nWrite ‘c’, if we need both a user web interface and a data analytics app.\nWrite no other text, just the outputs I provided to you. You will now get the user prompt. ### User:\n{self.user_prompt}"

    def task_distribution_prompt(self) -> str:
        return f"### System:\nYou are a software engineer working on the detailed design of a software architecture comprising two components. The backend program is responsible for communication with shop floor machines via MQTT. Furthermore, it is responsible for data processing and machine control. The frontend serves as the user interface and displays data, but does not process any data itself. It also may offer controls to the machines. The exact behavior of the frontend and the backend depends on the use-case description and software requirements provided below. Here is what I want you to do: Starting with the backend program: - summarize its task given the specific use-case. - define the data flow. Specify what data needs to be calculated/processed. Specify how to calculate this data. - summarize the interaction between the backend and the shop floor machine via MQTT. Include specific details including the data exchanged, its format, and the topic name. Continuing with the frontend program: - summarize its task including the interface layout. - specify what data needs to be queried from the backend. Finally, describe the interaction between the frontend and backend (what data needs to be exchanged, how often). Do not specify API endpoints, as these will be determined later. Also do not define any further details about the technologies than already provided. Do not provide any further recommendation of possible future features. Do not provide a rationale to your response. Make sure all information in the use-case and software requirements are included in your response, because we will only use your response in the future for development. Make sure no information is lost. ### User:\nHere is the use-case description and software requirements: {self.user_prompt}"


class IEAppPromptAdapter(PromptAdapter):
    def __init__(self, prompt: str = "") -> None:
        super().__init__(prompt)

    def requirement_prompt(self) -> str:
        return f"### System:\nYou are a decision maker for designing software architectures. Your task is to analyze a prompt given by a user to determine which components are needed in a system. The user gives a prompt that includes what kind of industrial edge app from Siemens he wants. The system can have one of two components or both. The possible components are a user web interface and a data analytics component. The user web interface serves just for displaying (output) the data from the data analytics component or interacting with it. The data analytics component fetches data from a MQTT data bus to interact with the machines or process the data. Your task is now to decide on what component is needed based on the user prompt so that it fulfills the user's needs. You have to write ‘a’, if we only need a web interface.\nWrite ‘b’, if we only need a data analytics app without a web interface for the user.\nWrite ‘c’, if we need both a user web interface and a data analytics app.\nWrite no other text, just the outputs I provided to you. You will now get the user prompt. ### User:\n{self.user_prompt}"

    def task_distribution_prompt(self) -> str:
        return f"### System:\nYou are a software engineer working on the detailed design of a software architecture comprising two components. The backend program is responsible for communication with shop floor machines via MQTT. Furthermore, it is responsible for data processing and machine control. The frontend serves as the user interface and displays data, but does not process any data itself. It also may offer controls to the machines. The exact behavior of the frontend and the backend depends on the use-case description and software requirements provided below. Here is what I want you to do: Starting with the backend program: - summarize its task given the specific use-case. - define the data flow. Specify what data needs to be calculated/processed. Specify how to calculate this data. - summarize the interaction between the backend and the shop floor machine via MQTT. Include specific details including the data exchanged, its format, and the topic name. Continuing with the frontend program: - summarize its task including the interface layout. - specify what data needs to be queried from the backend. Finally, describe the interaction between the frontend and backend (what data needs to be exchanged, how often). Do not specify API endpoints, as these will be determined later. Also do not define any further details about the technologies than already provided. Do not provide any further recommendation of possible future features. Do not provide a rationale to your response. Make sure all information in the use-case and software requirements are included in your response, because we will only use your response in the future for development. Make sure no information is lost. ### User:\nHere is the use-case description and software requirements: {self.user_prompt}"
