# Use lightweight python image
FROM python:3.10-slim

# set working directory inside container
WORKDIR /app
# Install system deps (important for ML libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first 
COPY requirements.txt .

#Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Copy rest of the application code
COPY . .

#Expose port (Render )
EXPOSE 8000

#Start FastAPI 
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]
