# 🚀 Study Buddy — Industry Production Deployment Guide

This guide provides step-by-step instructions for deploying Study Buddy to production environments using **Docker Compose**, **Render / Railway**, **Vercel**, or **Cloud Providers (AWS / GCP / DigitalOcean)**.

---

## 1. Quick Local Production Setup (Docker Compose)

The fastest way to spin up the entire full-stack production application is using Docker Compose.

```bash
# Clone repository
git clone https://github.com/baranidharan-cse/BIS-AI-Intelligent-Standards-Compliance-Copilot.git
cd study-buddy

# Build & launch containers
docker compose up --build -d
```

- **Frontend**: Available at `http://localhost` or `http://localhost:5173`
- **Backend API**: Available at `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`

To stop containers:
```bash
docker compose down
```

---

## 2. Deploying Backend to Cloud (Render / Railway / Fly.io)

### Option A: Render.com
1. Create a new **Web Service** on Render connected to your GitHub repository.
2. Select **Root Directory**: `backend`
3. Select **Environment**: `Docker`
4. Set Environment Variables:
   - `LLM_PROVIDER`: `demo` (or `watsonx`)
   - `WATSONX_API_KEY`: *(your IBM key if using watsonx)*
   - `WATSONX_PROJECT_ID`: *(your IBM project ID)*
   - `FRONTEND_ORIGIN`: `https://your-frontend.vercel.app`
5. Click **Deploy**. Render will build the Docker container and host your FastAPI API.

---

## 3. Deploying Frontend to Vercel / Netlify

### Option A: Vercel
1. Import your GitHub repository to Vercel.
2. Select **Root Directory**: `frontend`
3. Framework Preset: `Vite`
4. Build Command: `npm run build`
5. Output Directory: `dist`
6. Set Environment Variables:
   - `VITE_API_URL`: `https://your-backend.onrender.com`
7. Click **Deploy**.

---

## 4. Continuous Integration (CI/CD)

The repository includes a GitHub Actions pipeline in `.github/workflows/ci.yml`.

On every push to `main` or Pull Request:
- Runs backend test suite via `pytest`.
- Runs frontend TypeScript type-checking & production build.
- Validates Docker container builds.

---

## 5. Security & Environment Best Practices

- **Never commit `.env` files** containing live API keys to source control.
- Ensure CORS in `app/config.py` explicitly lists your production domain in `FRONTEND_ORIGIN`.
- Use SSL/TLS termination (HTTPS) in production (handled automatically by Render/Vercel/Nginx).
