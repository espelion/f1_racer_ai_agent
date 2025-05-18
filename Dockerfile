FROM python:3.11-slim

WORKDIR /app

COPY f1_agent.py .

COPY agent/ ./agent/
COPY project/ ./project/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "f1_agent.py"]

CMD []