FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV

RUN pip install --upgrade pip && \
    pip install pydantic-settings && \
    pip install 'pydantic[email]' && \
    pip install .

CMD ["python", "main.py"]
