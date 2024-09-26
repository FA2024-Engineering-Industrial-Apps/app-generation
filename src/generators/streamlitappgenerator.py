from .app_generator import AppGenerator
import time
import tempfile
import sys
import subprocess
from .promptadapter import StreamlitAppPromptAdapter
import logging

class StreamlitAppGenerator(AppGenerator):
    def __init__(self, logger : logging.Logger, app_name : str = 'My IE App', llm_model : str = "LLaMA-3-Latest", api_key : str = ""):
        super().__init__(logger, app_name, llm_model, api_key)
        self.prompt_adapter = StreamlitAppPromptAdapter()

    def run_pipeline(self, prompt):
        """Generate code using the selected LLM client."""
        self.prompt_adapter.update_user_prompt(prompt)
        return self.llm_client.get_response(self.prompt_adapter.app_prompt())

    def deploy(self, code: str, port=8052):
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

    def stop(self):
        if st.session_state.process:
            st.session_state.process.terminate()
            st.session_state.process = None
            st.success("App running stopped.")