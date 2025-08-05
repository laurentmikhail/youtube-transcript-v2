# 1. Use an official Python base image
# This gives us a clean Linux OS with Python pre-installed.
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy and install dependencies
# This copies the requirements file first to leverage Docker's caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application code
COPY . .

# 5. Define the command to run the application
# This is what the Procfile used to do. Note that Railway provides the $PORT variable.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
