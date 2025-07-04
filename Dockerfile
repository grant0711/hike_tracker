# Stage 1: Build the Python virtual environment
FROM python:3.13-bullseye AS builder

# Install build-time dependencies for C extensions + pipenv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv and create the virtual environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir pipenv
WORKDIR /opt/app
COPY Pipfile Pipfile.lock ./
RUN PIPENV_VENV_IN_PROJECT=1 pipenv sync --system

# ----------------------------------------------------------------

# Stage 2: Final production image
FROM python:3.13-bullseye AS final

# Install runtime dependencies for the app and Garmin tools
# These are needed to run the application, not just build it
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    garmin-forerunner-tools \
    usbutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the Python environment from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set up app directory and copy application code
WORKDIR /app
COPY . .
