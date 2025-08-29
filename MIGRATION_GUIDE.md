# AWS to FastAPI Migration Guide

This document outlines the migration from the AWS Lambda-based backend to the new FastAPI-based service.

## API Endpoint Mapping

### Authentication Services

| AWS Lambda | FastAPI Endpoint | Description |
|------------|------------------|-------------|
| `user_services/login_service` | `POST /api/auth/login` | User login with JWT token |
| `user_services/register_service` | `POST /api/auth/register` | User registration |
| `user_services/get_me_service` | `GET /api/auth/me` | Get current user info |

### Book Management

| AWS Lambda | FastAPI Endpoint | Description |
|------------|------------------|-------------|
| `get_user_books` | `GET /api/books/` | Get all books for user |
| `generate_presigned_upload_url` | `POST /api/books/generate-upload-url` | Generate upload info |
| N/A | `POST /api/books/upload` | Direct file upload |
| N/A | `GET /api/books/{book_id}` | Get specific book |
| `normalize_books` | `POST /api/books/{book_id}/process` | Process uploaded book |

### Summary Services

| AWS Lambda | FastAPI Endpoint | Description |
|------------|------------------|-------------|
| `book_summary_lambda` | `POST /api/summaries/{book_id}/generate` | Generate AI summaries |
| `get_summary_by_progress` | `GET /api/summaries/{book_id}/by-progress` | Get summary by reading progress |
| N/A | `GET /api/summaries/{book_id}` | Get all summaries |
| N/A | `GET /api/summaries/{book_id}/search` | Search summaries |

### Character Services

| AWS Lambda | FastAPI Endpoint | Description |
|------------|------------------|-------------|
| `character_summary_lambda` | `POST /api/characters/{book_id}/generate` | Generate character lists |
| `get_character_by_progress` | `GET /api/characters/{book_id}` | Get characters by progress |
| N/A | `GET /api/characters/{book_id}/search` | Search characters |

### Reading State

| AWS Lambda | FastAPI Endpoint | Description |
|------------|------------------|-------------|
| N/A (DynamoDB direct) | `GET /api/reading-state/{book_id}` | Get reading state |
| N/A (DynamoDB direct) | `POST /api/reading-state/{book_id}` | Update reading state |
| N/A | `DELETE /api/reading-state/{book_id}` | Delete reading state |

## Database Migration

### From DynamoDB to PostgreSQL

The service migrates from AWS DynamoDB to PostgreSQL with the following table mappings:

#### Users Table
- **DynamoDB**: `users` table with `userId` as partition key
- **PostgreSQL**: `users` table with `id` as primary key
- **Changes**: Added `is_active`, `role`, timestamps

#### Books Table  
- **DynamoDB**: `user_books` table with `user_id` + `book_id` composite key
- **PostgreSQL**: `books` table with relationships
- **Changes**: Enhanced metadata, processing status tracking

#### Summaries Table
- **DynamoDB**: `summaries` table with `book_id` + `progress` composite key  
- **PostgreSQL**: `summaries` table with foreign keys
- **Changes**: Added user-specific summaries, better indexing

#### Characters Table
- **DynamoDB**: `characters` table with `book_id` + `progress` composite key
- **PostgreSQL**: `characters` table with enhanced structure
- **Changes**: Better character tracking, search capabilities

#### Reading States Table
- **DynamoDB**: Embedded in user/book records
- **PostgreSQL**: Dedicated `reading_states` table
- **Changes**: More detailed progress tracking

## Storage Migration

### From S3 to Local/Cloud Storage

- **AWS S3**: Used for book file storage with presigned URLs
- **FastAPI**: Local file storage with optional cloud integration
- **Changes**: Direct file uploads, better file management

## Search Migration

### From DynamoDB Queries to OpenSearch

- **DynamoDB**: Limited query capabilities, scan operations
- **OpenSearch**: Full-text search, advanced indexing
- **Changes**: Better search performance, relevance scoring

## Authentication Migration

### JWT Implementation

- **AWS**: Lambda authorizers, API Gateway integration
- **FastAPI**: JWT middleware, bearer token authentication
- **Changes**: Simplified auth flow, better token management

## Configuration Migration

### Environment Variables

| AWS Lambda Env | FastAPI Env | Description |
|----------------|-------------|-------------|
| `GEMINI_API_KEY` | `GEMINI_API_KEY` | Google Gemini API key |
| `DDB_SUMMARIES_TABLE` | `DATABASE_URL` | Database connection |
| `USER_BOOKS_TABLE_NAME` | `DATABASE_URL` | Database connection |
| `UPLOAD_BUCKET_NAME` | `UPLOAD_FOLDER` | File storage location |
| `JWT_SECRET` | `JWT_SECRET_KEY` | JWT signing key |

## Deployment Migration

### From AWS Lambda to Container/VPS

1. **AWS Lambda**: Serverless functions, API Gateway
2. **FastAPI**: Single application, container deployment
3. **Benefits**: 
   - Simpler architecture
   - Better development experience  
   - Cost-effective for consistent load
   - Easier debugging and monitoring

## Migration Steps

1. **Setup Environment**:
   ```bash
   cd /Users/srk/readrecall/readrecallsvc
   ./setup.sh
   ```

2. **Configure Database**:
   - Set up Neon PostgreSQL
   - Update `DATABASE_URL` in `.env`
   - Run migrations: `alembic upgrade head`

3. **Configure Services**:
   - Set up OpenSearch cluster
   - Get Gemini API key
   - Update environment variables

4. **Test Migration**:
   ```bash
   python test_setup.py
   python run_dev.py
   ```

5. **Deploy**:
   - Use Docker: `docker-compose up --build`
   - Or deploy to Railway/Render/VPS

## Benefits of Migration

1. **Simplified Architecture**: Single application vs. multiple Lambda functions
2. **Better Development Experience**: Local development, easier debugging
3. **Cost Optimization**: No Lambda cold starts, predictable pricing
4. **Enhanced Features**: Better search, more flexible APIs
5. **Open Source**: No vendor lock-in, community contributions
6. **Performance**: Faster response times, persistent connections

## Compatibility

The new FastAPI service maintains API compatibility with the existing frontend. Only the base URL needs to change:

- **Before**: `https://api-gateway-url/stage/`
- **After**: `https://your-fastapi-host/api/`

All request/response formats remain the same for seamless migration.
