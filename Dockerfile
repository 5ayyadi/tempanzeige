# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir poetry && poetry install

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Add support for running both main.py and the Telegram bot
COPY app/bot /app/bot

# Default command to run main.py
CMD ["poetry", "run", "python", "main.py"]
