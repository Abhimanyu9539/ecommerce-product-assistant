# Ecommerce Product Assistant

An intelligent AI-powered assistant designed to help with e-commerce product research and analysis. This project combines web scraping, vector search (RAG), and agentic workflows to provide detailed product insights.

## 🎥 Demo

<video controls src="walkthrough.mp4" width="100%"></video>

## 🚀 Features

- **Product Scraping**: Scrape product details and reviews from Flipkart using a user-friendly Streamlit interface.
- **Data Ingestion**: Automatically process and store scraped data into AstraDB for efficient retrieval.
- **AI Chat Assistant**: A FastAPI-based chat interface that uses Agentic RAG to answer user queries about products based on the scraped data.
- **Multi-LLM Support**: Integrates with OpenAI, Google Gemini, and Groq for robust language processing.
- **MCP Server**: Includes a Model Context Protocol (MCP) server (`product_search_server.py`) for integrating product search with MCP-compliant clients (e.g., Claude Desktop).

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Web Framework**: FastAPI
- **UI**: Streamlit (for scraping), HTML/Jinja2 (for chat)
- **AI/LLM Framework**: LangChain, LangGraph
- **Database**: AstraDB (Vector Store)
- **Scraping**: Selenium, BeautifulSoup4
- **Containerization**: Docker

## 📋 Prerequisites

Ensure you have the following installed:
- Python 3.10 or higher
- Docker (optional, for containerized deployment)
- [AstraDB Account](https://astra.datastax.com/)
- API Keys for:
  - OpenAI
  - Google Gemini
  - Groq

## ⚙️ Configuration

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ecommerce-product-assistant
   ```

2. **Set up environment variables:**
   Create a `.env` file in the root directory and add your API keys. You can use `.env.copy` as a template.
   ```bash
   cp .env.copy .env
   ```
   
   Edit `.env` with your actual keys:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_API_KEY=your_google_api_key
   OPENAI_API_KEY=your_openai_api_key
   ASTRA_DB_API_ENDPOINT=your_astra_db_endpoint
   ASTRA_DB_APPLICATION_TOKEN=your_astra_db_token
   ASTRA_DB_KEYSPACE=default_keyspace
   ```

## 📦 Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃‍♂️ Usage

### 1. Data Scraping & Ingestion
Run the Streamlit app to scrape product reviews and ingest them into the vector database.

```bash
streamlit run scrapper_ui.py
```
- Enter product names or descriptions.
- Click **Start Scraping** to fetch data.
- Once scraped, click **Store in Vector DB** to populate AstraDB.

### 2. Chat Assistant
Start the FastAPI server to interact with the AI assistant.

```bash
uvicorn prod_assistant.router.main:app --reload
```
- Open your browser and navigate to `http://localhost:8000`.
- Start chatting with the assistant about the products you scraped!

## 🐳 Docker Support

Build and run the application using Docker.

```bash
# Build the image
docker build -t ecomm-assistant .

# Run the container (ensure .env is passed)
docker run --env-file .env -p 8000:8000 ecomm-assistant
```



## 📂 Project Structure

```
ecommerce-product-assistant/
├── data/               # Stored scraped data (CSV)
├── prod_assistant/     # Main application package
│   ├── etl/            # Scraping and ingestion logic
│   ├── router/         # FastAPI routes
│   ├── workflow/       # LangGraph agent workflows
│   └── ...
├── templates/          # HTML templates for chat UI
├── static/             # Static assets (CSS, JS)
├── scrapper_ui.py      # Streamlit entry point
├── requirements.txt    # Python dependencies
└── ...
```
