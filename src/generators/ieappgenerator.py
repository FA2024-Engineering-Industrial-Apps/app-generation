from .app_generator import AppGenerator

class IEAppGenerator(AppGenerator):
    def __init__(self, llm_model="LLaMA-3-Latest", api_key=""):
        super().__init__(llm_model, api_key)

    def run_pipeline(self, prompt):
        print(f'{prompt}')
        #self.llm_client.get_response()
        #promptfetcher.fetch('define_restful_api', architecture_description])
        #promptfetcher.fetch('generate_web_interface', frontend_app_desc, restful_api_def)