# Use an official Python runtime as a parent image
FROM python:3.11-slim
# Set environment variables to prevent buffering and disable pycache
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /

# Copy just the requirements file into the container at /app
COPY reqs.txt /reqs.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /reqs.txt

# Copy the rest of the application code into the container at /app
COPY ./app ./app

# Expose port 8000 to allow external access to the FastAPI app
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
