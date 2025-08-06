# 1. Use an official, clean Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy and install dependencies
# This copies only the requirements file first to leverage Docker's layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application code into the container
COPY . .

# 5. Define the command to run the application
# This "shell form" of CMD ensures that the $PORT variable provided by Railway
# is correctly interpreted by the shell.
CMD uvicorn app:app --host 0.0.0.0 --port $PORT
