FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY footprint_recorder.py .
ENV PORT=8080 DB=/data/fp.sqlite SYMBOLS=BTC-USDT,ETH-USDT,SOL-USDT
VOLUME /data
EXPOSE 8080
CMD ["python", "footprint_recorder.py"]
