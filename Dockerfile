# 1. Use a clean, official Python base image
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory
WORKDIR /app

# 4. Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the entrypoint script and the rest of the app
COPY ./entrypoint.sh .
COPY . .

# 6. Make the entrypoint script executable
RUN chmod +x ./entrypoint.sh

# 7. Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# 8. Define the command that the entrypoint will run
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "$PORT"]
