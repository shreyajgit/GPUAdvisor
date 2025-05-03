# GPU Recommender & Research Chatbot

A full‑stack application to help users discover the best GPUs based on region, budget, and usage timeline, and to interact with a research‑paper–powered chatbot for detailed insights.

Video - https://drive.google.com/file/d/1YuwXrVpLt-1kdGy2C1AQuFUaU68KXBgv/view?usp=sharing

Documentation - https://drive.google.com/file/d/1yUdIYdmQZP2WEUQSlfVG41omk_jmYKGc/view?usp=sharing

---


## 🔗 Live Backend API

The recommendation engine backend is deployed on Render:

```
https://gpu-recommender.onrender.com/api/recommend-gpus
```

This API returns the top 5 GPUs for given parameters (region, operating system, timeline, budget).

---

## 🖥️ Frontend (Streamlit)

The Streamlit frontend combines three interactive steps:

1. **Step 1: Fetch & Clean GPU Names**

   * Collects user inputs (region, OS, timeline, budget)
   * Calls the backend API and displays cleaned GPU names
2. **Step 2: GPU Recommendation (LLM-based)**

   * Uses LangChain + Groq LLM to generate short 2–3 line recommendations for each GPU
3. **Step 3: PDF ChatBot**

   * Loads research papers from a local `research_papers/` directory
   * Answers user questions with source snippets

### Folder Structure

```
project-root/
├── backend/               # (Optional local copy of API code)
├── frontend/              # Streamlit client
│   ├── main.py            # Entry point for Streamlit
│   ├── research_papers/   # PDF files for chatbot context
│   └── .env               # GROQ_API_KEY, HF_TOKEN
└── README.md
```

### Getting Started

1. **Clone the repo**

   ```bash
   git clone <repository-url>
   cd project-root
   ```

2. **Install dependencies**

   ```bash
   pip install -r frontend/requirements.txt
   ```

3. **Set up environment**

   Create a `.env` file inside `frontend/`:

   ```ini
   GROQ_API_KEY=<your_groq_api_key>
   HF_TOKEN=<your_huggingface_token>
   ```

4. **Run the Streamlit App**

   ```bash
   cd frontend
   streamlit run main.py
   ```

This will open the app in your default browser at `http://localhost:8501`.

---

## 🚀 Tech Stack

* **Backend**

  * Python, FastAPI (or Flask)
  * Hosted on Render.io
* **Frontend**

  * Streamlit
  * Requests for API calls
  * LangChain + ChatGroq for LLM integrations
  * FAISS for vector search over PDFs
  * SentenceTransformers for embeddings
* **Research Papers**

  * Local `research_papers/` directory
  * RecursiveCharacterTextSplitter for chunking

---

## ⭐ Features

* Dynamic top‑5 GPU recommendation by region, OS, timeline, and budget
* Cleaned, human‑readable GPU names
* Short, LLM‑generated usage recommendations
* Interactive PDF‑based chatbot with snippet‑level context
* Easy deployment with Render (backend) and Streamlit (frontend)

---

## 🔧 Configuration & Deployment

* **Backend**: ensure `RENDER` environment and any API keys are set on Render.io
* **Frontend**: configure `.env` and run `streamlit run main.py`

---

## 🤝 Contributing

Feel free to open issues or submit pull requests for improvements!

---

**File to run:** `frontend/main.py`

Happy GPU‑hunting and research exploration! 🎉
