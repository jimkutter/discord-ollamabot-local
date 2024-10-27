FROM python:3-bookworm

RUN pip install uv

WORKDIR /app
COPY . .
RUN uv pip install --no-cache --system -r requirements.lock

CMD python ollamabot.py --help