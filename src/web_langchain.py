from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
# from openai import OpenAI
import requests

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)


##### LLMs #####
def invoke_llm(query):
    if st.session_state["model"] == "llama3.1-Local":
        llm = ChatOllama(
            model="llama3-groq-tool-use",
            temperature=0.5,
            seed=0
        ) # .bind_tools(tools) #8B
        return llm.invoke(query).content

    elif st.session_state["model"] == "llama3.1-Remote":
        url = "http://workstation.ferienakademie.de:11434/api/generate"
        payload = {
            "model": "llama3.1:70b",
            "max_tokens": 18000,
            "prompt": query,
            "temperature": 0.6,
            "stream": False,
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            print("Failed with status code:", response.status_code)






##### Main app #####


with st.sidebar:
    st.title("Super app")
    st.caption("Generating an Industrial Edge App")
    st.markdown("Here the configuration can be specified")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])


    if prompt := st.chat_input():

        st.session_state.messages.append({"role": "user", "content": prompt})

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


        st.chat_message("user").write(prompt)
        msg = invoke_llm(query_chat)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
        # response_code = llm.invoke(query_code).content

    st.divider()

    with st.expander("Your API Settings"):
        model = st.radio("Model", ["llama3.1-Remote", "llama3.1-Local"])
        st.session_state["model"] = model

    st.link_button("View code in VSCode", "vscode://file/home/jonat/Documents/01_Studium/Ferienakademie/02_App/app-generation/src/frontend/index.html")



st.title("App")
st.caption("Automatically generated via input at the site")

components.iframe("http://localhost:8080", height=800)

