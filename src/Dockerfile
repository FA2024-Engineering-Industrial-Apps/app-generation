# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY ./requirements.txt .

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install socat
RUN apt update
RUN yes | apt install socat

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Expose the desired port (optional, but for documentation purposes)
EXPOSE 8501

# Set environment variables (optional, add as needed)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define the command to run the backend (adjust as necessary)
CMD ["streamlit", "run" ,"web_interface.py"]
