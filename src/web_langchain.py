from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
# from openai import OpenAI
import utils.llm_client as llm_client
from utils.app_generator import StreamlitAppGenerator
import utils.prompt as prompt_module

import streamlit as st
import streamlit.components.v1 as components




generator = StreamlitAppGenerator()


st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)


##### LLMs #####

llm_options = [
    "LLaMA-3-Latest",
    "LlaMa-3-Groq-Tool-Use",
    "LLaMA-3-70B",
    "Gemma-2",
    "Qwen-2.5",
    "Siemens LLM",
]


def get_answer(prompt):
    general_description = "You are an expert assistant which creates a dashboard for a smart factory. You are using streamlit to create the dashboard."

    query_chat = [
        SystemMessage(content=f"{general_description}"),
        HumanMessage(content=prompt),
    ]
    

    query_code = [
        SystemMessage(content=f"{general_description} You only write executable python code! It is raw and not markdown highlighted!"),
        HumanMessage(content=prompt),
    ]

    # make query to string
    query_chat = "".join([msg.content for msg in query_chat])

    return generator.llm_client.get_response(query_chat)

# # Prompt input
# prompt = st.text_area("Describe the Industrial Edge App you want to create:")


##### Main app #####


chat_column, preview_column = st.columns([2, 3])



with chat_column:
    with st.container():
        st.title("App Generator")
        st.caption("Generating an Industrial Edge App")
        st.markdown("Here the configuration can be specified")

        with st.expander("Your API Settings"):
            llm_model = st.radio("Select LLM model", llm_options, horizontal=True)
            st.session_state["model"] = llm_model



        if llm_model == "Siemens LLM":
            api_key = st.text_input("Enter your Siemens API key", type="password")
            if api_key:
                generator.select_llm_client(llm_model, api_key)
            else:
                st.warning("Please enter your Siemens API key.")
        else:
            generator.select_llm_client(llm_model)


    ### Chat 
    with st.container():
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input():

            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})


            get_answer(prompt)

            
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)
            # response_code = llm.invoke(query_code).content



    # Check generated code on VS
    st.divider()

    with st.container():
        st.link_button("View code in VSCode", "vscode://file/home/jonat/Documents/01_Studium/Ferienakademie/02_App/app-generation/src/frontend/index.html")


with preview_column:
    st.title("App")
    st.caption("Automatically generated via input at the site")

    components.iframe("http://localhost:8080", height=800)




# def invoke_llm(query):
#     if st.session_state["model"] == "llama3.1-Local":
#         llm = ChatOllama(
#             model="llama3-groq-tool-use",
#             temperature=0.5,
#             seed=0
#         ) # .bind_tools(tools) #8B
#         return llm.invoke(query).content
