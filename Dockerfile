# Use a Python base image with OpenCV pre-installed, suitable for ARM architecture
FROM francoisgervais/opencv-python:latest

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential 

# Install numpy next
RUN pip install --no-binary numpy numpy

# Install other Python packages
RUN pip install RPi.GPIO gpiozero requests

# Copy the Python script into the container
COPY sensor-app.py ./



# Set the command to run the Python script
CMD ["python", "./sensor-app.py"]
