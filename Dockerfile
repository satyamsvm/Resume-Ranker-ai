FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && python -m spacy download en_core_web_sm
COPY . .
RUN useradd -m appuser && chown -R appuser /app
USER appuser
ENV PORT=8000
EXPOSE 8000
CMD gunicorn -w 2 -b 0.0.0.0:${PORT} "run:app"
