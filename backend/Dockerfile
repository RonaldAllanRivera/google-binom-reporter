# Use official lightweight Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install psycopg2 dependencies
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY backend/ /app/

# Expose Django port
EXPOSE 8000

# Start Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
