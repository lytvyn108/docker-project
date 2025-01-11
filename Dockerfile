FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy application code
COPY app/ /app

# Install dependencies
RUN pip install flask faker requests mysql-connector-python


# Expose the port
EXPOSE 80

# Start the application
CMD ["python", "app.py"]