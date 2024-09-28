import logging
import streamlit as st
import streamlit.components.v1 as compenents

from appgenerator.app_generator import IEAppGenerator, AppGenerator
from appgenerator.llm_client import *
from appgenerator.generation_instance import GenerationInstance, AppArchitecture

# TODO: 
from app_previewer import *

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="web_interface.log",
    filemode="w",
    encoding="utf-8",
    level=logging.DEBUG,
    format="[%(asctime)s][%(levelname)s] %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

st.title("Industrial Edge Application Generator")
st.markdown(
    "Provide the necessary requirements and associated details in the input below. The assistant will generate an app configuration for you."
)

with st.expander('LLM Configuration'):
    # LLM Selection
    llm_sources: Dict[str, LLMClient] = {
        'FAPS LLM' : FAPSLLMClient(logger),
        'Workstation LLM' : WorkstationLLMClient(logger),
        'Siemens LLM' : SiemensLLMClient(logger),
        'ChatGPT' : OpenAILLMClient(logger)
    }
    llm_client: LLMClient = llm_sources[st.radio("Select LLM source", llm_sources.keys(), horizontal=True)]
    llm_client.select_model(st.selectbox("Please choose an LLM Model", list(llm_client.available_models.keys())))

    # Input secret
    if llm_client.secret_name:
        secret = st.text_input(f'Please enter your {llm_client.secret_name}', type="password").strip()
        if secret:
            llm_client.set_secret(secret)
        else:
            st.warning(f'Please enter your {llm_client.secret_name}.')
        
st.markdown('### Industrial Edge App Details')

app_name = st.text_input('App name', value='My IE App').strip()
use_case_description = st.text_area("Describe the Industrial Edge App you want to create:", height=400)

if 'generated_app' not in st.session_state:
    st.session_state['generated_app'] = None

if st.button("Generate Code"):
    if llm_client.secret_name and not llm_client.secret:
        st.warning('Please configure an LLM to generate your app.')
    elif not app_name:
        st.warning("Please enter an app name.")
    elif not use_case_description:
        st.warning("Please enter a use case description.")
    else:
        app_generator: AppGenerator = IEAppGenerator(logger, llm_client)
        with st.spinner("Generating code..."):
            try:
                st.session_state['generated_app'] = app_generator.generate_app(app_name, use_case_description)
                st.info('App successfully generated.')
            except BadLLMResponseError:
                st.error('App generation failed with the selected LLM. Please try again, or select a more powerful model.')

if st.session_state['generated_app']:
    if st.session_state['generated_app'].architecture in [AppArchitecture.FRONTEND_ONLY, AppArchitecture.FRONTEND_AND_BACKEND]:
        if st.link_button(label='Preview App Web Interface', url='http://127.0.0.1:7654'):
            start_preview(st.session_state['generated_app'])