FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml /app/
COPY smartgrid_mas /app/smartgrid_mas
COPY training /app/training
COPY main.py /app/main.py
COPY openenv.yaml /app/openenv.yaml

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health', timeout=3)"

CMD ["python", "main.py"]
