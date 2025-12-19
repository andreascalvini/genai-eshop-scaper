# Perplexity AI Integration Guide

## Changes Made

The application has been updated to use **Perplexity AI** instead of OpenAI. Here's what was changed:

### 1. Dependencies
- **Removed**: `langchain-openai>=0.0.1` (no longer needed)
- The `ChatOpenAI` class from LangChain supports any OpenAI-compatible API endpoint

### 2. Configuration (`src/config.py`)
- **Changed**: `openai_api_key` → `perplexity_api_key`
- Configuration now expects `PERPLEXITY_API_KEY` environment variable

### 3. Product Extraction Agent (`src/agents/product_extraction.py`)
- **Model**: Changed from `gpt-3.5-turbo` to `llama-2-70b-chat`
- **API Endpoint**: Uses Perplexity's API at `https://api.perplexity.ai`
- **API Key**: Reads from `PERPLEXITY_API_KEY` environment variable or config file

## Setup Instructions

### 1. Get Your Perplexity API Key
- Visit: https://www.perplexity.ai/
- Sign up or log in
- Generate an API key from your account settings

### 2. Set Environment Variable
```bash
# Option 1: Set in terminal
export PERPLEXITY_API_KEY="your_api_key_here"

# Option 2: Add to .env file
echo "PERPLEXITY_API_KEY=your_api_key_here" > .env
```

### 3. Available Models
Perplexity offers these models:
- `llama-2-70b-chat` (default - good balance of speed and quality)
- `llama-2-13b-chat` (faster, smaller)
- `mistral-7b-instruct`
- `pplx-7b-online` (can search the web)
- `pplx-70b-online` (can search the web, higher quality)

To use a different model, update `src/agents/product_extraction.py`:
```python
self.llm = ChatOpenAI(
    model="pplx-70b-online",  # Change to another model
    temperature=0,
    api_key=api_key,
    base_url="https://api.perplexity.ai"
)
```

## Pricing
Perplexity AI is typically more affordable than OpenAI:
- Llama-2 models: ~$0.0005 per 1k tokens
- Online models: ~$0.005-0.01 per 1k tokens

## Testing
To verify the integration works:

```bash
# Run with your API key
PERPLEXITY_API_KEY="your_key" python src/main.py https://formulaiozzi.com
```

## Debugging
If you encounter issues:

1. **API Key not found**: Ensure `PERPLEXITY_API_KEY` is set
2. **Model not available**: Check available models in Perplexity docs
3. **Rate limiting**: Check your Perplexity account usage
4. **Connection errors**: Verify internet connection and firewall rules

## Alternative Models for Product Extraction
The `llama-2-70b-chat` model is suitable for JSON extraction. If you need:
- **Better quality**: Use `pplx-70b-online`
- **Faster processing**: Use `llama-2-13b-chat`
- **Web search**: Use `pplx-70b-online` or `pplx-7b-online`

## Configuration Files Updated
- ✅ `pyproject.toml` - Removed langchain-openai dependency
- ✅ `src/config.py` - Changed config key name
- ✅ `src/agents/product_extraction.py` - Updated to use Perplexity endpoint
- ✅ `.env.example` - Updated with Perplexity API key instructions
