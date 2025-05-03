import streamlit as st
import requests
import os
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
os.environ['HF_TOKEN'] = os.getenv("HF_TOKEN")

# Set up the page
st.set_page_config(page_title="GPU Recommender & Chatbot", layout="centered")
st.title("🎯 Clean GPU Name Recommender + Recommendations + PDF ChatBot")

# -------------------------- Step 1: GPU Fetch from API --------------------------
with st.form("gpu_form"):
    st.subheader("Step 1: Get Top 5 GPUs Based on Requirements")
    region = st.selectbox("Region", ["Mumbai", "Delhi", "Noida", "Virginia"])
    operating_system = st.selectbox("Operating System", ["Linux", "Windows"])
    timeline = st.selectbox("Usage Timeline", ["hour", "month", "half_year", "year"])
    budget = st.number_input("Budget (INR)", min_value=1000.0, step=500.0)
    submitted = st.form_submit_button("Get Clean GPU Names")

API_URL = "https://gpu-recommender.onrender.com/api/recommend-gpus"
gpu_list = []

if submitted:
    payload = {
        "region": region.lower(),
        "operating_system": operating_system.lower(),
        "budget": budget,
        "timeline": timeline.lower()
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()

        if result.get("success") and result.get("topGpus"):
            raw_names = [gpu.get("resource_name", "") for gpu in result["topGpus"]]
            gpu_list = [name.replace("N.", "").replace(".512", "") for name in raw_names]

            st.success("✅ Cleaned GPU Names:")
            st.code(gpu_list, language="python")
        else:
            st.warning(result.get("error", "No GPUs found. Your request has been submitted."))

    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

# -------------------------- Step 2: Recommendations using LangChain --------------------------
st.header("🚀 Step 2: Best GPU Recommendations (LLM-based)")

# Initialize embeddings and LLM
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
llm = ChatGroq(groq_api_key=os.environ["GROQ_API_KEY"], model_name="Llama3-8b-8192")

# Caching vector embedding
@st.cache_resource
def create_vector_embedding():
    loader = PyPDFDirectoryLoader("research_papers")
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_docs = splitter.split_documents(documents[:50])
    return FAISS.from_documents(final_docs, embeddings)

# Initialize retriever
if "vectors" not in st.session_state:
    st.session_state.vectors = create_vector_embedding()
retriever = st.session_state.vectors.as_retriever()

# Prompt for GPU recommendation
gpu_prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a technical assistant specializing in GPU advice. Based on the context, provide a **short 2–3 line recommendation** for the GPU mentioned in the question.

Context:
{context}

Question:
{question}

Answer in this format:
"We recommend [GPU] for your task because it has [key features], ideal for [use case]."
"""
)

# GPU recommendation chain
gpu_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=False,
    chain_type_kwargs={"prompt": gpu_prompt_template}
)

# Use dynamic GPU list from Step 1, or default if empty
if not gpu_list:
    gpu_list = ["A100", "H100", "V100"]  # fallback

for gpu in gpu_list:
    with st.spinner(f"🔍 Recommending best use case for {gpu}..."):
        result = gpu_chain.invoke({"query": f"Should I use the {gpu} GPU? What are its key features and best use case?"})
        st.subheader(f"💡 {gpu}")
        st.write(result["result"])

# -------------------------- Step 3: Chatbot from Research Paper --------------------------
st.header("💬 Step 3: Ask Anything from the Research Papers")

chatbot_prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a knowledgeable assistant. Use the context from research papers to answer the user's question clearly and in detail.

Context:
{context}

Question:
{question}

Answer:
"""
)

user_prompt = st.text_input("📌 Enter your question about GPUs or research:")

if user_prompt:
    chatbot_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": chatbot_prompt_template}
    )

    start = time.process_time()
    response = chatbot_chain.invoke({'query': user_prompt})
    end = time.process_time()

    st.markdown(f"⏱️ **Response Time:** {round(end - start, 2)} seconds")
    st.markdown("### 📖 Answer")
    st.write(response["result"])

    with st.expander("📄 Show Relevant Context from PDF"):
        for i, doc in enumerate(response["source_documents"]):
            st.markdown(f"**Snippet {i+1}:**")
            st.write(doc.page_content)
            st.write("---")