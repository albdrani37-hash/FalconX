FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-deps --no-build-isolation . && useradd --uid 10001 --create-home appuser
USER 10001:10001
EXPOSE 8765
CMD ["ctvi-audit-mcp", "--host", "0.0.0.0", "--port", "8765"]
