FROM python:3.11-slim
WORKDIR /opt/project
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "src.pipeline", "--year", "2026", "--month", "1", "--sample-rows", "100000"]
