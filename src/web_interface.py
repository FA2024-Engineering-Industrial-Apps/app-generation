import streamlit as st
import streamlit.components.v1 as compenents
from generators.ieappgenerator import IEAppGenerator

import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="web_interface.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="[%(asctime)s][%(levelname)s] %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

generator = IEAppGenerator(logger)

# st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
# panel_generator, panel_app = st.columns([1, 1])

st.title("Industrial Edge Application Generator")

# LLM Selection
st.markdown(
    "Provide the necessary requirements and associated details in the input below. The assistant will generate an app configuration for you."
)
source_options = ["FAPS LLM", "Workstation LLM", "Siemens LLM", "ChatGPT"]
source = st.radio("Select LLM source", source_options, horizontal=True)

# Select model
if source == "Siemens LLM":
    api_key = st.text_input("Enter your Siemens API key", type="password")
    if api_key:
        generator.select_llm_client(source, api_key)
    else:
        st.warning("Please enter your Siemens API key.")
elif source == "FAPS LLM":
    url = st.text_input("Enter the URL to the LLM", type="default")
    if url:
        generator.select_llm_client(source, url)
    else:
        st.warning("Please enter the URL to the FAPS LLM.")
elif source == "ChatGPT":
    api_key = st.text_input("Enter your ChatGPT API key", type="password")
    if api_key:
        generator.select_llm_client(source, api_key)
    else:
        st.warning("Please enter your ChatGPT API key.")
else:
    generator.select_llm_client(source)

model_name = st.selectbox(
    "Please choose an LLM Model",
    list(generator.llm_client.available_models.keys()),
)
generator.llm_client.select_model(model_name)

# Prompt input
prompt = st.text_area("Describe the Industrial Edge App you want to create:")

# Generate code
if "code" not in st.session_state:
    st.session_state.code = ""

if st.button("Generate Code"):
    if prompt:
        with st.spinner("Generating code..."):
            try:
                st.session_state.code = generator.run_pipeline(prompt)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt.")


st.divider()




if st.button("After app is generated"):
    compenents.iframe("http://localhost:8080", height=800)
    # os.system("python3 -m ~/dist/my_ie_app/program/src/server.py")

