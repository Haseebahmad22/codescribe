# CodeScribe Installation Guide

This guide will help you set up CodeScribe - the AI-Powered Code Documentation Assistant on your system.

## Prerequisites

- Python 3.10 or higher
- Git (for cloning the repository)
- DeepSeek or OpenAI API key (AI provider) or Hugging Face for local models

## Installation Methods

### Method 1: Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/codescribe.git
   cd codescribe
   ```

2. **Set up the backend:**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up the frontend (React):**
   ```bash
   cd ../web
   npm install
   npm run dev
   ```

4. **Configure the application:**
   ```bash
   cd ../backend/config
   cp config.template.yaml config.yaml
   # Edit config.yaml with your settings
   ```

5. **Set environment variables:**
   ```bash
   # Set your OpenAI API key
   export OPENAI_API_KEY="your-api-key-here"
   ```

### Method 2: Docker Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/codescribe.git
   cd codescribe
   ```

2. **Set environment variables:**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

3. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

### Method 3: Package Installation

1. **Install from PyPI (when available):**
   ```bash
   pip install codescribe
   ```

2. **Install from source:**
   ```bash
   git clone https://github.com/your-username/codescribe.git
   cd codescribe
   pip install -e .
   ```

## Configuration

### OpenAI Setup

1. **Get an API key:**
   - Go to https://platform.openai.com/api-keys
   - Create a new API key
   - Copy the key

2. **Set the API key:**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

   Or edit the configuration file:
   ```yaml
   ai:
     provider: "openai"
     openai:
       api_key: "sk-your-key-here"
       model: "gpt-3.5-turbo"
   ```

### Hugging Face Setup (Alternative)

If you prefer to use local models instead of OpenAI:

1. **Install additional dependencies:**
   ```bash
   pip install torch transformers
   ```

2. **Configure for Hugging Face:**
   ```yaml
   ai:
     provider: "huggingface"
     huggingface:
       model: "microsoft/DialoGPT-medium"
   ```

## Verification

### Test the CLI

```bash
cd backend/src
python cli/main.py --help
```

### Test the API

1. **Start the API server:**
   ```bash
   cd backend/src/api
   python main.py
   ```

2. **Test the health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

### Test the Frontend

1. **Start the React dev server:**
   ```bash
   cd web
   npm run dev
   ```

2. **Open your browser to:**
   ```
   http://localhost:3000
   ```

## Troubleshooting

### Common Issues

1. **Import errors:**
   - Make sure you're in the correct directory
   - Verify virtual environment is activated
   - Check Python path configuration

2. **API key issues:**
   - Verify your OpenAI API key is correct
   - Check that the environment variable is set
   - Ensure you have sufficient API credits

3. **Dependencies not found:**
   - Try upgrading pip: `pip install --upgrade pip`
   - Install missing dependencies: `pip install package-name`

4. **Tree-sitter issues (JavaScript parsing):**
   ```bash
   pip install tree-sitter tree-sitter-python tree-sitter-javascript
   ```

5. **Port conflicts:**
   - Change API port in config: `api.port: 8001`
   - Change Streamlit port: `streamlit run app.py --server.port 8502`

### Getting Help

1. **Check the logs:**
   ```bash
   # API logs
   tail -f backend/logs/codescribe.log
   
   # Streamlit logs
   # Check terminal output where you started Streamlit
   ```

2. **Enable debug mode:**
   ```yaml
   logging:
     level: "DEBUG"
   ```

3. **Run tests:**
   ```bash
   cd backend
   python -m pytest tests/ -v
   ```

## Next Steps

Once installation is complete:

1. **Read the User Guide:** `docs/user-guide.md`
2. **Check API Documentation:** `http://localhost:8000/docs`
3. **Try the Examples:** `python examples.py`
4. **Explore Configuration Options:** `backend/config/config.template.yaml`

## Updates

To update CodeScribe:

```bash
git pull origin main
cd backend && pip install -r requirements.txt
cd ../frontend && pip install -r requirements.txt
```

For Docker (API only by default):
```bash
docker-compose down
git pull origin main
docker-compose up --build -d
```