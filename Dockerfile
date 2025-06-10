FROM python:3.13-slim

WORKDIR /app

# Copy all files at once to maintain the correct module structure
COPY . .

RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies directly (no need for virtual environment in container)
RUN pip install --upgrade pip && \
    pip install pydantic-settings && \
    pip install 'pydantic[email]' && \
    pip install click requests python-dotenv tqdm

# Create directory for mounting terraform state
RUN mkdir -p /terraform_state

ENTRYPOINT ["python", "-m", "squadcastify.main"]