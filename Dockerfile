FROM python:3.13-slim as builder

# Install UV for dependency management
RUN pip install uv

WORKDIR /build

# Copy only dependency files
COPY pyproject.toml uv.lock ./

# Install build dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    uv venv /build/.venv && \
    . /build/.venv/bin/activate && \
    uv pip install --no-cache .

# Final stage
FROM python:3.13-slim

WORKDIR /app

# Copy only necessary files from builder stage
COPY --from=builder /build/.venv .venv
COPY squadcastify squadcastify

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/usr/local/bin:${PATH}"

ENTRYPOINT ["/app/.venv/bin/python", "-m", "squadcastify.main"]