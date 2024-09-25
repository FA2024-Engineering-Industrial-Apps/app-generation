import streamlit as st
import requests


def beautify_prompt(prompt):
    return (
        f"### System:\n You are an AI assistant that generates fully functional Streamlit Python apps based on the user's request. When the user provides a description or requirements, output only the complete Python code for a Streamlit app that fulfills the request. Do not include any explanations, comments, or text outside the code. Output only the raw code without any code blocks or formatting.\n### User:\n{prompt}\n",
    )


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


def get_response_from_llama(prompt):
    url = "http://workstation.ferienakademie.de:11434/api/generate"
    payload = {
        "model": "llama3.1",
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


st.title("Streamlit App Code Generator")
# LLM Selection
llm_options = ["Siemens LLM", "LLaMA 3"]
llm_model = st.selectbox("Select LLM model", llm_options)

# API Key input for Siemens models
if llm_model == "Siemens LLM":
    api_key = st.text_input("Enter your Siemens API key", type="password")
    if api_key:
        api_key = api_key
    else:
        st.warning("Please enter your Siemens API key.")

# Prompt input
prompt = st.text_area("Describe the Streamlit app you want to create:")

if st.button("Generate Code"):
    if prompt:
        prompt = beautify_prompt(prompt)[0]
        with st.spinner("Generating code..."):
            try:
                if llm_model == "Siemens LLM":
                    code = get_response_from_siemens(api_key, prompt)
                elif llm_model == "LLaMA 3":
                    code = get_response_from_llama(prompt)
                st.subheader("Generated Streamlit App Code:")
                st.code(code, language="python")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt.")
