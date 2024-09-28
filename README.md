# App Generation

### Setup

To start the app install the `requirements.txt` via

```bash
pip install -r requirements.txt
```

You should also have `ollama` installed on your system. To execute the streamlit app execute

```bash
streamlit run streamlit_app.py
```

### Setup when running with docker
To start a docker-container running the app-generator, follow these steps:
    1. Open a (bash) terminal
    2. Start the docker-engine using  
    ```bash
    sudo service docker start
    ```
    2. Navigate to the repository where the docker-compose.yaml file is located
    3. Run the follwing command in your bash terminal
        ```bash
        docker-compose up
        ```
    4. Open the following URL in your favourite browser : http://localhost:8501/
    5. Enjoy our SUPER-APP!!!!

