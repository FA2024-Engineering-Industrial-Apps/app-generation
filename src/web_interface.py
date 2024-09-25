import streamlit as st
from streamlit_ace import st_ace
from utils.code_generator import AppGenerator
import utils.prompt as prompt_module

genertor = AppGenerator()
st.title("Industrial Edge Application Generator")

# LLM Selection
st.markdown(
    "Provide the necessary requirements and associated details in the input below. The assistant will generate an app configuration for you."
)
llm_options = [
    "Siemens LLM",
    "Gemma-2",
    "LLaMA-3-70B",
    "LLaMA-3-Latest",
    "LlaMa-3-Groq-Tool-Use",
    "Qwen-2.5",
]

# Prompt input
prompt = st.text_area("Describe the Industrial Edge App you want to create:")
llm_model = st.radio("Select LLM model", llm_options, horizontal=True)

# Select model and API Key input
if llm_model == "Siemens LLM":
    api_key = st.text_input("Enter your Siemens API key", type="password")
    if api_key:
        genertor.select_llm_client(llm_model, api_key)
    else:
        st.warning("Please enter your Siemens API key.")
else:
    genertor.select_llm_client(llm_model)

# Generate code
if "code" not in st.session_state:
    st.session_state.code = ""

if st.button("Generate Code"):
    if prompt:
        prompt = prompt_module.streamlit_prompt(prompt)[0]
        with st.spinner("Generating code..."):
            try:
                st.session_state.code = genertor.generate_code(prompt)
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
        genertor.run_code(code)
    if st.button("Stop App"):
        genertor.stop_code()
