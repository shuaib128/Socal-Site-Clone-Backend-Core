# Use official Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Run makemigrations for Users, then migrate everything, collect static files, and start the server
CMD ["sh", "-c", "python manage.py makemigrations Users && python manage.py migrate Users && python manage.py makemigrations Posts && python manage.py migrate Posts && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
