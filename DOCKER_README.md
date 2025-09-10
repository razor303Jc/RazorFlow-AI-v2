# RazorFlow AI Docker Deployment Guide

🚀 **Complete containerized deployment of RazorFlow AI with monitoring and debugging**

## Overview

This Docker setup provides a complete, production-ready deployment of RazorFlow AI with:

- **Backend**: FastAPI with comprehensive logging and error handling
- **Frontend**: React with Nginx reverse proxy
- **Database**: PostgreSQL 15 with optimized configuration
- **Cache**: Redis with persistence
- **Vector DB**: ChromaDB for AI embeddings
- **Monitoring**: Health checks and logging aggregation
- **Debugging**: Enhanced debugging tools in all containers

## Quick Start

### 1. Prerequisites

- Docker Engine (tested with 24.0+)
- Docker Compose (v2.0+)
- 4GB+ RAM available
- 10GB+ disk space

### 2. Initial Setup

```bash
# Clone and navigate to project
cd /home/jc/Documents/RazorFlow-AI-v2

# Copy environment template
cp .env.example .env

# Edit environment variables if needed
vim .env

# Make script executable
chmod +x razorflow-docker.sh
```

### 3. Start Services

```bash
# Start all services with health monitoring
./razorflow-docker.sh start

# Or manually with docker-compose
docker-compose up -d
```

### 4. Verify Deployment

The script will automatically perform health checks. You can also check manually:

```bash
# Check service status
./razorflow-docker.sh status

# Check health
./razorflow-docker.sh health

# View logs
./razorflow-docker.sh logs
```

## Service URLs

Once running, access services at:

| Service    | URL                        | Description                   |
| ---------- | -------------------------- | ----------------------------- |
| Frontend   | http://localhost:3000      | React UI                      |
| Backend    | http://localhost:8000      | FastAPI application           |
| API Docs   | http://localhost:8000/docs | Interactive API documentation |
| ChromaDB   | http://localhost:8001      | Vector database API           |
| PostgreSQL | localhost:5434             | Database (external access)    |
| Redis      | localhost:6379             | Cache (external access)       |

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   PostgreSQL    │
│   (React +      │◄──►│   (FastAPI)     │◄──►│   Database      │
│    Nginx)       │    │                 │    │                 │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5434    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │     Redis       │    │    ChromaDB     │
                    │     Cache       │    │  Vector Store   │
                    │   Port: 6379    │    │   Port: 8001    │
                    └─────────────────┘    └─────────────────┘
```

## Management Commands

### Service Management

```bash
# Start all services
./razorflow-docker.sh start

# Stop all services
./razorflow-docker.sh stop

# Restart services
./razorflow-docker.sh restart

# Rebuild and restart
./razorflow-docker.sh rebuild
```

### Monitoring & Debugging

```bash
# Check service status
./razorflow-docker.sh status

# Health checks
./razorflow-docker.sh health

# View logs (all services)
./razorflow-docker.sh logs

# View logs (specific service)
./razorflow-docker.sh logs backend
./razorflow-docker.sh logs frontend
./razorflow-docker.sh logs postgres
```

### Cleanup

```bash
# Stop services and cleanup
./razorflow-docker.sh cleanup

# Manual cleanup
docker-compose down -v
docker system prune -f
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Application
DEBUG=true
ENVIRONMENT=development

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000
POSTGRES_PORT=5434

# Database
POSTGRES_DB=razorflow_ai
POSTGRES_USER=razorflow
POSTGRES_PASSWORD=razorflow_secret_2025

# API URLs
VITE_API_BASE=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=detailed
```

### Database Configuration

The PostgreSQL container includes:

- Optimized configuration for performance
- Comprehensive logging
- Health checks
- Automatic schema initialization
- Sample data for testing

### Logging & Monitoring

All services include:

- **Structured logging** with JSON format
- **Log rotation** to prevent disk space issues
- **Health checks** with automatic recovery
- **Performance monitoring** with custom metrics
- **Error tracking** with detailed stack traces

## Debugging

### Container Debugging

Each container includes debugging tools:

```bash
# Access backend container
docker exec -it razorflow-backend bash

# Access database
docker exec -it razorflow-postgres psql -U razorflow -d razorflow_ai

# Access Redis
docker exec -it razorflow-redis redis-cli

# Check ChromaDB
curl http://localhost:8001/api/v1/heartbeat
```

### Log Analysis

```bash
# Real-time logs
./razorflow-docker.sh logs backend

# Error logs only
docker logs razorflow-backend 2>&1 | grep ERROR

# Database logs
docker logs razorflow-postgres | grep ERROR
```

### Common Issues

#### Services Not Starting

1. **Check Docker status**: `docker info`
2. **Check ports**: `netstat -tlnp | grep :8000`
3. **Check logs**: `./razorflow-docker.sh logs`
4. **Check resources**: `docker stats`

#### Database Connection Issues

1. **Check PostgreSQL health**: `docker exec razorflow-postgres pg_isready`
2. **Check credentials**: Verify `.env` database settings
3. **Check network**: `docker network ls`

#### Frontend Blank Page

1. **Check backend connection**: `curl http://localhost:8000/health`
2. **Check API URL**: Verify `VITE_API_BASE` in `.env`
3. **Check CORS**: Verify `CORS_ORIGINS` includes frontend URL

## Production Deployment

### Security Considerations

1. **Change default passwords** in `.env`
2. **Use secrets management** for sensitive data
3. **Enable HTTPS** with SSL certificates
4. **Configure firewall** rules
5. **Regular security updates**

### Performance Optimization

1. **Resource limits**: Configure Docker resource constraints
2. **Database tuning**: Adjust PostgreSQL configuration
3. **Caching**: Optimize Redis cache settings
4. **Monitoring**: Set up external monitoring (Prometheus/Grafana)

### Backup Strategy

```bash
# Database backup
docker exec razorflow-postgres pg_dump -U razorflow razorflow_ai > backup_$(date +%Y%m%d).sql

# Volume backup
docker run --rm -v razorflow-ai-v2_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## Troubleshooting

### Health Check Failures

If health checks fail:

1. Check service logs: `./razorflow-docker.sh logs [service]`
2. Verify network connectivity between services
3. Check resource usage: `docker stats`
4. Restart problematic service: `docker-compose restart [service]`

### Performance Issues

1. **Check resources**: `docker stats`
2. **Monitor logs**: Look for error patterns
3. **Database performance**: Check PostgreSQL slow query logs
4. **Network issues**: Verify inter-service communication

### Data Issues

1. **Database connection**: Verify credentials and network
2. **Migration issues**: Check database initialization logs
3. **Data corruption**: Restore from backup if needed

## Development

### Local Development Setup

For development with hot reload:

```bash
# Start only infrastructure services
docker-compose up postgres redis chromadb -d

# Run backend locally
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Run frontend locally
cd frontend
npm install
npm run dev
```

### Testing

```bash
# Run backend tests
docker exec razorflow-backend python -m pytest

# Run frontend tests
docker exec razorflow-frontend npm test

# Integration tests
curl -f http://localhost:8000/health
curl -f http://localhost:3000/health
```

## Support

For issues and questions:

1. Check logs: `./razorflow-docker.sh logs`
2. Verify health: `./razorflow-docker.sh health`
3. Review configuration in `.env`
4. Check resource usage: `docker stats`

## License

RazorFlow AI - Proprietary Software
