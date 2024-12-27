# syntax=docker/dockerfile:1

FROM python:3.9-slim

# Create app directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# tests
CMD ["pytest", "tests/"]