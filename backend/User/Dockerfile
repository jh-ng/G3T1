FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY userapp.py .

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=userapp.py

EXPOSE 5001

CMD ["python", "User_app.py"]