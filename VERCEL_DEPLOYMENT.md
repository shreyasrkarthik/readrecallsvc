# Deploying ReadRecall to Vercel

This guide will walk you through deploying your FastAPI application to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install the Vercel CLI globally
   ```bash
   npm i -g vercel
   ```
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Important Considerations

### ⚠️ Limitations of Vercel for FastAPI

Vercel has some limitations that may affect your application:

1. **Serverless Functions**: Vercel runs your app as serverless functions with:
   - Maximum execution time: 30 seconds (configurable up to 900 seconds for Pro plans)
   - Cold starts for each function invocation
   - No persistent file system (uploads won't work as-is)

2. **Database Connections**: 
   - Each function invocation creates new database connections
   - Connection pooling may not work as expected
   - Consider using connection pooling services or connection management

3. **File Storage**: 
   - Vercel doesn't provide persistent file storage
   - You'll need to use external services like AWS S3, Cloudinary, or similar

## Deployment Steps

### Step 1: Prepare Your Environment Variables

Create a `.env.production` file with your production values:

```bash
# App Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database (use production database URL)
DATABASE_URL=your_production_database_url

# Security
SECRET_KEY=your_production_secret_key
JWT_SECRET_KEY=your_production_jwt_secret

# OpenSearch
OPENSEARCH_HOST=your_production_opensearch_host
OPENSEARCH_USER=your_production_opensearch_user
OPENSEARCH_PASSWORD=your_production_opensearch_password

# AI Services
GEMINI_API_KEY=your_production_gemini_api_key

# CORS (update with your production domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# File Storage (use external service)
UPLOAD_FOLDER=s3://your-bucket/uploads
```

### Step 2: Set Up External Services

#### Database
- Use a managed PostgreSQL service (Neon, Supabase, AWS RDS, etc.)
- Ensure your database is accessible from Vercel's servers

#### File Storage
- Set up AWS S3, Cloudinary, or similar service
- Update your file upload logic to use external storage

#### OpenSearch
- Use a managed OpenSearch service (AWS OpenSearch, Elastic Cloud, etc.)
- Ensure it's accessible from Vercel's servers

### Step 3: Deploy to Vercel

#### Option A: Using Vercel CLI

1. **Login to Vercel**:
   ```bash
   vercel login
   ```

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Follow the prompts**:
   - Link to existing project or create new
   - Set project name
   - Set root directory (current directory)
   - Override settings if needed

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your Git repository
4. Configure build settings:
   - Framework Preset: Other
   - Build Command: Leave empty
   - Output Directory: Leave empty
   - Install Command: `pip install -r requirements-vercel.txt`

### Step 4: Configure Environment Variables

In your Vercel project dashboard:

1. Go to Settings → Environment Variables
2. Add all your environment variables from `.env.production`
3. Set them for Production environment

### Step 5: Update CORS Settings

Update your CORS origins to include your Vercel domain:
```bash
CORS_ORIGINS=https://yourproject.vercel.app,https://yourdomain.com
```

## Post-Deployment

### Test Your API

1. **Health Check**: Visit `https://yourproject.vercel.app/health`
2. **API Documentation**: Visit `https://yourproject.vercel.app/docs` (if enabled)
3. **Test Endpoints**: Use tools like Postman or curl to test your API endpoints

### Monitor Performance

- Check Vercel Analytics for function execution times
- Monitor database connection performance
- Watch for cold start delays

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are in `requirements-vercel.txt`
2. **Database Connection**: Check if your database allows connections from Vercel's IP ranges
3. **Environment Variables**: Verify all required env vars are set in Vercel dashboard
4. **Function Timeout**: Increase `maxDuration` in `vercel.json` if needed

### Debugging

1. **Check Vercel Function Logs**: View logs in the Vercel dashboard
2. **Local Testing**: Test with `vercel dev` to simulate the production environment
3. **Environment Variables**: Use `vercel env ls` to verify environment variables

## Production Considerations

### Performance Optimization

1. **Database Connections**: Implement connection pooling or use connection management
2. **Caching**: Add Redis or similar for caching frequently accessed data
3. **CDN**: Use Vercel's Edge Network for static assets

### Security

1. **HTTPS**: Vercel provides automatic HTTPS
2. **Rate Limiting**: Implement rate limiting for your API endpoints
3. **CORS**: Restrict CORS origins to only necessary domains

### Monitoring

1. **Logging**: Use Vercel's built-in logging or integrate with external services
2. **Metrics**: Monitor function execution times and errors
3. **Alerts**: Set up alerts for function failures or timeouts

## Alternative Deployment Options

If Vercel's limitations are too restrictive, consider:

1. **Railway**: Better for Python applications with persistent storage
2. **Render**: Good for Python apps with database support
3. **Heroku**: Traditional hosting with more control
4. **AWS/GCP**: Full control but more complex setup

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
