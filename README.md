# Legal Debate System - AI-Powered Multi-Agent Debate

An intelligent legal debate system that uses multiple AI agents to conduct structured legal debates. Built with LangChain, LangGraph, and Google Gemini.

## 🎯 Features

- **Multi-Agent Architecture**: Prosecution, Defense, and Moderator agents
- **Structured Debates**: Up to 3 rounds of arguments and counter-arguments
- **Case Law Integration**: RAG system for retrieving relevant case law
- **Interactive UI**: Beautiful Streamlit web interface
- **Detailed Analysis**: Comprehensive legal reasoning and citations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

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

5. **Configure API Key**

Copy `.env.example` to `.env` and add your Google API key:
```bash
GOOGLE_API_KEY=your_api_key_here
```

### Running Locally

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📦 Project Structure

```
legal-debate-system/
├── app.py                  # Main Streamlit application
├── main.ipynb             # Jupyter notebook with original code
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example          # Example environment file
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── README.md             # This file
```

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

1. **Enter your Google API Key** in the sidebar (or configure in `.env`)
2. **Enter case details** in the text area (or use the pre-filled example)
3. **Click "Start Legal Debate"** to run the multi-agent debate
4. **View results**:
   - Round-by-round arguments from prosecution and defense
   - Moderator analysis after each round
   - Final judgement with legal reasoning
   - Case citations and statistics

## 🎓 How It Works

### Agent Architecture

1. **Prosecution Agent**
   - Builds strongest case for prosecution
   - Cites relevant case law and statutes
   - Anticipates defense counterarguments

2. **Defense Agent**
   - Defends the accused with legal reasoning
   - Challenges prosecution's arguments
   - Emphasizes rights protections and precedents

3. **Moderator Agent**
   - Evaluates arguments impartially
   - Identifies strengths and weaknesses
   - Guides debate toward consensus
   - Generates final legal judgement

### Workflow

```
User Input → Prosecution → Defense → Moderator → [Repeat up to 3 rounds] → Final Judgement
```

Built with LangGraph for orchestrated multi-agent workflows.

## 🔧 Technologies

- **LangChain**: Framework for LLM applications
- **LangGraph**: Workflow orchestration for multi-agent systems
- **Google Gemini**: Large language model (gemini-2.0-flash-exp)
- **Streamlit**: Web application framework
- **FAISS**: Vector database for case law retrieval
- **Pydantic**: Data validation and parsing

## 📝 Example Cases

The system comes with a pre-filled example case about:
- Miranda rights violations
- Warrantless search and seizure
- Probable cause requirements

You can modify or replace with your own legal scenarios.

## 🛠️ Configuration

### Model Settings

In `app.py`, you can modify:
- `model_name`: Change Gemini model (default: `gemini-2.0-flash-exp`)
- `temperature`: Adjust creativity (0.0 = deterministic, 1.0 = creative)
- Max rounds: Change debate rounds (default: 3)

### Streamlit Config

Edit `.streamlit/config.toml` to customize:
- Theme colors
- Server port
- Browser settings

## 🤝 Contributing

Contributions welcome! Some ideas:
- Add real case law database integration
- Implement different legal domains (civil, criminal, constitutional)
- Add export functionality (PDF reports)
- Multi-language support

## 📄 License

MIT License - feel free to use for educational or commercial purposes.

## ⚠️ Disclaimer

This is an educational tool. The AI-generated legal arguments should not be considered actual legal advice. Always consult qualified legal professionals for real legal matters.

## 🆘 Troubleshooting

### API Key Issues
- Ensure your Google API key is valid
- Check that Gemini API is enabled in your Google Cloud project
- Verify you have sufficient quota/credits

### Installation Errors
```bash
# If you encounter dependency conflicts, try:
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Virtual Environment Not Activating
```bash
# Windows PowerShell - enable script execution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📞 Support

For issues or questions:
- Check the [Streamlit documentation](https://docs.streamlit.io)
- Review [LangChain documentation](https://python.langchain.com)
- Open an issue on GitHub

---

**Made with ⚖️ by AI-Powered Legal Technology**
