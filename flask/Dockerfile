# Use Python as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy the rest of the application code
COPY . /app

# Expose the Flask port
EXPOSE 5000

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]