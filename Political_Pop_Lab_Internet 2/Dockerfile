FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py bots.py legislation.py question-bank.json ./
COPY public ./public
ENV PORT=8002
EXPOSE 8002
CMD ["python", "server.py"]
