# Library-API-Service
Online management system for book borrowings

## Docker Commands

### Build and Run
```bash
# Build the containers
docker-compose build

# Start the containers
docker-compose up -d

# Stop the containers
docker-compose down
```

### Running Tests
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

### Development
- The API will be available at `http://localhost:8000`
- Admin interface: `http://localhost:8000/admin`
- API documentation: `http://localhost:8000/api/doc/swagger/`
