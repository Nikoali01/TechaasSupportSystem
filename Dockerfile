FROM python:3.12-slim-bullseye as python-base

WORKDIR /app
COPY . .

# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_VERSION=1.8.2
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv

# Tell Poetry where to place its cache and virtual environment
ENV POETRY_CACHE_DIR=/opt/.cache

RUN apt update -y && apt upgrade -y && apt install curl -y
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
RUN poetry export -f requirements.txt >> requirements.txt

# Create a new stage from the base python image
FROM python:3.12-slim-bullseye as runtime

WORKDIR /app

COPY . .

COPY --from=python-base /app/requirements.txt .

RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose port of container
EXPOSE 8501

# Run Application
CMD streamlit run main.py