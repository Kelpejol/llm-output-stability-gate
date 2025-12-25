# 🛡️ LLM Output Stability Gate (UQLM)


A pre-execution reliability gate for LLM systems that quantifies output uncertainty using UQLM and enforces explicit confidence thresholds.

## 🎯 Why This Exists

LLM failures often stem from **unstable or low-confidence outputs**, not model incapability.

Given the same prompt, an LLM may:
- Produce contradictory answers
- Hallucinate inconsistently  
- Vary significantly across generations

This project uses **uncertainty quantification** as a **control gate** before LLM outputs are accepted.

## ✨ Features

- 🔍 **Multi-sample uncertainty quantification** using UQLM
- 🎯 **Confidence scoring** between 0 and 1
- 🚦 **Configurable thresholds** for acceptance/rejection
- ⚡ **Fast API** for integration
- 🐳 **Docker ready**
- 🧪 **Well tested**

## 🚀 Quick Start

### Installation

```bash
# Clone the repo
git clone https://github.com/kelpejol/llm-output-stability-gate.git
cd llm-output-stability-gate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY=your_key_here

# Run the server
uvicorn gate.main:app --reload
```

### Docker

```bash
docker-compose up -d
```

### First API Call

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain Paxos in simple terms",
    "min_confidence": 0.7,
    "num_samples": 5
  }'
```

**Response:**
```json
{
  "confidence_score": 0.73,
  "passed": true
}
```

## 📖 API Documentation

### POST `/evaluate`

Evaluate prompt stability and confidence.

**Request:**
```json
{
  "prompt": "string",
  "min_confidence": 0.6,
  "num_samples": 5
}
```

**Response (Pass):**
```json
{
  "confidence_score": 0.75,
  "passed": true
}
```

**Response (Fail):**
```json
{
  "confidence_score": 0.42,
  "passed": false,
  "reason": "Output confidence 0.42 is below required threshold 0.60"
}
```

**Interactive Docs:** Visit `http://localhost:8000/docs` after starting the server.

## 🏗️ Architecture

```
Prompt
  ↓
Multiple Generations (5x)
  ↓
UQLM Uncertainty Scoring
  ↓
Policy Enforcement (threshold check)
  ↓
Accept / Reject
```

### Design Principles

- **Fail fast** - Invalid outputs rejected immediately
- **Explicit trust decisions** - No silent acceptance
- **Model-agnostic** - Works with any LLM backend
- **Separation of concerns** - Scoring separate from policy

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=gate

# Specific test file
pytest tests/test_api.py
```

## 🛠️ Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Format code
black gate/ tests/

# Run linter
ruff check gate/
```

## 📦 Deployment

### Environment Variables

```bash
OPENAI_API_KEY=your_key
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

See `.env.example` for all options.

## 🎯 Use Cases

- **Agent execution gating** - Verify output before action
- **Tool invocation safety** - Check confidence before API calls
- **Autonomous workflows** - Add reliability checkpoints
- **Trust-aware pipelines** - Route based on confidence
- **Infrastructure automation** - Prevent low-confidence changes

## 📊 How UQLM Works

UQLM measures semantic agreement across multiple LLM outputs using information-theoretic metrics.

**More robust than:**
- Single-response heuristics
- Regex or keyword filters
- Length-based checks

**References:**
- [UQLM Paper](https://arxiv.org/abs/2305.19187)
- [UQLM GitHub](https://github.com/zlin7/UQ-NLG)

## 🤝 Contributing

Contributions are welcome! Please check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [UQLM](https://github.com/zlin7/UQ-NLG) for uncertainty quantification
- [FastAPI](https://fastapi.tiangolo.com/) for the framework
- [LangChain](https://www.langchain.com/) for LLM orchestration

## 📞 Support

- 🐛 [Report Issues](https://github.com/kelpejol/llm-output-stability-gate/issues)
- 💬 [Discussions](https://github.com/kelpejol/llm-output-stability-gate/discussions)

## 🔮 Future Work

- White-box uncertainty scoring
- Batch and streaming evaluation
- Drift detection over time
- Policy composition
- Model-agnostic backends
- Human-in-the-loop escalation
