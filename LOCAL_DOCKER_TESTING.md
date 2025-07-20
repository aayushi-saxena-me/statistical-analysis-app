# 🧪 Local Docker Testing Guide

Test your Docker setup locally before deploying to AWS.

## 🚀 **Quick Start**

### **Option 1: Simple Docker Run (SQLite)**

```bash
# Build the image
docker build -t statistical-analysis .

# Run with SQLite (for quick testing)
docker run -p 8000:8000 -e DEBUG=True statistical-analysis

# Visit: http://localhost:8000
```

### **Option 2: Full Stack with PostgreSQL**

```bash
# Start all services (Django + PostgreSQL + Redis)
docker-compose up

# Visit: http://localhost:8000
```

## 🔧 **Testing Checklist**

- [ ] **App loads** at http://localhost:8000
- [ ] **Health check** works: http://localhost:8000/health/
- [ ] **File upload** functionality works
- [ ] **Statistical analysis** tab functions
- [ ] **SVM training** works (if enabled)
- [ ] **Admin panel** accessible: http://localhost:8000/admin/

## 🛠 **Useful Commands**

```bash
# View running containers
docker ps

# View logs
docker-compose logs web

# Access container shell
docker-compose exec web bash

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Stop all services
docker-compose down

# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## 🐛 **Troubleshooting**

### **Port already in use:**
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### **Database issues:**
```bash
# Reset database
docker-compose down -v
docker-compose up
```

### **Permission errors:**
```bash
# Fix file permissions (Linux/Mac)
sudo chown -R $USER:$USER .
```

## ✅ **Success Indicators**

When everything works locally:
- App loads without errors
- Health check returns `{"status": "healthy"}`
- Database operations work
- File uploads are successful
- No error logs in `docker-compose logs`

You're ready to deploy to AWS! 🎉 