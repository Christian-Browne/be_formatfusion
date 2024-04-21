FROM python:3.12.3-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Run the FastAPI application using uvicorn server
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}