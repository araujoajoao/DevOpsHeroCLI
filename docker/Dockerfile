FROM python:3.11-slim

# Avoid buffering and enable full terminal color support
ENV PYTHONUNBUFFERED=1 \
    TERM=xterm-256color \
    COLORTERM=truecolor

# Create non-root devops user for security (CIS Benchmark 4.1 / CWE-250)
RUN groupadd -g 1000 devops && \
    useradd -u 1000 -g devops -m -s /bin/bash devops

WORKDIR /home/devops/app

# Copy project definition and source code
COPY --chown=devops:devops pyproject.toml README.md /home/devops/app/
COPY --chown=devops:devops devopsherocli /home/devops/app/devopsherocli
COPY --chown=devops:devops tests /home/devops/app/tests
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

USER devops
ENV HOME=/home/devops
VOLUME ["/home/devops/.devopsherocli"]

ENTRYPOINT ["devopsherocli"]
CMD []
