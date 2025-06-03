# Library API Service

A comprehensive library management system built with Django REST Framework, featuring book borrowing, user management, payment processing, and Telegram bot integration.

## Features

- 📚 Book management and borrowing system
- 👥 User authentication and authorization
- 💳 Payment processing with Stripe integration
- 🤖 Telegram bot for notifications and interactions
- 📱 RESTful API with comprehensive documentation
- 🔄 Asynchronous task processing with Celery
- 📊 Admin dashboard for system management
- 📨 Email notifications
- 🔒 JWT authentication
- 📝 API documentation with Swagger/OpenAPI

## Tech Stack

- **Backend Framework:** Django 5.2
- **API Framework:** Django REST Framework
- **Database:** PostgreSQL
- **Task Queue:** Celery with Redis
- **Web Server:** Nginx
- **Application Server:** Gunicorn
- **Payment Processing:** Stripe
- **Bot Framework:** Aiogram
- **Documentation:** DRF Spectacular & Swagger

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- PostgreSQL 14
- Redis
- Stripe account (for payment processing)
- Telegram Bot Token

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=library_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Stripe
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

## Installation and Setup

1. Clone the repository:
```bash
git clone https://github.com/PrimeGlorious/Library-API-Service
cd Library-API-Service
```

2. Create and configure the `.env` file as shown above.

3. Build and start the containers:
```bash
# Build the containers
docker-compose build

# Start the containers
docker-compose up

# To run in detached mode (background)
docker-compose up -d

# To stop the containers
docker-compose down
```

4. The application will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`

## Project Structure

```
Library-API-Service/
├── books/              # Book management app
├── borrowings/         # Book borrowing functionality
├── config/            # Project configuration
├── notifications/     # Notification system
├── payments/         # Payment processing
├── user/             # User management
├── nginx/            # Nginx configuration
├── staticfiles/      # Static files
├── media/           # User-uploaded files
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Development

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Running Tests

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific app tests
docker-compose exec web python manage.py test books
docker-compose exec web python manage.py test borrowings
docker-compose exec web python manage.py test user

# Run specific test file
docker-compose exec web python manage.py test books.tests.tests_books_views
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.
