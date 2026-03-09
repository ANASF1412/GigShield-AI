# GigShield AI  
### Parametric Income Protection for Delivery Workers

GigShield AI is an **AI-powered parametric insurance platform** designed to protect gig economy delivery workers from **income loss caused by environmental disruptions** such as heavy rain, heatwaves, floods, pollution, and curfews.

Instead of requiring manual claim filing, GigShield AI **automatically detects disruptions, estimates lost income, and triggers instant payouts**.

The system combines **AI prediction, parametric triggers, fraud detection, and automated payouts** to provide financial security for delivery workers.

---

# Problem Statement

Delivery workers depend heavily on outdoor conditions. Extreme weather or environmental disruptions can stop deliveries completely, causing sudden income loss.

Common disruptions include:

- Heavy rainfall
- Heatwaves
- Flooding
- Severe air pollution
- Government curfews

Traditional insurance systems require **manual claim filing, verification, and long processing times**.

GigShield AI solves this using **parametric insurance and AI automation**.

---

# Solution Overview

GigShield AI automatically:

1. Predicts disruption risk using AI
2. Detects environmental disruption events
3. Calculates lost delivery income
4. Verifies claim authenticity
5. Triggers automatic payouts

Workers do not need to submit claims manually.

---

# Target Users

Food delivery workers operating on platforms such as:

- Swiggy
- Zomato

Why delivery workers?

- Outdoor dependent
- High delivery frequency
- Weather sensitive
- Predictable earning patterns

---

# Example Scenario

A delivery worker normally earns **₹120 per hour**.

Heavy rain occurs in their delivery zone.

Rainfall detected:

70mm

Parametric trigger condition:

Rainfall > 50mm

Delivery disruption lasts **5 hours**.

Income loss:

5 × ₹120 = ₹600

GigShield AI automatically triggers:

Payout = ₹600


Worker receives instant compensation.

---

# Key Features

- Parametric insurance model
- AI disruption prediction
- Automatic payout system
- Fraud detection engine
- Hyperlocal risk scoring
- Delivery income loss estimation
- Real-time monitoring dashboard

---

# System Architecture

            Worker App / Dashboard
                    │
                    │ API Requests
                    │
            Backend Server (FastAPI)
                    │
    ┌───────────────┼────────────────┐
    │               │                │

AI Risk Engine   Parametric Engine   Fraud Detection

    │               │                │
    └───────────────┬────────────────┘
                    │
            Data Processing Layer
    Weather API | Pollution API | Delivery Logs
                    │
                    ▼
               Database
               (SQLite)

                    │
                    ▼
            Payout Engine
         Mock UPI / Razorpay


---

# Workflow

The system follows this pipeline:

Environmental Data
│
▼
Weather + Pollution Dataset
│
▼
AI Risk Prediction Model
│
▼
Disruption Trigger Detection
│
▼
Income Loss Estimation
│
▼
Fraud Detection
│
▼
Automatic Payout
│
▼
Worker Dashboard Notification


---

# AI Components

## 1 Risk Prediction Model

Predicts probability of delivery disruption.

Inputs:

- Rainfall probability
- Temperature
- Pollution levels
- Weather forecast

Output:

Disruption risk score (0–100).

Example:

Disruption Risk Tomorrow = 65%


---

## 2 Parametric Trigger Engine

Detects disruption events automatically.

Triggers include:

| Event | Trigger Condition |
|------|-------------------|
| Heavy Rain | Rainfall > 50mm |
| Heatwave | Temperature > 42°C |
| Pollution | AQI > 300 |
| Flood | Flood alert issued |
| Curfew | Government notification |

When a trigger occurs:

Disruption Event Detected
↓
Calculate Lost Delivery Hours
↓
Trigger Payout


---

## 3 Income Loss Estimator

Calculates lost income using delivery history.

Inputs:

- Average hourly earnings
- Delivery activity logs
- Disruption duration

Example:

Hourly earning = ₹120
Disruption = 4 hours

Loss = ₹480


---

## 4 Fraud Detection Model

Detects suspicious claims.

Checks:

- Worker GPS location
- Weather data
- Delivery logs
- Historical claims

Model:

Isolation Forest anomaly detection.

Example fraud case:

Worker claims rain disruption but weather API reports no rainfall.

System flags claim.

---

## 5 Hyperlocal Risk Scoring

Each delivery zone has a risk score.

Inputs:

- Historical weather
- Flood zones
- Pollution levels
- Traffic congestion

Output:

Zone Risk Score = 0.72


Higher risk zones require higher premiums.

---

# Hugging Face Models Used

The system integrates models from the Hugging Face ecosystem.

Text classification:

- distilbert-base-uncased

Used to classify alerts and disruption events.

Zero-shot classification:

- facebook/bart-large-mnli

Used to detect event types:

- rain
- flood
- pollution
- curfew
- heatwave

Time-series forecasting:

- huggingface/time-series-transformer

Used to predict disruption probability.

---

# Hugging Face Datasets

Datasets loaded using:

from datasets import load_dataset


Example datasets used:

- climate datasets
- weather datasets
- environmental event datasets

These datasets simulate environmental disruption signals.

---

# Technology Stack

Frontend Dashboard

- Streamlit

Backend

- FastAPI

Programming Language

- Python

Machine Learning

- Scikit-learn
- Hugging Face Transformers

Dataset Management

- Hugging Face Datasets

Database

- SQLite

Visualization

- Plotly

APIs

- Weather API
- AQI API

---

# Project Structure

gigshield-ai/

app.py

data_loader.py

risk_model.py

trigger_engine.py

income_estimator.py

fraud_detector.py

payout_engine.py

dashboard.py

requirements.txt

README.md


---

# Dashboard Features

The Streamlit dashboard shows:

- Worker profile
- Weather conditions
- Disruption risk score
- Risk forecast chart
- Zone risk heatmap
- Income loss estimation
- Triggered payouts

---

# Installation

Clone the repository.

git clone https://github.com/ANASF1412/GigShield-AI.git
cd GigShield-AI


Install dependencies.

pip install -r requirements.txt


---

# Run the Prototype

Start the Streamlit dashboard.

streamlit run app.py


Open browser:

http://localhost:8501


---

# Example Output

Disruption Alert Detected

Event: Heavy Rain
Rainfall: 72mm

Delivery Disruption Duration: 4 hours

Estimated Income Loss: ₹480

Payout Triggered: ₹480


---

# Future Improvements

Potential upgrades:

- Real delivery data integration
- GPS tracking
- Mobile app for workers
- Blockchain claim transparency
- Dynamic insurance marketplace
- Multi-city deployment

---

# Impact

GigShield AI supports the gig economy by providing:

- Financial stability for delivery workers
- Faster insurance payouts
- Transparent claim processing
- AI-driven risk prediction

This system demonstrates how **AI and parametric insurance can transform financial protection for gig workers**.

---

# License

MIT License
