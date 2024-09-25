import time
import tempfile
import sys
import subprocess
import streamlit as st
from .llm_client import SiemensLLMClient, WorkstationLLMClient


class AppGenerator:
    def __init__(self):
        self.llm_client = None
        self.prompt = ""

    def select_llm_client(self, llm_model, api_key=""):
        """Select the appropriate LLM client based on user choice."""
        if llm_model == "Siemens LLM":
            if api_key:
                api_key = api_key
                self.llm_client = SiemensLLMClient(api_key)
            else:
                raise Exception("No API Key.")
        else:
            self.llm_client = WorkstationLLMClient(llm_model)

    def generate_code(self, prompt):
        """Generate code using the selected LLM client."""
        return self.llm_client.get_response(prompt)

    def run_code(self, code: str, port=8052):
        if st.session_state.process:
            st.session_state.process.terminate()
            st.session_state.process = None

        # Save the code to a temporary file
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        # Command to run the Streamlit app
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            tmp_file_path,
            "--server.port",
            str(port),
            "--server.headless",
            "true",
            "--server.enableCORS",
            "false",
            "--server.enableXsrfProtection",
            "false",
        ]
        # Start the Streamlit server as a subprocess
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        st.session_state.process = process
        # Wait briefly to allow the server to start
        time.sleep(3)
        # Embed the app using an iframe
        st.markdown(
            f"""
			<iframe src="http://localhost:{port}" width="100%" height="600" frameborder="0"></iframe>
		""",
            unsafe_allow_html=True,
        )

    def stop_code(self):
        if st.session_state.process:
            st.session_state.process.terminate()
            st.session_state.process = None
            st.success("App running stopped.")
