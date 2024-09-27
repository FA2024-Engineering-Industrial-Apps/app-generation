import streamlit as st
from generators.ieappgenerator import IEAppGenerator
from generators.streamlitappgenerator import StreamlitAppGenerator
import logging
import os
import traceback

logger = logging.getLogger(__name__)
logging.basicConfig(filename='web_interface.log', encoding='utf-8', level=logging.DEBUG, format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

generator = IEAppGenerator(logger)
st.title("Industrial Edge Application Generator")

# LLM Selection
st.markdown(
    "Provide the necessary requirements and associated details in the input below. The assistant will generate an app configuration for you."
)
llm_options = [
    "FAPS LLM",
    "Siemens LLM",
    "Gemma-2",
    "LLaMA-3-70B",
    "LLaMA-3-Latest",
    "LlaMa-3-Groq-Tool-Use",
    "Qwen-2.5"
]
llm_model = st.radio("Select LLM model", llm_options, horizontal=True)

# API Key input
if llm_model == "Siemens LLM":
    api_key = st.text_input("Enter your Siemens API key", type="password")
    if api_key:
        generator.select_llm_client(llm_model, api_key)
    else:
        st.warning("Please enter your Siemens API key.")
elif llm_model == "FAPS LLM":
    url = st.text_input("Enter the URL to the LLM", type="default")
    if url:
        generator.select_llm_client(llm_model, url)
    else:
        st.warning("Please enter the URL to the FAPS LLM.")
else:
    generator.select_llm_client(llm_model)

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

# Code display and run
if st.session_state.code:
    st.subheader("Generated Industrial Edge App Code:")
    code = st_ace(
        value=st.session_state.code,
        language="python",
        theme="monokai",
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        height=200,
    )
    if "process" not in st.session_state:
        st.session_state.process = None
    if st.button("Run App"):
        generator.deploy(code)
    if st.button("Stop App"):
        generator.stop()
