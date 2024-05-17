# Use an official lightweight Python image.
FROM python:3.11-slim

# Environment variables ensure that the python output is set straight
# to the terminal without buffering it first
ENV PYTHONUNBUFFERED 1

# Create root directory for our project in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run manage.py to start your Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
