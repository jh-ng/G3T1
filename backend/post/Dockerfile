FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Add this line to install wheel before your requirements
RUN pip install --upgrade pip wheel setuptools
RUN pip install --no-cache-dir -r requirements.txt

COPY post.py .

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=post.py

EXPOSE 5000

CMD ["python", "post.py"]
