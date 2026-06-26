# Use official Python image for the backend and Streamlit UI
FROM python:3.11-slim

# Set up the backend
WORKDIR /app/backend
COPY syntra_backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY syntra_backend/ .

# Set up Streamlit
WORKDIR /app
COPY streamlit_app.py .
COPY start.sh .
RUN chmod +x start.sh

# Expose Hugging Face Space port
EXPOSE 7860

# Start both services
CMD ["./start.sh"]
