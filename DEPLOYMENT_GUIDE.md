# Comprehensive Deployment & Configuration Guide

This guide will walk you step-by-step through setting up your free-tier production environment, acquiring the necessary API keys, and deploying the **AI-Based Cognitive Gaming Platform** to the internet.

---

## Part 1: Acquiring Environment Keys

You need to register for a few free services. Keep a notepad open to copy-paste the keys as you generate them.

### 1. Supabase (Database & Authentication)
Supabase is an open-source Firebase alternative that provides a free PostgreSQL database.
1. Go to [supabase.com](https://supabase.com) and create a free account.
2. Click **"New Project"**. Select your organization and a region closest to India (e.g., Mumbai or Singapore).
3. **Important:** Create a strong Database Password and save it somewhere safe. You will need it.
4. Wait for the database to provision (takes a few minutes).
5. **Get the Keys:**
   * Go to **Project Settings** (the gear icon on the left sidebar).
   * Click **Database**. Scroll down to **Connection string** -> **URI**. 
     * *Copy this.* It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.[REF].supabase.co:5432/postgres`. (Replace `[YOUR-PASSWORD]` with the password you made in step 3). This is your `DATABASE_URL`.
   * Click **API** under Project Settings.
     * Copy the **Project URL**. This is your `SUPABASE_URL` and `VITE_SUPABASE_URL`.
     * Copy the **anon** `public` key. This is your `VITE_SUPABASE_ANON_KEY`.
     * Copy the **service_role** `secret` key. This is your `SUPABASE_SERVICE_ROLE_KEY`.
     * Scroll down to **JWT Settings** and copy the **JWT Secret**. This is your `JWT_SECRET`.

### 2. Bhashini (AI Translation & Voice)
Bhashini provides Indic language translation, Text-to-Speech (TTS), and Speech-to-Text (STT).
1. Go to [bhashini.gov.in/bhashadaan](https://bhashini.gov.in/) (or the developer portal at [Bhashini API](https://bhashini.gov.in/en/bhashini-api)).
2. Register for a Developer Account.
3. Once approved/logged in, go to your **Dashboard** or **Profile**.
4. Generate or reveal your **API Key** and **User ID**.
   * Copy the API Key -> This is your `BHASHINI_API_KEY`.
   * Copy the User/Client ID -> This is your `BHASHINI_USER_ID`.

### 3. Cloudinary (Media Storage)
Used for storing images and audio uploads for the Reminiscence Therapy feature.
1. Go to [cloudinary.com](https://cloudinary.com) and sign up for a free account.
2. On your main Dashboard, look at the **Product Environment Credentials**.
3. Copy the **API Environment variable** (starts with `cloudinary://...`).
   * This is your `CLOUDINARY_URL`.

### 4. Resend (Email Notifications)
Replaces simulated SMS/Push notifications with real email alerts for caregivers.
1. Go to [resend.com](https://resend.com) and sign up.
2. Go to **API Keys** on the left menu.
3. Click **Create API Key**. Give it a name and give it "Full Access".
4. Copy the generated key (starts with `re_...`).
   * This is your `RESEND_API_KEY`.

---

## Part 2: Local Configuration

Now that you have all your keys, I (the AI) need them to configure your `.env` file. 
Once you paste them into the chat, I will set up the local environment and begin refactoring the code to use real databases instead of the mock data.

---

## Part 3: Deploying the Application Online

After I finish refactoring the codebase to use these live services, you will deploy the code using Render (Backend) and Vercel (Frontend). Here is exactly how that will happen:

### Step 1: Push Code to GitHub
1. Create a free account on [GitHub](https://github.com) if you don't have one.
2. Create a new private repository.
3. Push this entire project folder to that GitHub repository.

### Step 2: Deploy the Backend (Render)
1. Go to [render.com](https://render.com) and sign up using your GitHub account.
2. Click **New +** -> **Web Service**.
3. Select **"Build and deploy from a Git repository"** and select your GitHub repo.
4. **Configuration:**
   * **Name:** `brain-blast-backend`
   * **Root Directory:** `backend` (Important!)
   * **Environment:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 10000`
   * **Instance Type:** Free
5. **Environment Variables:** Scroll down and click "Advanced". Add all backend keys from your `.env` file (e.g., `DATABASE_URL`, `SUPABASE_URL`, `BHASHINI_API_KEY`, etc.).
6. Click **Create Web Service**. 
7. Once deployed, Render will give you a URL (e.g., `https://brain-blast-backend.onrender.com`). *Copy this URL.*

### Step 3: Deploy the Frontend (Vercel)
1. Go to [vercel.com](https://vercel.com) and sign up using your GitHub account.
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository.
4. **Configuration:**
   * **Framework Preset:** Vite
   * **Root Directory:** Edit this and select `frontend`.
5. **Environment Variables:**
   * Name: `VITE_API_BASE_URL` | Value: `[Your Render URL from Step 2]` (e.g., `https://brain-blast-backend.onrender.com`)
   * Add the frontend Supabase keys (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`).
6. Click **Deploy**.
7. Vercel will build your React application and give you a live URL (e.g., `https://brain-blast-frontend.vercel.app`).

### Step 4: Final Connection (CORS)
1. Go back to Render (your backend).
2. Go to **Environment** settings.
3. Add or update the `CORS_ORIGINS` variable. Set it to your new Vercel URL: `https://brain-blast-frontend.vercel.app`.
4. Render will automatically redeploy. 

**Congratulations! Your application is now live on the internet, backed by a real database, real AI, and real authentication.**
