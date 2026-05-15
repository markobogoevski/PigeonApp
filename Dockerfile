FROM python:3.12-slim

WORKDIR /app
COPY app.py /app/app.py
COPY jokes.py /app/jokes.py
COPY dev_server.py /app/dev_server.py
COPY static /app/static

ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000
CMD ["python", "dev_server.py"]
