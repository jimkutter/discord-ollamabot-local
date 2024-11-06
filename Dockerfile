FROM python:3-bookworm

RUN apt install libffi-dev libnacl-dev python3-dev

RUN pip install uv

WORKDIR /app
COPY . .
RUN uv pip install --no-cache --system -r requirements.lock

CMD python ollamabot.py