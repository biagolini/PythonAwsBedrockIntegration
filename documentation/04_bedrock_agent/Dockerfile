# Use the official Python image
FROM python:3.12

# Update the package list and install zip
RUN apt update -y && apt install -y zip

# Set the working directory in the container
WORKDIR /home

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the Python dependencies in a folder named 'python'
RUN pip install --no-cache-dir -r requirements.txt -t python

# Zip the dependencies
RUN zip -r python_dependencies.zip python/