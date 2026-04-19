# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user for security (Hugging Face Spaces requirement)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Set working directory to /app
WORKDIR $HOME/app
COPY --chown=user . $HOME/app

# Expose the port Hugging Face Spaces expects
EXPOSE 7860

# Run the application with Gunicorn
# Bind to 0.0.0.0:7860 as required by HF Spaces
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "run:app"]
