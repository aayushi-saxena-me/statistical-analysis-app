# 🐳 Docker Deployment Guide for AWS

This guide will help you deploy your Django Statistical Analysis app using Docker on AWS App Runner.

## 📋 **Prerequisites**

✅ **AWS Account** with appropriate permissions  
✅ **Docker installed locally** (for testing)  
✅ **Git repository** (GitHub recommended)  
✅ **AWS CLI configured** (optional but helpful)  

## 🚀 **Deployment Options**

### **Option 1: AWS App Runner (Recommended)**
- ✅ Simplest setup - like Heroku
- ✅ Auto-scaling and load balancing
- ✅ Built-in CI/CD from GitHub
- ✅ Managed SSL certificates
- ✅ No infrastructure management

### **Option 2: ECS with Fargate**
- ✅ More control and customization
- ✅ Better for complex architectures
- ⚠️ More configuration required

---

## 🎯 **Option 1: AWS App Runner Deployment**

### **Step 1: Test Docker Locally (Optional)**

```bash
# Build and test the Docker image
docker build -t statistical-analysis .
docker run -p 8000:8000 -e DEBUG=True statistical-analysis

# Test with docker-compose (includes database)
docker-compose up
```

Visit `http://localhost:8000` to test your app.

### **Step 2: Push Code to GitHub**

1. **Create a new GitHub repository**
2. **Push your code:**
   ```bash
   git add .
   git commit -m "Add Docker configuration"
   git push origin main
   ```

### **Step 3: Create RDS Database**

1. **Go to AWS RDS Console**
2. **Create Database:**
   - Engine: PostgreSQL 15
   - Template: Free tier (or Production)
   - DB instance identifier: `statistical-analysis-db`
   - Master username: `postgres`
   - Master password: `your-secure-password`
   - VPC: Default VPC
   - Public access: **Yes** (for App Runner)
   - Security group: Create new (allow port 5432)

3. **Note the endpoint** (will look like: `statistical-analysis-db.xxx.rds.amazonaws.com`)

### **Step 4: Create App Runner Service**

1. **Go to AWS App Runner Console**
2. **Click "Create service"**
3. **Configure source:**
   - Repository type: **Source code repository**
   - Provider: **GitHub**
   - Connect to GitHub and select your repository
   - Branch: **main**
   - Deployment trigger: **Automatic**

4. **Configure build:**
   - Configuration file: **Use configuration file** 
   - Configuration file: `apprunner.yaml`

5. **Configure service:**
   - Service name: `statistical-analysis-app`
   - Virtual CPU: **1 vCPU**
   - Memory: **2 GB**

6. **Environment variables:**
   ```
   DATABASE_URL=postgresql://postgres:your-password@your-rds-endpoint:5432/postgres
   SECRET_KEY=your-super-secret-key-here
   DEBUG=False
   AWS_DEFAULT_REGION=us-east-1
   ```

7. **Health check:**
   - Path: `/health/`
   - Interval: 10 seconds
   - Timeout: 5 seconds
   - Healthy threshold: 2
   - Unhealthy threshold: 5

8. **Review and Create**

### **Step 5: Configure Database Security**

1. **Go to RDS → Databases → Your DB**
2. **Click on VPC security groups**
3. **Edit inbound rules:**
   - Add rule: PostgreSQL, Port 5432, Source: App Runner VPC
   - Or temporarily: Anywhere (0.0.0.0/0) for testing

### **Step 6: Run Database Migrations**

After deployment, run migrations:

1. **App Runner Console → Your Service → Logs**
2. **Or connect via App Runner Actions** (if available)
3. **Run:** `python manage.py migrate`

---

## 🎯 **Option 2: ECS with Fargate Deployment**

### **Step 1: Push to ECR**

```bash
# Create ECR repository
aws ecr create-repository --repository-name statistical-analysis

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t statistical-analysis .
docker tag statistical-analysis:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/statistical-analysis:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/statistical-analysis:latest
```

### **Step 2: Create ECS Cluster**

1. **ECS Console → Clusters → Create**
2. **Cluster name:** `statistical-analysis-cluster`
3. **Infrastructure:** AWS Fargate (serverless)

### **Step 3: Create Task Definition**

1. **Task definitions → Create new**
2. **Family:** `statistical-analysis-task`
3. **Launch type:** Fargate
4. **CPU:** 1 vCPU, Memory: 2GB
5. **Container definition:**
   - Name: `web`
   - Image: Your ECR image URI
   - Port: 8000
   - Environment variables (same as App Runner)

### **Step 4: Create Service**

1. **Cluster → Create Service**
2. **Task definition:** Your task definition
3. **Service name:** `statistical-analysis-service`
4. **Desired tasks:** 2
5. **Load balancer:** Application Load Balancer
6. **Target group:** Create new, health check `/health/`

---

## 🔧 **Environment Variables Reference**

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Yes | Django secret key | Random 50-character string |
| `DEBUG` | No | Enable debug mode | `False` (production) |
| `AWS_STORAGE_BUCKET_NAME` | No | S3 bucket for static files | `my-app-static-files` |
| `AWS_ACCESS_KEY_ID` | No | AWS access key | From IAM user |
| `AWS_SECRET_ACCESS_KEY` | No | AWS secret key | From IAM user |
| `AWS_DEFAULT_REGION` | No | AWS region | `us-east-1` |

---

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **Health check failing:**
   - Check `/health/` endpoint returns 200
   - Verify app is listening on correct port
   - Check logs for startup errors

2. **Database connection errors:**
   - Verify RDS security group allows connections
   - Check DATABASE_URL format
   - Ensure RDS is publicly accessible

3. **Static files not loading:**
   - Set up S3 bucket and configure environment variables
   - Or use WhiteNoise for simple static file serving

4. **Build failures:**
   - Check Dockerfile syntax
   - Verify requirements.txt is complete
   - Check resource limits (memory/CPU)

### **Useful Commands:**

```bash
# View App Runner logs
aws apprunner describe-service --service-arn your-service-arn

# Check ECS service status
aws ecs describe-services --cluster your-cluster --services your-service

# Connect to running container (ECS)
aws ecs execute-command --cluster your-cluster --task your-task-id --container web --interactive --command "/bin/bash"
```

---

## 🎉 **Post-Deployment Checklist**

- [ ] App loads successfully
- [ ] Health check endpoint responds
- [ ] Database connection works
- [ ] File uploads work
- [ ] SVM training functions correctly
- [ ] Static files load properly
- [ ] SSL certificate is working
- [ ] Monitoring and logging configured

---

## 📊 **Costs (Approximate)**

### **App Runner:**
- Service: ~$25-50/month (1 vCPU, 2GB RAM)
- RDS: ~$20-40/month (t3.micro PostgreSQL)
- Data transfer: ~$5-10/month

### **ECS Fargate:**
- Tasks: ~$20-40/month (2 tasks, 1 vCPU, 2GB RAM)
- Load Balancer: ~$20/month
- RDS: ~$20-40/month

**Total estimated cost: $45-100/month**

---

## 🆘 **Need Help?**

If you encounter issues:

1. **Check service logs** in AWS Console
2. **Verify environment variables** are set correctly
3. **Test health check endpoint** manually
4. **Check security group configurations**
5. **Review this guide step-by-step**

Happy deploying! 🚀 