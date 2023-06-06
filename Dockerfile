FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


ENV DJANGO_SETTINGS_MODULE=PriceAlert.settings


EXPOSE 8000


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
