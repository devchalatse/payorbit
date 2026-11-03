FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system payorbit && adduser --system --ingroup payorbit payorbit

COPY pyproject.toml README.md ./
COPY app ./app

RUN python -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

USER payorbit

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
