# Statistical Analysis Application

A Django-based web application for statistical analysis with machine learning capabilities.

## Features

- File upload and data processing (CSV, Excel)
- Statistical analysis and visualization
- Machine learning with SVM
- Interactive dashboard with Plotly charts
- Docker deployment ready

## Prerequisites

- Python 3.12+
- Django 4.2+
- Docker (for deployment)
- PostgreSQL (for production)

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Docker Deployment

### Local Testing
```bash
docker build -t statistical-analysis .
docker run -p 8000:8000 statistical-analysis
```

### Full Stack with PostgreSQL
```bash
docker-compose up
```

## AWS Deployment

This application is configured for AWS deployment using:
- **AWS App Runner** (recommended)
- **ECS with Fargate** (advanced)

See `DOCKER_DEPLOYMENT_GUIDE.md` for detailed deployment instructions.

## Project Structure
```
statistical_analysis/
├── analysis/                # Main Django app
├── statistical_analysis/    # Django project settings
├── templates/              # HTML templates
├── static/                 # Static files
├── media/                  # Uploaded files
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Local development
├── apprunner.yaml          # AWS App Runner config
└── requirements.txt        # Python dependencies
```
