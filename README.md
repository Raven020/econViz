# EconViz

Economic indicator dashboard using Hidden Markov Models to predict market regime. Click on any asset to see a Monte Carlo simulation that predicts likely price outcomes over the next 30 days.

**Live:** [econviz.tech](https://econviz.tech)

## Architecture

- **Python FastAPI** — analytical backend (HMM regime detection, Monte Carlo simulation, data fetching)
- **C# ASP.NET Core** — API gateway (caching, request aggregation, SignalR real-time push)
- **Next.js + MUI** — frontend dashboard