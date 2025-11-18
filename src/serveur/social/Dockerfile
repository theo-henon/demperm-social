FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install -e .

# Copy project
COPY social_api ./social_api

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python social_api/manage.py migrate && python social_api/manage.py runserver 0.0.0.0:8000"]
