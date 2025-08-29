# ReadRecall FastAPI Service

A FastAPI-based backend service for the ReadRecall book processing and summarization platform. This service provides APIs for user authentication, book management, AI-powered summarization, and character extraction.

## Features

- **User Authentication**: JWT-based authentication with registration and login
- **Book Management**: Upload, process, and manage EPUB/PDF books
- **AI Summarization**: Generate summaries at percentage intervals using Google Gemini
- **Character Extraction**: Extract and track characters throughout the book
- **Reading State**: Track user reading progress
- **Search**: Full-text search using OpenSearch
- **Database**: PostgreSQL with Neon support
- **File Processing**: Support for EPUB and PDF files

## Architecture

This service replaces the AWS Lambda-based backend with a unified FastAPI application that provides the same APIs:

### Original AWS Lambda Functions → FastAPI Endpoints

- `user_services/login_service` → `POST /api/auth/login`
- `user_services/register_service` → `POST /api/auth/register`  
- `user_services/get_me_service` → `GET /api/auth/me`
- `get_user_books` → `GET /api/books/`
- `generate_presigned_upload_url` → `POST /api/books/generate-upload-url`
- `book_summary_lambda` → `POST /api/summaries/{book_id}/generate`
- `character_summary_lambda` → `POST /api/characters/{book_id}/generate`
- `get_summary_by_progress` → `GET /api/summaries/{book_id}/by-progress`
- `get_character_by_progress` → `GET /api/characters/{book_id}`
- `normalize_books` → `POST /api/books/{book_id}/process`

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (Neon)
- **Search**: OpenSearch
- **AI**: Google Gemini API
- **Authentication**: JWT with bcrypt
- **File Processing**: PyPDF2, ebooklib
- **Testing**: pytest

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL database (Neon recommended)
- OpenSearch cluster
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
cd /Users/srk/readrecall/readrecallsvc
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
alembic upgrade head
```

### Configuration

Create a `.env` file with the following variables:

```env
# Database Configuration - Neon PostgreSQL
DATABASE_URL=postgresql://username:password@host:5432/database_name

# FastAPI Configuration
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
ENVIRONMENT=development

# OpenSearch Configuration
OPENSEARCH_HOST=https://your-opensearch-host.com
OPENSEARCH_USER=your-opensearch-user
OPENSEARCH_PASSWORD=your-opensearch-password

# AI Service Configuration
GEMINI_API_KEY=your-gemini-api-key

# Other configurations...
```

## Running the Service

### Development Mode

```bash
python run_dev.py
```

The service will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Books
- `GET /api/books/` - Get user's books
- `GET /api/books/{book_id}` - Get specific book
- `POST /api/books/upload` - Upload book file
- `POST /api/books/{book_id}/process` - Process uploaded book
- `POST /api/books/generate-upload-url` - Generate upload info

### Summaries
- `GET /api/summaries/{book_id}` - Get all summaries
- `GET /api/summaries/{book_id}/by-progress` - Get summary by progress
- `POST /api/summaries/{book_id}/generate` - Generate summaries
- `GET /api/summaries/{book_id}/search` - Search summaries

### Characters
- `GET /api/characters/{book_id}` - Get characters by progress
- `POST /api/characters/{book_id}/generate` - Generate character lists
- `GET /api/characters/{book_id}/search` - Search characters

### Reading State
- `GET /api/reading-state/{book_id}` - Get reading state
- `POST /api/reading-state/{book_id}` - Update reading state
- `DELETE /api/reading-state/{book_id}` - Delete reading state

### Health
- `GET /health` - Service health check
- `GET /test-gemini` - Test Gemini API connection
- `GET /test-opensearch` - Test OpenSearch connection

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app
```

## Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t readrecall-service .

# Run container
docker run -p 8000:8000 --env-file .env readrecall-service
```

### Railway/Render Deployment

1. Connect your repository
2. Set environment variables
3. Deploy with the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## File Structure

```
readrecallsvc/
├── app/
│   ├── api/          # API route handlers
│   ├── core/         # Core configuration and database
│   ├── models/       # SQLAlchemy models
│   ├── services/     # Business logic services
│   ├── utils/        # Utility functions and schemas
│   └── main.py       # FastAPI application
├── alembic/          # Database migrations
├── tests/            # Test suite
├── uploads/          # File upload directory
├── requirements.txt  # Python dependencies
├── run_dev.py       # Development server
└── README.md        # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.
