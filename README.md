# PharmaPulse Forecast Dashboard

PharmaPulse is a Flask + Plotly single-page forecasting dashboard for total and category demand planning.

## What This Version Delivers

- Single-page dashboard UX for desktop, tablet, and mobile.
- Total vs Category toggle.
- Category selector + forecast horizon slider.
- KPI cards including dynamic accuracy display.
- Dark mode toggle with persisted preference.
- Deployment-ready WSGI, Docker, Render, and Railway config.

## Project Entry Points

- Website app: app.py
- WSGI module: wsgi.py
- Main template: templates/index.html
- Main styles: static/main.css
- Frontend behavior: static/app.js

## Required Forecast Artifacts

The website expects these generated CSV files in data/processed:

- global_predictions.csv
- model_comparison.csv
- future_weekly_predictions.csv
- future_month_forecast.csv

Generate them via your existing training and comparison scripts before launching the site.

## Local Run

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements-web.txt
```

3. Start app:

```bash
python app.py
```

4. Open:

http://127.0.0.1:8501/

## Permanent Public URL (Laptop Independent)

To get a URL that works even when your laptop is off, deploy to a cloud host.

### Option A: Render (recommended fastest)

1. Push this project to a GitHub repository.
2. Open Render Dashboard and click New + > Blueprint.
3. Select your repository.
4. Render will auto-detect render.yaml and deploy.
5. Your permanent URL will be like:
	https://pharmapulse-forecast.onrender.com

Configured file:
- render.yaml

### Option B: Railway

1. Push this project to GitHub.
2. In Railway, click New Project > Deploy from GitHub Repo.
3. Select this repository.
4. Railway builds using requirements-web.txt and starts with Procfile or wsgi command.
5. You get a public railway.app URL.

Configured file:
- railway.json

## Production Deploy Commands

### Option A: Gunicorn (Linux container or VM)

```bash
gunicorn -w 2 -k gthread -b 0.0.0.0:8501 wsgi:app
```

### Option B: Docker

```bash
docker build -t pharmapulse .
docker run -p 8501:8501 pharmapulse
```

### Health Check

- Endpoint: /health
- Expected response: {"status":"ok"}

## Performance and UX Notes

- Plotly is deferred to improve first paint behavior.
- CSS and JS are split into static assets for browser caching.
- Forecast controls update chart/table views without page reload.

## Accessibility and UX Checklist

- Semantic structure with header and main content regions.
- Responsive layout with readable typography at all breakpoints.
- Keyboard-accessible controls and clear labels.

## Cleanup Status

Legacy Streamlit pages/components/styles are removed from this version.
