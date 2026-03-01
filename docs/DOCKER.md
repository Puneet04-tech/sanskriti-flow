# Docker Deployment Guide

## Quick Start

### Start all services:
```bash
docker-compose up -d
```

### Stop all services:
```bash
docker-compose down
```

## Individual Services

### Backend Only:
```bash
docker-compose up -d backend
```

### Worker Only:
```bash
docker-compose up -d worker
```

### Frontend Only:
```bash
docker-compose up -d frontend
```

## Accessing Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redis**: localhost:6379

## GPU Support

To enable GPU support for faster processing:

1. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

2. Modify `docker-compose.yml` for backend and worker services:
```yaml
backend:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  environment:
    - USE_GPU=true
```

## Volume Management

### Backup data:
```bash
docker-compose exec backend tar czf /tmp/backup.tar.gz /app/data
docker cp sanskriti-flow-backend-1:/tmp/backup.tar.gz ./backup.tar.gz
```

### Clear cache:
```bash
docker-compose exec backend rm -rf /app/data/cache/*
```

## Logs

### View all logs:
```bash
docker-compose logs -f
```

### View specific service logs:
```bash
docker-compose logs -f backend
docker-compose logs -f worker
```

## Troubleshooting

### Rebuild services:
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Check service health:
```bash
docker-compose ps
docker-compose exec backend curl http://localhost:8000/health
```

### Reset everything:
```bash
docker-compose down -v
docker-compose up -d
```
