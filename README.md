# Legal Debate System - AI-Powered Multi-Agent Debate

[![CI](https://github.com/Tumul001/Legal-debate-system-with-multi-agent-architecture/actions/workflows/ci.yml/badge.svg)](https://github.com/Tumul001/Legal-debate-system-with-multi-agent-architecture/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

An intelligent legal debate system that uses multiple AI agents to conduct structured legal debates. Built with LangChain, LangGraph, and Google Gemini, this system simulates real legal proceedings with prosecution, defense, and moderator agents.

## 🎯 Features

- **Multi-Agent Architecture**: Independent prosecution, defense, and moderator agents
- **Structured Debates**: Up to 3 rounds of arguments and counter-arguments
- **ML-Based Confidence Scoring**: Sentiment analysis and citation quality metrics
- **Case Law Integration**: RAG system for retrieving relevant precedents
- **Interactive UI**: Beautiful Streamlit web interface
- **Detailed Analysis**: Comprehensive legal reasoning and citations
- **Deterministic Testing**: MockLLM for offline development and testing
- **Docker Support**: Reproducible containerized deployment
- **CI/CD Pipeline**: Automated testing and code quality checks

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Installation](#installation)
  - [Local Installation](#local-installation)
  - [Docker Installation](#docker-installation)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Deterministic Mode](#deterministic-mode)
- [Evaluation](#evaluation)
- [Limitations and Ethics](#limitations-and-ethics)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The Legal Debate System is designed as an educational tool and research platform for understanding multi-agent AI systems in legal contexts. It demonstrates:

- **Multi-agent coordination** using LangGraph workflows
- **Structured argumentation** with legal precedents and citations
- **Real-time evaluation** of legal arguments
- **ML-powered confidence scoring** combining sentiment analysis and structural metrics

### Use Cases

- **Legal Education**: Teaching argumentation and case analysis
- **Research**: Studying AI in legal reasoning
- **Practice**: Preparing for debates or understanding opposing viewpoints
- **Development**: Testing multi-agent AI architectures

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Web UI                      │
│                  (src/app/main.py)                      │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Debate Orchestrator                         │
│            (src/core/orchestrator.py)                    │
└─────┬────────────────────────────────────────┬──────────┘
      │                                        │
┌─────▼──────────┐  ┌──────────────┐  ┌──────▼──────────┐
│  Prosecution   │  │  Moderator   │  │    Defense      │
│     Agent      │  │    Agent     │  │     Agent       │
└────────┬───────┘  └──────┬───────┘  └────────┬────────┘
         │                 │                     │
         └─────────────────┼─────────────────────┘
                           │
                ┌──────────▼──────────┐
                │    LLM Client       │
                │ (Google Gemini or   │
                │      MockLLM)       │
                └─────────────────────┘
```

### Package Structure

```
legal-debate-system/
├── src/
│   ├── app/
│   │   └── main.py              # Streamlit UI
│   ├── core/
│   │   ├── orchestrator.py      # Debate workflow management
│   │   └── messages.py          # Data structures (typed)
│   └── utils/
│       └── llm_client.py        # LLM wrapper + MockLLM
├── tests/
│   ├── test_smoke.py            # Basic functionality tests
│   └── test_orchestrator.py    # Orchestrator tests
├── .github/workflows/
│   └── ci.yml                   # CI/CD pipeline
├── app.py                       # Original entrypoint (maintained)
├── Dockerfile                   # Container definition
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── CONTRIBUTING.md             # Contributor guide
└── LICENSE                     # MIT License
```

### Agent Workflow

1. **Prosecution Agent** presents initial case based on facts
2. **Defense Agent** responds with counter-arguments
3. **Moderator Agent** evaluates arguments and identifies key issues
4. Repeat for configured rounds (default: 3)
5. **Final Judgement** synthesized by moderator

## Installation

### Prerequisites

- Python 3.8 or higher
- pip and virtualenv
- Docker (optional, for containerized deployment)
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Local Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Tumul001/Legal-debate-system-with-multi-agent-architecture.git
   cd Legal-debate-system-with-multi-agent-architecture
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key**:
   ```bash
   cp .env.example .env
   # Edit .env and add: GOOGLE_API_KEY=your_api_key_here
   ```

5. **Run the application**:
   ```bash
   streamlit run app.py
   ```

The app will open at `http://localhost:8501`

### Docker Installation

1. **Build the Docker image**:
   ```bash
   docker build -t legal-debate-system .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8501:8501 \
     -e GOOGLE_API_KEY=your_api_key_here \
     legal-debate-system
   ```

3. **Access the app** at `http://localhost:8501`

#### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./.streamlit:/app/.streamlit
```

Run with:
```bash
docker-compose up
```

## Usage

### Basic Usage

1. **Launch the application** (see Installation)
2. **Enter case details** in the text area or use the pre-filled example
3. **Click "Start Legal Debate"** to begin
4. **View results**:
   - Round-by-round arguments from prosecution and defense
   - ML confidence analysis for each argument
   - Moderator evaluation after each round
   - Final legal judgement
   - Citation summary

### Example Case

The system includes a pre-filled example about Miranda rights and search/seizure:

> John Doe was arrested for theft after being stopped by police officers who noticed him acting suspiciously near a jewelry store. During the stop, officers found stolen jewelry in his backpack. However, John claims:
> 1. He was not informed of his Miranda rights before questioning
> 2. The search of his backpack was conducted without a warrant
> 3. The officers had no probable cause for the initial stop
>
> Legal Question: Should the evidence (stolen jewelry) be admissible in court?

### Advanced Configuration

Modify settings in `src/app/main.py`:

```python
# Change model
model_name = "gemini-2.0-flash-exp"  # or other Gemini models

# Adjust temperature (0.0 = deterministic, 1.0 = creative)
temperature = 0.3

# Change maximum rounds
max_rounds = 3
```

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-cov black isort flake8 mypy
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_smoke.py -v

# Run tests matching a pattern
pytest tests/ -k "test_orchestrator"
```

### Test Categories

- **Smoke tests**: Basic functionality without external dependencies
- **Orchestrator tests**: Debate flow and state management
- **Integration tests**: Full system tests (require API key)

### Continuous Integration

The CI pipeline (`.github/workflows/ci.yml`) automatically:

1. Installs dependencies
2. Runs black (code formatting check)
3. Runs isort (import sorting)
4. Runs flake8 (linting)
5. Runs mypy (type checking, ignores missing imports)
6. Runs pytest (all tests)

Tests run on Python 3.8, 3.9, 3.10, 3.11, and 3.12.

## Deterministic Mode

For development and testing without API costs, use `MockLLM`:

### In Tests

```python
from src.utils.llm_client import MockLLM

def test_debate():
    mock_llm = MockLLM()
    response = mock_llm.invoke([])
    # response.content contains predictable JSON
```

### Custom Mock Responses

```python
custom_responses = [
    '{"position": "prosecution", "main_argument": "Custom argument..."}',
    '{"position": "defense", "main_argument": "Custom defense..."}'
]
mock_llm = MockLLM(responses=custom_responses)
```

### Environment Variable

Set `USE_MOCK_LLM=true` in `.env` to use mock mode in the UI (if implemented).

## Evaluation

### Confidence Scoring

The system uses ML-based confidence scoring with multiple factors:

1. **Sentiment Analysis (40% weight)**
   - Polarity: More positive/assertive = higher confidence
   - Objectivity: Less subjective = better for legal arguments

2. **Citation Quality (30% weight)**
   - Number of citations (optimal: 5)
   - Recency of cases (1950-2025)

3. **Thoroughness (20% weight)**
   - Reasoning length (target: 200 words)
   - Supporting points (target: 5)
   - Statutes cited (target: 3)

4. **Acknowledged Weaknesses (10% weight)**
   - Acknowledging 1-2 weaknesses = optimal
   - None = suspicious, many = too defensive

### Viewing Confidence Breakdown

Each argument displays an expandable "ML Confidence Analysis" section showing:
- Sentiment polarity and subjectivity
- Citation and statute counts
- Reasoning length
- Weaknesses acknowledged

### Metrics

Track debate quality through:
- **Confidence scores**: Per-argument strength assessment
- **Citation coverage**: Number and quality of precedents
- **Round completion**: Whether full debate occurred
- **Argument balance**: Prosecution vs. defense metrics

## Limitations and Ethics

### Legal Disclaimer

⚠️ **IMPORTANT**: This is an educational tool for learning and research purposes only.

- **Not Legal Advice**: AI-generated arguments should NOT be considered actual legal advice
- **No Attorney-Client Relationship**: Using this tool does not create any legal relationship
- **Consult Professionals**: Always consult qualified legal professionals for real legal matters
- **Jurisdiction Matters**: Laws vary by jurisdiction; the system may not reflect local law

### Limitations

1. **Case Law Accuracy**
   - Mock RAG system; not connected to real legal databases
   - Citations may be fictional or outdated
   - Always verify citations independently

2. **Legal Reasoning**
   - AI may miss nuances of legal interpretation
   - May not consider all relevant precedents
   - Reasoning may contain logical gaps

3. **Bias Considerations**
   - LLMs can reflect biases in training data
   - May favor certain legal philosophies
   - Should not be used for actual case decisions

4. **Technical Limitations**
   - Requires internet connection (for real LLM mode)
   - API rate limits may apply
   - Response quality depends on model version

### Ethical Use

- **Education**: Use for learning, not case preparation
- **Research**: Study AI capabilities, not legal outcomes
- **Transparency**: Disclose AI usage if sharing outputs
- **Privacy**: Don't input confidential case information
- **Fairness**: Don't use to circumvent legal process

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

### Quick Start for Contributors

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/Legal-debate-system-with-multi-agent-architecture.git
cd Legal-debate-system-with-multi-agent-architecture

# Create feature branch
git checkout -b feature/your-feature

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black isort flake8 mypy

# Make changes and test
black src/ tests/
pytest tests/

# Submit PR
git push origin feature/your-feature
```

### Areas for Contribution

- Real case law database integration
- Additional legal domains (civil, constitutional, etc.)
- Multi-language support
- Export functionality (PDF/Word)
- Enhanced evaluation metrics
- UI/UX improvements

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **LangChain**: Framework for LLM applications
- **LangGraph**: Multi-agent workflow orchestration
- **Google Gemini**: Large language model
- **Streamlit**: Web application framework
- **TextBlob**: Sentiment analysis

## Support

- **Documentation**: This README and [CONTRIBUTING.md](CONTRIBUTING.md)
- **Issues**: [GitHub Issues](https://github.com/Tumul001/Legal-debate-system-with-multi-agent-architecture/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Tumul001/Legal-debate-system-with-multi-agent-architecture/discussions)

## Roadmap

- [ ] Integration with real legal databases (CourtListener, Case.law)
- [ ] Support for multiple legal systems (common law, civil law)
- [ ] Advanced evaluation metrics and benchmarks
- [ ] Multi-language support
- [ ] Export to PDF/Word with formatting
- [ ] Collaborative debate mode
- [ ] Historical case analysis
- [ ] Legal research assistant features

---

**Made with ⚖️ for Legal Education and AI Research**

*Remember: This tool is for educational purposes. Always consult qualified legal professionals for real legal matters.*
