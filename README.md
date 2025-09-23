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
├── web/                   # React (Vite+TS) frontend
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

### Frontend Setup (React)

1. Navigate to the web directory:
   ```bash
   cd web
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Optional: set API base URL (defaults to http://localhost:8000):
   ```bash
   echo VITE_API_BASE_URL=http://localhost:8000 > .env
   ```

4. Start the dev server:
   ```bash
   npm run dev
   ```

## 🖥️ Usage

### Command Line Interface

Generate documentation for a Python project:

```bash
python backend/src/cli/main.py --path ./my_project --language python --output md --verbosity high
```

### Web Interface

Start the API server and the React dev server:

```bash
# API
cd backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd ../web
npm run dev
```

Then open your browser to `http://localhost:3000` (React) and ensure the API is at `http://localhost:8000`.

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- API docs: once running, visit `http://localhost:8000/docs`

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