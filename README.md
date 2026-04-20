# DataPilot

This repository now contains two separate projects:

- [streamlit/](streamlit/) for the original Streamlit dashboard
- [website/](website/) for the real web app built with FastAPI and Next.js

## Streamlit app

The Streamlit version lives in [streamlit/](streamlit/).

Run it from that folder:

```bash
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```

## Real website

The website lives in [website/](website/).

Backend:

```bash
cd website/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd website/frontend
npm install
npm run dev
```

The frontend opens at http://localhost:3000 and talks to the backend at http://localhost:8000/api.

Startup checklist for the website:

1. Start backend first from `website/backend`.
2. Confirm API health at http://localhost:8000/api/health.
3. Ensure `website/frontend/.env.local` has `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api`.
4. Start frontend from `website/frontend`.
5. Open http://localhost:3000/upload and test CSV upload.

Website pages:

- `/upload` - upload a CSV and inspect preview, columns, and descriptive stats
- `/exploration` - histogram, box plot, correlation, scatter, and categorical charts
- `/preprocessing` - drop columns, missing values, encoding, scaling, outliers
- `/training` - model selection and training
- `/results` - metrics, feature importance, and evaluation charts

New file support:

- The upload flow now accepts CSV and image files.
- Image files are summarized as metadata rows for inspection.
- Trained sklearn models are saved as downloadable `.pkl` artifacts from the results page.

## Current layout

```
DataPilot/
├── README.md
├── streamlit/
│   ├── app.py
│   ├── modules/
│   └── requirements.txt
└── website/
	├── backend/
	└── frontend/
```
