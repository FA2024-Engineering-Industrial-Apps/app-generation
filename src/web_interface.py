import streamlit as st
from streamlit_ace import st_ace
from utils.app_generator import StreamlitAppGenerator
from utils.prompt import StreamlitAppPromptAdapter

genertor = StreamlitAppGenerator()
prompt_adapter = StreamlitAppPromptAdapter(prompt="")
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
llm_model = st.radio("Select LLM model", llm_options, horizontal=True)

# API Key input
if llm_model == "Siemens LLM":
    api_key = st.text_input("Enter your Siemens API key", type="password")
    if api_key:
        genertor.select_llm_client(llm_model, api_key)
    else:
        st.warning("Please enter your Siemens API key.")
else:
    genertor.select_llm_client(llm_model)

# Prompt input
prompt = st.text_area("Describe the Industrial Edge App you want to create:")
prompt_adapter.update_user_prompt(prompt)
# Show requirements
if st.button("Show requirements"):
    requirement_prompt = prompt_adapter.requirement_prompt()
    with st.spinner("Finding Requirements..."):
        try:
            requirement = {
                "a": "Only web interface is needed.",
                "b": "Only a data analytics app without a web interface for the user is needed.",
                "c": "We need both a user web interface and a data analytics app.",
            }
            r = genertor.llm_client.get_response(requirement_prompt)
            if r == "a" or r == "b" or r == "c":
                st.write(requirement[r])
                st.write(
                    genertor.llm_client.get_response(
                        prompt_adapter.task_distribution_prompt()
                    )
                )
            else:
                st.write("Not clear")

        except Exception as e:
            st.error(f"An error occurred: {e}")


# Generate code
if "code" not in st.session_state:
    st.session_state.code = ""

if st.button("Generate Code"):
    if prompt:
        prompt_adapter.update_user_prompt(prompt)
        streamlit_prompt = prompt_adapter.app_prompt()
        with st.spinner("Generating code..."):
            try:
                st.session_state.code = genertor.run_pipeline(streamlit_prompt)
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
        genertor.deploy(code)
    if st.button("Stop App"):
        genertor.stop()
