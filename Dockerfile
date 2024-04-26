FROM arm32v7/python:3.9-slim

WORKDIR /app

# Copy TestSensor.py, entrypoint.sh, and the virtual environment into the container
COPY Sensor.py entrypoint.sh ./
COPY myenv ./myenv

# Set execute permissions for entrypoint.sh
RUN chmod +x entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]