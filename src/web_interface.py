# %%
import streamlit as st
import requests
import tempfile
import subprocess
from streamlit_ace import st_ace


# %%
def get_response_from_siemens(api_key, prompt):
    url = "https://api.siemens.com/llm/v1/chat/completions"
    payload = {
        "model": "mistral-7b-instruct",
        "max_tokens": 18000,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6,
        "stream": False,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        print("Failed with status code:", response.status_code)


def get_response_from_workstation(prompt, model: str):
    ''' model options: llama3.1 or gemma2
    '''
    url = "http://workstation.ferienakademie.de:11434/api/generate"
    payload = {
        "model": model,
        "max_tokens": 18000,
        "prompt": prompt,
        "temperature": 0.6,
        "stream": False,
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        print("Failed with status code:", response.status_code)

    



def requirement_prompt(prompt):
    pass


def beautify_prompt(prompt:str) -> str:
    ''' Give context to the prompt
    '''
    return (
        f"### System:\n You are an AI assistant that generates fully functional Streamlit Python apps based on the user's request. When the user provides a description or requirements, output only the complete Python code for a Streamlit app that fulfills the request. Do not include any explanations, comments, or text outside the code. Output only the raw code without any code blocks or formatting.\n### User:\n{prompt}\n",
    )


def run_code(code):
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as tmp_file:
        tmp_file.write(code)
        tmp_file_name = tmp_file.name
    subprocess.run(["streamlit", "run", tmp_file_name])


st.title("Industrial Edge Application Generator")
# LLM Selection
st.markdown("Provide the necessary requirements and associated details in the input below. The assistant will generate an app configuration for you.")
llm_options = ["Siemens LLM", "LLaMA 3", "Gemma2"]


# Prompt input
prompt = st.text_area("Describe the Industrial Edge App you want to create:")

llm_model = st.radio("Select LLM model", llm_options)
# API Key input for Siemens models
if llm_model == "Siemens LLM":
    api_key = st.text_input("Enter your Siemens API key", type="password")
    if api_key:
        api_key = api_key
    else:
        st.warning("Please enter your Siemens API key.")

if "code" not in st.session_state:
    st.session_state.code = ""

if st.button("Generate Code"):
    if prompt:
        prompt = beautify_prompt(prompt)[0]
        with st.spinner("Generating code..."):
            try:
                if llm_model == "Siemens LLM":
                    st.session_state.code = get_response_from_siemens(api_key, prompt)
                elif llm_model == "LLaMA 3":
                    st.session_state.code = get_response_from_workstation(prompt, "llama3.1")
                elif llm_model == "Gemma2":
                    st.session_state.code = get_response_from_workstation(prompt, "gemma2:27b")
                # st.code(code, language="python")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt.")
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
    if st.button("Run Code"):
        exec(code)
