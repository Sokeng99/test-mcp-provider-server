FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bot_server.py .
COPY teams_bot.py .

# Expose port
EXPOSE 3978

# Run the application
CMD ["python", "bot_server.py"]
