FROM python:3.12
LABEL authors="ask4git"

WORKDIR /app

RUN apt-get update && apt-get install -y python3-venv python3-pip curl

# Install pipx so we can install poetry system wide
RUN python3 -m pip install --no-cache-dir --user pipx && \
    python3 -m pipx ensurepath

ENV PATH=/root/.local/bin:$PATH

# Install poetry to install our dependencies
RUN pipx install poetry==1.8.3
ENV PATH=/root/.local/bin:$PATH
ENV DJANGO_SETTINGS_MODULE=snapsapi.config.settings.docker

COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false && \
        poetry config installer.max-workers 10 && \
        poetry install --no-interaction --no-dev --no-ansi --no-root -vvv && \
        poetry cache clear pypi --all -n

COPY . /app
EXPOSE 8000
RUN ["chmod", "+x", "./entrypoint.sh"]
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "snapsapi.config.wsgi:application", "--bind", "0.0.0.0:8000", "--reload"]
