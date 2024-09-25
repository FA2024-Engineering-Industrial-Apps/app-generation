# from openai import OpenAI
import streamlit as st

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


llm = ChatOllama(
    model="llama3-groq-tool-use",
    temperature=0.5,
    seed=0
) # .bind_tools(tools) #8B

response_code = "st.write('_No code is generated yet_')"


with st.sidebar:
    st.title("Super app")
    st.caption("Generating an Industrial Edge App")

    with st.expander("Your API Settings"):
        model = st.radio("Model", ["gpt-4o", "llama3.1"])
        st.session_state["model"] = model

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


        st.chat_message("user").write(prompt)
        msg = llm.invoke(query_chat).content
        response_code = llm.invoke(query_code).content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)


st.title("App")
st.caption("Automatically generated via input at the site")

if st.button("Run Code"):
    st.code(response_code)
    exec(response_code)



