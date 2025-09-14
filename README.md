# CodeScribe - AI-Powered Code Documentation Assistant

CodeScribe is a Python-based tool designed to automatically generate high-quality documentation and comments for codebases using AI. It helps developers understand, maintain, and scale their projects efficiently, while reducing manual documentation effort.

## 🚀 Features

- **Multi-language Support**: Python, JavaScript, and more
- **AI-Powered Documentation**: Uses OpenAI GPT or Hugging Face models
- **Batch Processing**: Process entire project directories
- **Flexible Output**: Generate Markdown, HTML, or inline comments
- **Web Interface**: Upload and preview documentation in real-time
- **CLI Tool**: Command-line interface for automation
- **Customizable**: Configure style, verbosity, and templates

## 📁 Project Structure

```
codescribe/
├── backend/                 # Python backend
│   ├── src/
│   │   ├── parsers/        # Code parsing modules
│   │   ├── generators/     # AI documentation generators
│   │   ├── api/           # REST API endpoints
│   │   └── cli/           # Command-line interface
│   ├── config/            # Configuration files
│   └── tests/             # Test suite
├── frontend/              # Web interface
└── docs/                  # Documentation
```

## 🛠️ Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your API keys:
   ```bash
   cp config/config.template.yaml config/config.yaml
   # Edit config.yaml with your OpenAI API key
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (for React frontend):
   ```bash
   npm install
   ```

   Or for Streamlit:
   ```bash
   pip install streamlit
   ```

## 🖥️ Usage

### Command Line Interface

Generate documentation for a Python project:

```bash
python backend/src/cli/main.py --path ./my_project --language python --output md --verbosity high
```

### Web Interface

Start the web application:

```bash
# For Streamlit
streamlit run frontend/app.py

# For Flask/FastAPI
python backend/src/api/main.py
```

Then open your browser to `http://localhost:8501` (Streamlit) or `http://localhost:8000` (FastAPI).

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [CLI Reference](docs/cli-reference.md)
- [API Documentation](docs/api-reference.md)
- [Configuration Guide](docs/configuration.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT API
- Hugging Face for Transformers
- The open-source community for inspiration