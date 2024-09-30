FROM python:3.12

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3-setuptools \
        python3-pip \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app
COPY . /opt/app

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH
RUN poetry config virtualenvs.create false && poetry install

CMD ["python", "main.py"]
