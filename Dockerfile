FROM python:3.11.9-alpine

WORKDIR /app

COPY f1_agent.py .
COPY logger.json .

COPY agent/ ./agent/
COPY project/ ./project/
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "f1_agent.py"]

CMD []