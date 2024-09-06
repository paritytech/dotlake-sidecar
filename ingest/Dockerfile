# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Make sure start-ingest.sh is executable
RUN chmod +x start-ingest.sh

# Run start-ingest.sh when the container launches
CMD ["./start-ingest.sh"]