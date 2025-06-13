FROM python:3.13-slim

WORKDIR /app

# Install UV for better dependency management
RUN pip install uv

# Copy only the files needed for dependency installation first
COPY pyproject.toml uv.lock ./

# Install build tools and install dependencies using UV
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    uv venv && \
    . .venv/bin/activate && \
    uv pip install .

# Now copy the rest of the application
COPY . .

# Create directory for mounting terraform state
RUN mkdir -p /terraform_state

ENTRYPOINT ["uv", "run", "-m", "squadcastify.main"]