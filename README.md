# SIT753 Task 7.3HD — DevOps Pipeline with Jenkins

**Student:** Talha Azeez Mohammed  
**Unit:** SIT753 Professional Practice in IT  
**Task:** 7.3HD — DevOps Pipeline with Jenkins  
**Stages Implemented:** 7 (Build, Test, Code Quality, Security, Deploy, Release, Monitoring)

---

## Project Overview

A Flask-based Movie Database CRUD application used as the target project for a full 7-stage Jenkins DevOps pipeline. The application allows users to create, read, update, and delete movie entries (title, year, rating) and is served via server-rendered Jinja2 templates backed by SQLite.

The focus of this submission is the CI/CD pipeline rather than the application itself — the pipeline automates building, testing, quality analysis, security scanning, deployment, release, and monitoring using industry-standard tools.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Application | Python 3.11, Flask 3.0.3, Flask-SQLAlchemy |
| Containerisation | Docker |
| CI/CD | Jenkins (Docker) |
| Testing | pytest, pytest-cov |
| Code Quality | SonarQube Community Edition |
| Security | Bandit, pip-audit |
| Monitoring | Prometheus, Grafana, prometheus-flask-exporter |
| Source Control | Git, GitHub |

---

## Pipeline Stages

| # | Stage | Tool | Description |
|---|---|---|---|
| 1 | Build | Docker | Builds a versioned Docker image tagged with the Jenkins build number |
| 2 | Test | pytest | Runs unit and integration tests, publishes JUnit XML to Jenkins |
| 3 | Code Quality | SonarQube | Static analysis for code smells, bugs, and coverage |
| 4 | Security | Bandit + pip-audit | Source code and dependency vulnerability scanning |
| 5 | Deploy | Docker | Deploys to staging environment on port 5001 with health check |
| 6 | Release | Docker | Manual approval gate, then promotes to production on port 5000 |
| 7 | Monitoring | Prometheus + Grafana | Live metrics dashboard and alert rule for production app |

---

## Repository Structure

```
sit753-8hd-jenkins-pipeline/
├── Dockerfile                  # Container definition for the app
├── Jenkinsfile                 # Full 7-stage pipeline definition
├── movie.py                    # Flask application
├── requirements.txt            # Python dependencies
├── sonar-project.properties    # SonarQube scanner configuration
├── prometheus.yml              # Prometheus scrape configuration
├── .dockerignore
├── templates/
│   └── index.html              # Jinja2 template
├── static/
│   └── css/
└── tests/
    ├── __init__.py
    └── test_app.py             # pytest test suite
```

---

## How to Run Locally

### Prerequisites
- Docker Desktop installed and running
- Git

### 1. Clone the repository

```bash
git clone https://github.com/tazeezx/sit753-8hd-jenkins-pipeline.git
cd sit753-8hd-jenkins-pipeline
```

### 2. Build and run the app

```bash
docker build -t movie-app:latest .
docker run -d -p 5000:5000 --name movie-app movie-app:latest
```

Visit `http://localhost:5000`

### 3. Set up the full pipeline

Start required infrastructure:

```bash
docker network create jenkins-net

docker run -d --name jenkins --network jenkins-net \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -u root jenkins/jenkins:latest-jdk17

docker run -d --name sonarqube --network jenkins-net \
  -p 9000:9000 sonarqube:community

docker run -d --name prometheus --network jenkins-net \
  -p 9090:9090 \
  -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

docker run -d --name grafana --network jenkins-net \
  -p 3000:3000 grafana/grafana
```

Then:
- Jenkins: `http://localhost:8080`
- SonarQube: `http://localhost:9000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Create a Pipeline job in Jenkins pointing to this repository with `Jenkinsfile` as the script path.

---

## Endpoints

| Endpoint | Description |
|---|---|
| `http://localhost:5000` | Production app |
| `http://localhost:5001` | Staging app |
| `http://localhost:5000/health` | Health check — returns `{"status": "ok"}` |
| `http://localhost:5000/metrics` | Prometheus metrics |

---
