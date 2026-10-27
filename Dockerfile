FROM python:3.11-slim

# Avoid buffering and enable full terminal color support
ENV PYTHONUNBUFFERED=1 \
    TERM=xterm-256color \
    COLORTERM=truecolor

WORKDIR /app

# Install dependencies first for fast layer caching
COPY pyproject.toml requirements.txt README.md /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and install
COPY devopsherocli /app/devopsherocli
COPY tests /app/tests
RUN pip install --no-cache-dir -e .

# Create persistent user home
ENV HOME=/root
VOLUME ["/root/.devopsherocli"]

ENTRYPOINT ["devopsherocli"]
CMD []
