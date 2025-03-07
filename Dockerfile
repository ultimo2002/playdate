FROM python:3.9-slim
LABEL org.opencontainers.image.source=https://github.com/ultimo2002/playdate
WORKDIR /app

ENV PYTHONBUFFERED=1
ENV TERM=xterm-256color

# Install PostgreSQL development libraries
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["python", "main.py"]
