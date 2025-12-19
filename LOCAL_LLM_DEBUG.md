# Local LLM Debug Mode - Summary

## What Was Added

You now have **two LLM modes** for development:

1. **Perplexity (Cloud)** - Production-ready, API-based
2. **Ollama (Local)** - Free, offline, perfect for debugging

## Quick Setup

### For Ollama (Local/Free)

```bash
# 1. Install Ollama
# macOS: brew install ollama
# Linux: curl https://ollama.ai/install.sh | sh
# Windows: Download from https://ollama.ai

# 2. Start Ollama server
ollama serve

# 3. Download a model (in another terminal)
ollama pull llama2

# 4. In VSCode, select "Debug with Local Llama (Ollama)" and press F5
```

### For Perplexity (Cloud)

Use the existing "Debug with Formula Iozzi" configuration.

## Configuration Options

Edit `.env`:
```env
# Use local LLM (set to "local" or "perplexity")
LLM_MODE=local

# For local Ollama:
OLLAMA_MODEL_NAME=llama2
OLLAMA_BASE_URL=http://localhost:11434

# For Perplexity:
PERPLEXITY_API_KEY=your_key_here
```

Or via environment variables:
```bash
export LLM_MODE=local
export OLLAMA_MODEL_NAME=llama2
python src/main.py https://formulaiozzi.com
```

## VSCode Debug Configurations

Three new debug modes available:

1. **Debug with Formula Iozzi** - Uses Perplexity API
2. **Debug with Local Llama (Ollama)** - Uses local Ollama model
3. **Debug Workflow** - For testing workflow logic

Select in VSCode debug dropdown and press **F5**.

## Files Modified

- ✅ `src/config.py` - Added LLM mode selection
- ✅ `src/agents/product_extraction.py` - Added Ollama support
- ✅ `pyproject.toml` - Added optional `langchain-community` dependency
- ✅ `.vscode/launch.json` - Added local debug config
- ✅ `.env.example` - Updated with LLM mode options

## New Documentation

- **OLLAMA_SETUP.md** - Complete Ollama setup and troubleshooting guide

## Model Options

Recommended for development:
- `llama2` (4GB) - Balanced, good for JSON extraction
- `mistral` (4GB) - Faster alternative
- `phi` (2.6GB) - Minimal resources, still decent quality

See **OLLAMA_SETUP.md** for full model comparison table.

## Key Benefits

| Benefit | Details |
|---------|---------|
| **Free** | No API costs during development |
| **Fast** | Local inference, no network latency |
| **Private** | Data stays on your machine |
| **Offline** | Works without internet |
| **Flexible** | Easy to switch between modes |

## Next Steps

1. **Read** [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for detailed setup
2. **Install** Ollama from https://ollama.ai
3. **Run** `ollama pull llama2`
4. **Debug** using VSCode config or terminal

## Switching Modes

To toggle between cloud and local:
```bash
# Edit .env file
LLM_MODE=local      # Use local Ollama
LLM_MODE=perplexity # Use Perplexity API
```

Or use the VSCode debug dropdown to select different configs.

## Cost Comparison

| Mode | Cost | Setup Time | Speed |
|------|------|-----------|-------|
| Perplexity | $$ | 2 min | Fast |
| Ollama | FREE | 10 min | Very Fast |

Perfect for development testing with Ollama, production with Perplexity!
