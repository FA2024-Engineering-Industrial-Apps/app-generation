from langchain_core.tools import tool
import streamlit as st


@tool
def createTimer() -> None:
    """Creates a streamlit timer
    """
    