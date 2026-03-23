FROM python:3.12-slim

WORKDIR /app

COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY apps/api/src /app/src
COPY apps/api/worker.py /app/worker.py
COPY core /app/core

ENV PYTHONPATH="/app"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
