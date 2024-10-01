import logging
import streamlit as st
import streamlit.components.v1 as compenents

from appgenerator.app_generator import IEAppGenerator, AppGenerator
from appgenerator.llm_client import *
from appgenerator.generation_instance import GenerationInstance, AppArchitecture
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

st.set_page_config(page_title='IE App Generator')

st.title("Industrial Edge Application Generator")
st.markdown(
    "Provide the necessary requirements and associated details in the input below. The assistant will generate an app configuration for you."
)

with st.expander('LLM Configuration'):
    # LLM Selection
    llm_sources: Dict[str, LLMClient] = {
        'ChatGPT' : OpenAILLMClient(logger),
        'FAPS LLM' : FAPSLLMClient(logger),
        'Workstation LLM' : WorkstationLLMClient(logger),
        'Siemens LLM' : SiemensLLMClient(logger)
    }
    llm_client: LLMClient = llm_sources[st.radio("Select LLM source", llm_sources.keys(), horizontal=True)]
    st.caption('For best performance it is highly recommended to use the GPT-4o model from OpenAI.')
    llm_client.select_model(st.selectbox("Please choose an LLM Model", list(llm_client.available_models.keys())))

    # Input secret
    if llm_client.secret_name:
        secret = st.text_input(f'Please enter your {llm_client.secret_name}', type="password").strip()
        if secret:
            llm_client.set_secret(secret)
        else:
            st.warning(f'Please enter your {llm_client.secret_name}.')
        
st.markdown('### Industrial Edge App Details')


# Session State
if 'app_name' not in st.session_state:
    st.session_state['app_name'] = "My IE App"
if 'use_case_description' not in st.session_state:
    st.session_state['use_case_description'] = ""
if 'generated_app' not in st.session_state:
    st.session_state['generated_app'] = None

app_name = st.text_input('App name', value=st.session_state["app_name"]).strip()
use_case_description = st.text_area("Describe the Industrial Edge App you want to create:", value=st.session_state['use_case_description'], height=400)


col1, col2 = st.columns([5, 1])

with col1:
    if st.button("Generate Code"):
        st.session_state['generated_app'] = None
        if llm_client.secret_name and not llm_client.secret:
            st.warning('Please configure an LLM to generate your app.')
        elif not app_name:
            st.warning("Please enter an app name.")
        elif not use_case_description:
            st.warning("Please enter a use case description.")
        else:
            app_generator: AppGenerator = IEAppGenerator(logger, llm_client)
            progress_indication = st.progress(0, 'Generating app...')
            
            def update_progress(steps_done: int, total_steps: int, current_step: str) -> None:
                progress_indication.progress(value=steps_done/total_steps, text=f'({steps_done + 1}/{total_steps + 1}) {current_step}')
                
            try:
                st.session_state['generated_app'] = app_generator.generate_app(app_name, use_case_description, update_progress)
                progress_indication.info('App successfully generated.')
            except BadLLMResponseError:
                progress_indication.error('App generation failed with the selected LLM. Please try again, or select a more powerful model.')
with col2:
    if st.button("Demo"):
        st.session_state.app_name = "Material Count"
        st.session_state.use_case_description = '''I want to display a counter of the material used in my "Pick and Place" machine.

The part consumption is published by the pick and place machine on the Databus (MQTT). Whenever the machine uses up a component (transistor, capacitor or resistor) it sends a message containing the name of the component used on the “material_consumption” channel/topic. The name is sent as a plain string.

The app shall listen to the messages sent by the machine. Every time it receives a message it shall decrement a counter representing the number of components left. Initialize the counter of all components to 200.

The app shall offer a web interface displaying a table containing the count of components left for each material. The table shall be full screen. The display shall update automatically every 5 seconds.'''
        st.rerun()

if st.session_state["generated_app"]:
    if st.session_state['generated_app'].architecture in [AppArchitecture.FRONTEND_ONLY, AppArchitecture.FRONTEND_AND_BACKEND]:
        if st.link_button(label='Preview App Web Interface', url='http://127.0.0.1:7654'):
            start_preview(st.session_state['generated_app'])
            
    if st.session_state['generated_app'].placeholder_needed:
        st.warning("Placeholder detected in the generated code.")
