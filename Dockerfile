FROM python:3.10

ENV TG_TOKEN = {TG_TOKEN}
ENV WEATH_TOKEN = {WEATH_TOKEN}

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "bot.py"]