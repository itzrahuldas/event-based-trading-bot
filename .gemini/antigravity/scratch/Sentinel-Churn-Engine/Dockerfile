# Base Image
FROM python:3.10-slim

# Set Working Directory
WORKDIR /app

# Install System Dependencies (if any required for some python packages like gcc)
# RUN apt-get update && apt-get install -y build-essential

# Copy Project Files
COPY . /app

# Install Project Dependencies
# Install as editable package to ensure src module resolution works
RUN pip install --no-cache-dir -e .

# Expose Streamlit Port
EXPOSE 8501

# Run Application
CMD ["streamlit", "run", "src/dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
