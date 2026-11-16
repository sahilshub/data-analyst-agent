FROM python:3.12-slim

# Copy the uv binary from its official image instead of installing it with pip.
COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /bin/uv

WORKDIR /app

# Use the image's Python (never download another), and precompile for faster startup.
ENV UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Dependencies first: this layer is rebuilt only when the lockfile changes,
# so a code-only change rebuilds in seconds.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev

COPY app ./app

# Do not run as root inside the container.
RUN useradd --create-home appuser
USER appuser

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

# One worker: the production box has 1 GB of memory.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
