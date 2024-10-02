import logging
import os
import random

import streamlit as st
import streamlit.components.v1 as compenents
import subprocess

from appgenerator.app_generator import IEAppGenerator, AppGenerator
from appgenerator.llm_client import *
from appgenerator.generation_instance import GenerationInstance, AppArchitecture
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

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

st.set_page_config(page_title='IE App Generator')

st.title("Industrial Edge Application Generator")
st.markdown(
    "Provide the necessary requirements and associated details in the input below. The assistant will generate an app configuration for you."
)

if 'generating_app' not in st.session_state:
    st.session_state.generating_app = False  # Flag to indicate if the code is being generated.

if 'refining_prompt' not in st.session_state:
    st.session_state.refining_prompt = False  # Flag to indicate if the prompt is being refined.

if 'input_counter' not in st.session_state:
    st.session_state.input_counter = 0  # A counter to generate unique keys


def refine_input(app_generator: IEAppGenerator, user_input) -> str:
    st.session_state.refining_prompt = True
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

        # Initialize with system message if not already done
        initial_prompt = app_generator.prompt_fetcher.fetch("refinement")
        st.session_state.conversation_history.append(SystemMessage(initial_prompt))

    # Add the user's input to the conversation history
    st.session_state.conversation_history.append(HumanMessage(user_input))

    # Process the conversation and get the AI's response
    bot_response = refine_conversation(st.session_state.conversation_history)
    st.session_state.conversation_history.append(AIMessage(bot_response))

    if "User prompt is completed" not in bot_response:
        st.session_state.input_counter += 1
        st.rerun()

    else:
        st.write("User prompt is completed. Generating app...")
        st.session_state.generating_app = True
        return bot_response


def refine_conversation(conversation_history):
    response = llm_client.get_response(str(conversation_history))
    # TODO: add methods to llm_client to receive conversation_history as a parameter and send it to the LLM
    return response


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

# TODO
if not st.session_state.refining_prompt:
    app_name = st.text_input('App name', value='My IE App').strip()
    use_case_description = st.text_area("Describe the Industrial Edge App you want to create:", height=400)
else:
    app_name = st.text_input('App name', value='My IE App').strip()
    for msg in st.session_state.conversation_history:
        if msg.type != 'system':  # Skip 'system' messages
            with st.chat_message(msg.type):
                st.write(msg.content)
    use_case_description = st.text_area("Your response:", height=200, key=st.session_state.input_counter)


# Session State
if 'app_name' not in st.session_state:
    st.session_state['app_name'] = "My IE App"
if 'use_case_description' not in st.session_state:
    st.session_state['use_case_description'] = ""
if 'generated_app' not in st.session_state:
    st.session_state['generated_app'] = None

if st.button("Submit"):
    st.session_state['generated_app'] = None
    if llm_client.secret_name and not llm_client.secret:
        st.warning('Please configure an LLM to generate your app.')
    elif not app_name:
        st.warning("Please enter an app name.")
    elif not use_case_description:
        st.warning("Please enter a use case description.")
    else:
        app_generator: AppGenerator = IEAppGenerator(logger, llm_client)
        use_case_description = refine_input(app_generator, use_case_description)
        if st.session_state.generating_app:
            progress_indication = st.progress(0, 'Generating app...')

            def update_progress(steps_done: int, total_steps: int, current_step: str) -> None:
                progress_indication.progress(value=steps_done/total_steps, text=f'({steps_done + 1}/{total_steps + 1}) {current_step}')

            try:
                st.session_state['generated_app'] = app_generator.generate_app(app_name, use_case_description, update_progress)
                progress_indication.info('App successfully generated.')
            except BadLLMResponseError:
                progress_indication.error('App generation failed with the selected LLM. Please try again, or select a more powerful model.')

if st.session_state['generated_app']:
    generated_app: GenerationInstance = st.session_state['generated_app']
    if generated_app.placeholder_needed:
        instruction_list = generated_app.artifacts["instruction_list"]
        st.warning("The generated code is not complete.\nPlease update the code manually or provide more details in your description.\n" + instruction_list)
    
    col1, col2 = st.columns(2)
    preview_available: bool = generated_app.architecture in [AppArchitecture.FRONTEND_ONLY, AppArchitecture.FRONTEND_AND_BACKEND]
    deploy_locally = None
    with col1:
        deploy_locally = st.button(label='Deploy Locally', use_container_width=preview_available)
    with col2:
        if preview_available:
            if st.link_button(label='Preview App Web Interface', url='http://127.0.0.1:7654', use_container_width=True):
                start_preview(generated_app)
                
    if deploy_locally:
        st.info('Attempting to start the docker container.')
        process = subprocess.Popen(
                ['docker-compose', '-f', os.path.join(generated_app.root_path, 'docker-compose.yml'), 'up', '--build'],
                stdout=subprocess.PIPE,  # Redirect stdout
                stderr=subprocess.PIPE,  # Redirect stderr
                text=True  # Decodes output as text rather than bytes
            )