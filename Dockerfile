# Use Python 3.10.11 as base image
FROM python:3.10.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make the keep-alive script executable
RUN chmod +x keep_alive.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# Expose the port
EXPOSE 10000

# Run the bot and health check server
CMD ["sh", "-c", "python health_check.py & python main.py"] 