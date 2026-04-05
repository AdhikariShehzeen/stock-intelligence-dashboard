# Stock Intelligence Dashboard

## Overview

This project is a mini financial data platform that collects, processes, and visualizes stock market data.

It demonstrates:

* Data collection using APIs
* Backend development with FastAPI
* Data visualization using Streamlit
* Docker-based deployment
* AWS ECS hosting

---

## Tech Stack

* Python
* FastAPI
* Streamlit
* SQLite
* Pandas, NumPy
* yfinance
* Docker
* AWS (ECR + ECS)
* GitHub Actions (CI/CD)

---

## Features

* Stock price visualization
* 52-week summary
* Compare two stocks
* Correlation analysis
* Simple price prediction
* Dockerized backend & frontend
* Deployed on AWS

---

##  Project Structure

```
backend/
frontend/
data/
Dockerfile.backend
Dockerfile.streamlit
.github/workflows/
```

---

##  API Endpoints

* `/companies` → list of stocks
* `/data/{symbol}` → last 30 days data
* `/summary/{symbol}` → 52-week stats
* `/compare` → compare stocks
* `/correlation` → correlation value
* `/predict/{symbol}` → price prediction

---

## Live Deployment

Frontend:

```
http://3.104.110.81:8501/
```

Backend:

```
http://54.206.106.216:8000/
```

Swagger Docs:

```
http://54.206.106.216:8000/docs
```

> Note: Public IPs may change after redeployment.

---

## Docker

### Backend

```bash
docker build -f Dockerfile.backend .
```

### Frontend

```bash
docker build -f Dockerfile.streamlit .
```

---

## CI/CD

* GitHub Actions builds Docker images
* Pushes to AWS ECR
* ECS runs containers

---

## Data Source

* Yahoo Finance (yfinance)

---

## Limitations

* Uses SQLite (not scalable)
* Public IP instead of domain
* Basic prediction model

---

## Future Improvements

* PostgreSQL / Cloud DB
* Authentication
* Advanced ML models
* Load balancer + domain

---


