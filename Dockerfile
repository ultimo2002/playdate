FROM python:3.13.2-alpine
LABEL org.opencontainers.image.source=https://github.com/ultimo2002/playdate

ENV PYTHONBUFFERED=1
ENV TERM=xterm-256color

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["python", "main.py"]
