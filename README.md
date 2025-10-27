# Legal Debate System - AI-Powered Multi-Agent Debate

An intelligent legal debate system that uses multiple AI agents to conduct structured legal debates. Refactored with clean package structure, comprehensive tests, and Docker support.

## 🎯 Features

- **Multi-Agent Architecture**: Prosecution, Defense, and Judge agents
- **Structured Debates**: Configurable rounds of arguments and counter-arguments
- **Deterministic Mode**: Mock LLM for testing without API keys
- **Interactive UI**: Beautiful Streamlit web interface
- **Comprehensive Tests**: Full test coverage with pytest
- **Docker Support**: Containerized deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized deployment)
- OpenAI API Key (optional - works in mock mode without it)

### Installation

1. **Clone or download this repository**

2. **Create virtual environment**
```bash
python -m venv .venv
```

3. **Activate virtual environment**
```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running Locally

**With Streamlit UI:**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

**In Deterministic Mode (no API key needed):**
```bash
# Set environment variable for mock mode
export MOCK_LLM=true  # Linux/Mac
set MOCK_LLM=true     # Windows

streamlit run app.py
```

**Run Tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_orchestrator.py -v
```

**Format Code:**
```bash
black src/ tests/
```

## 📦 Project Structure

```
legal-debate-system/
├── app.py                  # Thin shim - entry point for Streamlit
├── src/                    # Main package
│   ├── __init__.py
│   ├── core/              # Core debate logic
│   │   ├── __init__.py
│   │   ├── messages.py    # Data structures
│   │   └── orchestrator.py # Debate orchestration
│   ├── utils/             # Utility modules
│   │   ├── __init__.py
│   │   └── llm_client.py  # LLM client with mock support
│   └── app/               # Streamlit application
│       ├── __init__.py
│       └── main.py        # Main UI implementation
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_orchestrator.py
│   └── test_smoke.py
├── Dockerfile             # Docker configuration
├── .dockerignore
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment file
└── README.md             # This file
```

## 🐳 Docker Deployment

**Build the image:**
```bash
docker build -t legal-debate-system .
```

**Run in mock mode (default, no API key needed):**
```bash
docker run -p 8501:8501 legal-debate-system
```

**Run with real LLM (provide API key):**
```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_api_key_here \
  -e MOCK_LLM=false \
  legal-debate-system
```

Access the app at `http://localhost:8501`

## 🌐 Deployment to Streamlit Cloud

### Deploy to Streamlit Cloud (Free Hosting)

1. **Push your code to GitHub**
   - Create a new repository on GitHub
   - Push your code (make sure `.env` is in `.gitignore`)

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Add secrets: Go to Advanced settings → Secrets
   - Add your API key:
     ```toml
     GOOGLE_API_KEY = "your_api_key_here"
     ```
   - Click "Deploy"

3. **Your app will be live!**
   - URL format: `https://[app-name]-[random-string].streamlit.app`

## 💡 Usage

### Deterministic Mode (Testing)

The system includes a deterministic mock LLM that provides predictable responses without requiring an API key. This is perfect for:
- Testing and development
- CI/CD pipelines
- Demonstrations without API costs
- Understanding system behavior

**Enable deterministic mode:**
- Leave API key blank in the UI
- Set `MOCK_LLM=true` environment variable
- No API key configured in `.env`

**Example with mock LLM:**
```python
from src.core.orchestrator import DebateOrchestrator
from src.utils.llm_client import LLMClient

# Create orchestrator with mock LLM
orchestrator = DebateOrchestrator(max_rounds=2)
orchestrator.start_debate("Sample legal case")

# Run debate
orchestrator.step()  # Round 1
orchestrator.step()  # Round 2
result = orchestrator.evaluate()

print(f"Winner: {result.winner}")
print(f"Scores: {result.scores}")
```

### Web Interface Usage

1. **Start the application** (see Running Locally above)
2. **Optional: Enter API Key** in the sidebar (leave blank for mock mode)
3. **Enter case details** in the text area (or use the pre-filled example)
4. **Configure debate settings** (number of rounds)
5. **Click "Start Legal Debate"**
6. **View results**:
   - Round-by-round arguments from prosecution and defense
   - Judge's final evaluation and scores
   - Debate statistics and breakdown
## 🎓 How It Works

### Architecture Overview

The system uses a clean, modular architecture:

1. **Core Package (`src.core`)**
   - `messages.py`: Data structures (AgentMessage, DebateResult)
   - `orchestrator.py`: Main debate logic and flow control

2. **Utils Package (`src.utils`)**
   - `llm_client.py`: LLM abstraction with mock support

3. **App Package (`src.app`)**
   - `main.py`: Streamlit UI implementation

### Agent Roles

1. **Prosecution Agent**
   - Builds strongest case for prosecution
   - Presents arguments supporting conviction
   - Responds to defense arguments

2. **Defense Agent**
   - Defends the accused with legal reasoning
   - Challenges prosecution's arguments
   - Creates reasonable doubt

3. **Judge Agent**
   - Evaluates arguments impartially
   - Assigns scores (0-10) to each side
   - Determines the winner based on argument strength

### Debate Flow

```
Initialize → Round 1 (P→D) → Round 2 (P→D) → ... → Judge Evaluation → Result
```

Each round:
1. Prosecution presents argument
2. Defense responds
3. Arguments are recorded

After all rounds:
- Judge evaluates all arguments
- Scores are assigned
- Winner is determined

## 🔧 Technologies

- **Python 3.11+**: Core language
- **Streamlit**: Web application framework
- **Pytest**: Testing framework
- **Docker**: Containerization
- **LangChain** (optional): For real LLM integration
- **OpenAI API** (optional): For real LLM responses

## 🧪 Testing

The project includes comprehensive tests:

**Test Structure:**
- `test_orchestrator.py`: Core debate logic tests
- `test_smoke.py`: Import and integration tests

**Run tests:**
```bash
# All tests
pytest

# Verbose mode
pytest -v

# With coverage
pytest --cov=src

# Specific test
pytest tests/test_orchestrator.py::test_full_debate_with_mock_llm
```

**All tests pass without API keys** using the mock LLM.

## 📝 Example Cases

The system comes with a pre-filled example case about:
- Miranda rights violations
- Warrantless search and seizure
- Probable cause requirements

You can modify or replace with your own legal scenarios.

## 🤝 Contributing

Contributions welcome! Ideas:
- Add real LLM integration (OpenAI, Anthropic, etc.)
- Implement different legal domains (civil, criminal, constitutional)
- Add export functionality (PDF reports)
- Multi-language support
- Enhanced UI features

**Development Process:**
1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run `black` formatter and `pytest`
5. Submit a pull request

## 📄 License

MIT License - feel free to use for educational or commercial purposes.

## ⚠️ Disclaimer

This is an educational tool. The AI-generated legal arguments should not be considered actual legal advice. Always consult qualified legal professionals for real legal matters.

## 🆘 Troubleshooting

### Tests Not Running
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run from project root
pytest -v
```

### Import Errors
```bash
# Ensure you're in project root and Python can find src/
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%          # Windows
```

### Docker Build Issues
```bash
# Clean build
docker build --no-cache -t legal-debate-system .

# Check logs
docker logs <container_id>
```

### Streamlit Won't Start
```bash
# Check if port is available
lsof -i :8501  # Linux/Mac
netstat -ano | findstr :8501  # Windows

# Use different port
streamlit run app.py --server.port 8502
```

## 📞 Support

For issues or questions:
- Check the [Streamlit documentation](https://docs.streamlit.io)
- Check the [pytest documentation](https://docs.pytest.org)
- Open an issue on GitHub

---

**Made with ⚖️ by AI-Powered Legal Technology**
