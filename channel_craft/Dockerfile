# Use official pytho runtime as a parent image
FROM python:3.10-slim

# Set env variable
ENV PYTHONDONTWRITEBYTECODE 1 # this env variable help to speed up subsequent runtime of code.
ENV PYTHONUNBUFFERED 1

# Set a working directory in container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the host or current directory content into the container /app
COPY . /app/

#Expose port 800 to outside world
EXPOSE 8000

#Run Django Application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noasgi"]
