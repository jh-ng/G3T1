FROM python:3.9-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional required packages
RUN pip install --no-cache-dir psycopg2-binary flask-cors cloudinary python-dotenv

COPY . .

CMD ["python", "post.py"]
