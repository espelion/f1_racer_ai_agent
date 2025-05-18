FROM python:3.11.9-alpine

WORKDIR /app

COPY f1_agent.py .

COPY agent/ ./agent/
COPY project/ ./project/
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# In your console, limit your API KEY to just the Gemini API for safety
ENV GOOGLE_API_KEY="your-api-key-here"

ENTRYPOINT ["python", "f1_agent.py"]

CMD []