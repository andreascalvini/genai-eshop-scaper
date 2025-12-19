# Local LLM Setup with Ollama

This guide shows how to set up and use free local Llama models via Ollama for debugging without consuming API credits.

## What is Ollama?

**Ollama** is a tool that lets you run large language models locally on your machine. It's:
- ✅ Free to use
- ✅ No API calls needed
- ✅ Fast for development/debugging
- ✅ Supports Llama 2, Mistral, and other models
- ✅ Easy to install and use

## Installation

### macOS
```bash
# Download from: https://ollama.ai
# Or use Homebrew:
brew install ollama
```

### Linux
```bash
curl https://ollama.ai/install.sh | sh
```

### Windows
```bash
# Download from: https://ollama.ai/download/windows
# Run the installer
```

## Getting Started

### 1. Start Ollama Server
```bash
ollama serve
```
This starts the Ollama service on `http://localhost:11434` (default).

### 2. Download a Model (in another terminal)
```bash
# Download Llama 2 (4GB model, good balance of speed and quality)
ollama pull llama2

# Alternative models:
ollama pull mistral          # Faster, 4.1GB
ollama pull neural-chat      # Optimized for chat, 4.1GB
ollama pull dolphin-mixtral  # High quality, 26GB (requires more VRAM)
```

### 3. Test Ollama is Working
```bash
ollama run llama2
# Type something and chat with the model locally!
# Type 'exit' to quit
```

## Using with the Scraper

### Option 1: Use Debug Configuration (Easiest)

1. Start Ollama server: `ollama serve`
2. Download a model: `ollama pull llama2`
3. In VSCode, select the **"Debug with Local Llama (Ollama)"** launch configuration
4. Press **F5** to start debugging

### Option 2: Set Environment Variables

Add to your `.env` file:
```env
LLM_MODE=local
OLLAMA_MODEL_NAME=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

Then run:
```bash
python src/main.py https://formulaiozzi.com
```

### Option 3: Command Line
```bash
LLM_MODE=local python src/main.py https://formulaiozzi.com
```

## Available Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `llama2` | 4GB | Medium | Good | Default, balanced |
| `mistral` | 4.1GB | Fast | Good | Quick tests |
| `neural-chat` | 4.1GB | Fast | Good | Chat-optimized |
| `dolphin-mixtral` | 26GB | Slow | Excellent | Best quality (high VRAM) |
| `phi` | 2.6GB | Very Fast | Medium | Minimal resources |

### How to Use Different Models
```bash
# Pull a different model
ollama pull mistral

# Use it in .env
OLLAMA_MODEL_NAME=mistral
```

## System Requirements

### Minimum
- **RAM**: 8GB (for llama2)
- **Disk**: 5GB (for one model)
- **CPU**: Multi-core processor

### Recommended
- **RAM**: 16GB
- **GPU**: NVIDIA (with CUDA) or Apple Silicon - for faster inference
- **Disk**: 10GB+ for multiple models

### GPU Support
Ollama automatically uses GPU if available:
- **NVIDIA**: Install CUDA toolkit
- **Apple Silicon**: Automatic
- **AMD**: Experimental support

## Troubleshooting

### "Connection refused" error
```bash
# Make sure Ollama server is running
ollama serve

# Check if running on port 11434
lsof -i :11434
```

### Model not found
```bash
# List installed models
ollama list

# Pull the model first
ollama pull llama2
```

### Slow responses
- Use a smaller model: `mistral` or `phi`
- Ensure you have enough RAM
- Enable GPU acceleration if available

### Memory issues
```bash
# Use a smaller model
OLLAMA_MODEL_NAME=phi

# Or limit memory usage
OLLAMA_NUM_PARALLEL=1
```

## Performance Tips

### 1. Use Smaller Models for Quick Tests
```bash
# Fast feedback during development
OLLAMA_MODEL_NAME=phi
```

### 2. Pre-load Model
```bash
# Run before your scraper to load model into memory
ollama run llama2 ""
```

### 3. Adjust Number of Parallel Requests
```bash
export OLLAMA_NUM_PARALLEL=1
```

## Comparing Modes

| Feature | Perplexity (Cloud) | Ollama (Local) |
|---------|-------------------|----------------|
| Cost | Paid API | Free |
| Speed | Fast (network dependent) | Very Fast (local) |
| Requires API Key | ✅ Yes | ❌ No |
| Privacy | Sent to cloud | Local only |
| Model Selection | Limited | Many options |
| Quality | High (GPT-powered) | Good (Llama/Mistral) |
| Setup | Simple | Slightly more setup |

## Switching Between Modes

To switch from Ollama back to Perplexity:
```bash
# In .env or command line
LLM_MODE=perplexity
PERPLEXITY_API_KEY=your_key
```

Or use the VSCode debug config: **"Debug with Formula Iozzi"**

## Advanced Usage

### Run Specific Model Version
```bash
ollama pull llama2:13b  # 13B parameter version
```

### Custom Model Configuration
```bash
# Create custom Modelfile
cat > Modelfile << EOF
FROM llama2
PARAMETER temperature 0.1
PARAMETER top_k 40
EOF

ollama create mymodel -f Modelfile
```

### Monitor Ollama
```bash
# See running models
curl http://localhost:11434/api/tags

# Check system status
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "test",
  "stream": false
}'
```

## Additional Resources

- **Ollama Documentation**: https://github.com/ollama/ollama
- **Model Library**: https://ollama.ai/library
- **Community Models**: https://github.com/ollama/ollama/blob/main/docs/modelfile.md

## Quick Start Script

Save as `start_local_debug.sh`:
```bash
#!/bin/bash

# Start Ollama in background
echo "Starting Ollama..."
ollama serve &
OLLAMA_PID=$!

# Wait for server
sleep 2

# Pull model if not exists
echo "Ensuring llama2 model is available..."
ollama pull llama2

# Start scraper in debug mode
echo "Starting scraper with local LLM..."
LLM_MODE=local python src/main.py https://formulaiozzi.com

# Cleanup on exit
trap "kill $OLLAMA_PID" EXIT
```

Run with: `chmod +x start_local_debug.sh && ./start_local_debug.sh`
