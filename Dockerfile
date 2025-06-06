# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8000

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT