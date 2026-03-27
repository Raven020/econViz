# EconViz

Economic indicator dashboard using Hidden Markov Models to predict market regime. Click on any asset to see a Monte Carlo simulation that predicts likely price outcomes over the next 30 days.

**Live:** [econviz.tech](https://econviz.tech)

## Architecture

- **Python FastAPI** — analytical backend (HMM regime detection, Monte Carlo simulation, data fetching)
- **C# ASP.NET Core** — API gateway (caching, request aggregation, SignalR real-time push)
- **Next.js + MUI** — frontend dashboard

## Running locally

```bash
# Backend (port 8000)
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m backend.main

# Gateway (port 5000)
cd gateway/EconViz.Gateway && dotnet run

# Frontend (port 3000)
cd frontend && npm install && npm run dev
```
