FROM python:3.9-slim
WORKDIR /app
# Install PostgreSQL development libraries
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD uvicorn main:app