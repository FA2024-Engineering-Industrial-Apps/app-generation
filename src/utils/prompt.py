def streamlit_prompt(prompt: str) -> str:
    """Provide context to the prompt that can generate streamlit prompt."""
    return (
        f"### System:\n You are an AI assistant that generates fully functional Streamlit Python apps based on the user's request. When the user provides a description or requirements, output only the complete Python code for a Streamlit app that fulfills the request. Do not include any explanations, comments, or text outside the code. Output only the raw code without any code blocks or formatting.\n### User:\n{prompt}\n",
    )
