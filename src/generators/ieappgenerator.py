from .app_generator import AppGenerator

class IEAppGenerator(AppGenerator):
    def __init__(self, llm_model="LLaMA-3-Latest", api_key=""):
        super().__init__(llm_model, api_key)

    def run_pipeline(self, prompt):
        print(f'{prompt}')
        #self.llm_client.get_response()