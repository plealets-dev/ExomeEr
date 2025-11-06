FROM python:3.10.11

ENV DOCKER=true

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    ffmpeg \
    libsndfile1 \
    swig \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# RUN ls -l
# CMD ["poetry", "run", "hypercorn", "/app/main:app", "--bind", "0.0.0.0:8000", "--reload"]
# CMD ["poetry", "run", "hypercorn", "app/main:app", "--bind", "0.0.0.0:8000", "--reload"]

# To build Docker
# Docker build -t genai . d
# To run docker
# docker run -p 3000:8000 -d genai