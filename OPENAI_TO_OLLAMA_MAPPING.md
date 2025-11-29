# OpenAI → Ollama Model Mapping Guide

**Date:** 2025-11-29
**Purpose:** Recommended mappings from OpenAI models to functionally equivalent Ollama models
**Target Audience:** Developers, System Architects

---

## Table of Contents

1. [Overview](#overview)
2. [Chat Model Mappings](#chat-model-mappings)
3. [Vision Model Mappings](#vision-model-mappings)
4. [Embedding Model Mappings](#embedding-model-mappings)
5. [Reasoning Model Mappings](#reasoning-model-mappings)
6. [Quick Reference Table](#quick-reference-table)
7. [Migration Guide](#migration-guide)

---

## Overview

This guide provides recommended mappings between OpenAI models and their Ollama equivalents based on:
- **Capabilities**: Chat, vision, embedding, reasoning
- **Performance tier**: Context window, parameter count
- **Use case**: General chat, coding, analysis, etc.

### Why Map OpenAI to Ollama?

- **Cost savings**: Ollama models are free and run locally
- **Privacy**: Keep data on-premises
- **Offline capability**: No internet dependency
- **Customization**: Fine-tune and modify as needed

### Mapping Methodology

Models are matched based on:
1. **Primary capability** (chat, vision, embedding)
2. **Context window size** (similar capacity)
3. **Parameter count** (performance tier)
4. **Specific features** (vision, function calling, reasoning)

---

## Chat Model Mappings

### GPT-4 Turbo / GPT-4o Series

**Use case:** High-performance chat, complex reasoning, long context

| OpenAI Model | Context | Parameters | → | Ollama Model | Context | Parameters | Notes |
|--------------|---------|------------|---|--------------|---------|------------|-------|
| **gpt-4-turbo** | 128K | Unknown | → | **qwen3:32b** | 262K | 32.8B | Best overall match |
| **gpt-4o** | 128K | ~200B | → | **qwen3:30b** | 262K | 30.5B | Excellent for reasoning |
| **gpt-4o** | 128K | ~200B | → | **llama3.3:70b** | 128K | 70B | Highest quality, slow |
| **gpt-4o-mini** | 128K | ~8B | → | **qwen3:8b** | 41K | 8.2B | Fast, good quality |
| **gpt-4o-mini** | 128K | ~8B | → | **llama3.1:8b** | 128K | 8B | Stable, well-tested |

**Recommendation:**
- For **best quality**: `llama3.3:70b` or `qwen3:32b`
- For **speed/efficiency**: `qwen3:8b` or `llama3.1:8b`
- For **long context**: `qwen3:30b` (262K context)

### GPT-4 (Original) / GPT-4-32K

**Use case:** Complex tasks, high accuracy

| OpenAI Model | Context | → | Ollama Model | Context | Parameters | Notes |
|--------------|---------|---|--------------|---------|------------|-------|
| **gpt-4** | 8K | → | **mistral:7b** | 33K | 7.2B | Good for general use |
| **gpt-4** | 8K | → | **llama3.1:8b** | 128K | 8B | Better context window |
| **gpt-4-32k** | 32K | → | **qwen3:14b** | 262K | 14B | Larger context + size |

### GPT-3.5 Turbo

**Use case:** Fast responses, general chat, simple tasks

| OpenAI Model | Context | → | Ollama Model | Context | Parameters | Notes |
|--------------|---------|---|--------------|---------|------------|-------|
| **gpt-3.5-turbo** | 16K | → | **qwen3:4b** | 262K | 4.0B | Fast, huge context |
| **gpt-3.5-turbo** | 16K | → | **llama3.2:3b** | 128K | 3.2B | Lightweight, efficient |
| **gpt-3.5-turbo-16k** | 16K | → | **qwen3:8b** | 41K | 8.2B | Better quality |

**Recommendation:**
- For **speed**: `llama3.2:3b`
- For **quality**: `qwen3:8b`
- For **long context**: `qwen3:4b`

### Specialized Chat Models

| OpenAI Model | → | Ollama Model | Specialization |
|--------------|---|--------------|----------------|
| **gpt-3.5-turbo-instruct** | → | **qwen2.5-coder:7b** | Instruction following |
| **code-davinci-002** | → | **qwen2.5-coder:14b** | Code generation |
| **text-davinci-003** | → | **qwen3:14b** | High-quality text |

---

## Vision Model Mappings

**Use case:** Image understanding, multimodal tasks

| OpenAI Model | Context | → | Ollama Model | Context | Vision Capability | Notes |
|--------------|---------|---|--------------|---------|-------------------|-------|
| **gpt-4-vision-preview** | 128K | → | **llama3.2-vision:11b** | 128K | ✓ Images | Stable, well-tested |
| **gpt-4o** (vision) | 128K | → | **qwen3-vl:8b** | 262K | ✓ Images | Huge context |
| **gpt-4o** (vision) | 128K | → | **qwen3-vl:32b** | 262K | ✓ Images | Highest quality |
| **gpt-4o-mini** (vision) | 128K | → | **qwen3-vl:4b** | 262K | ✓ Images | Fast, efficient |

**Recommendation:**
- For **general vision**: `llama3.2-vision:11b`
- For **high quality**: `qwen3-vl:32b`
- For **speed**: `qwen3-vl:4b`

### Vision Features Comparison

| Feature | llama3.2-vision:11b | qwen3-vl:8b | qwen3-vl:32b |
|---------|---------------------|-------------|--------------|
| Image understanding | ✓ Excellent | ✓ Excellent | ✓ Best |
| Context window | 128K | 262K | 262K |
| Speed | Fast | Fast | Moderate |
| Quality | High | High | Highest |

---

## Embedding Model Mappings

**Use case:** Semantic search, RAG, similarity matching

| OpenAI Model | Dimensions | → | Ollama Model | Dimensions | Parameters | Notes |
|--------------|------------|---|--------------|------------|------------|-------|
| **text-embedding-3-large** | 3072 | → | **qwen3-embedding:8b** | 4096 | 7.6B | Highest quality |
| **text-embedding-3-small** | 1536 | → | **nomic-embed-text** | 768 | 137M | Fast, lightweight |
| **text-embedding-ada-002** | 1536 | → | **bge-large** | 1024 | 334M | Good quality |
| **text-embedding-ada-002** | 1536 | → | **mxbai-embed-large** | Unknown | Unknown | Alternative |

**Recommendation:**
- For **best quality**: `qwen3-embedding:8b`
- For **speed/efficiency**: `nomic-embed-text`
- For **balanced**: `bge-large`

### Embedding Use Cases

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| RAG with long documents | `qwen3-embedding:8b` | Large dimensions, high quality |
| Fast search/lookup | `nomic-embed-text` | Lightweight, very fast |
| Multilingual | `bge-large` | Good multilingual support |
| General purpose | `mxbai-embed-large` | Balanced performance |

---

## Reasoning Model Mappings

**Use case:** Complex problem-solving, step-by-step reasoning

| OpenAI Model | Context | → | Ollama Model | Context | Parameters | Notes |
|--------------|---------|---|--------------|---------|------------|-------|
| **o1-preview** | 128K | → | **deepseek-r1:14b** | 128K | 14B | Reasoning-focused |
| **o1-mini** | 128K | → | **deepseek-r1:7b** | 128K | 7.6B | Smaller, faster |
| **o4-mini** | 200K | → | **deepseek-r1:32b** | 128K | 32.8B | Highest capability |
| **o4-mini** | 200K | → | **qwq:32b** | 128K | 32.8B | Alternative |

**Recommendation:**
- For **best reasoning**: `deepseek-r1:32b` or `qwq:32b`
- For **balanced**: `deepseek-r1:14b`
- For **speed**: `deepseek-r1:7b`

### Reasoning Capabilities

DeepSeek-R1 and QwQ models excel at:
- Mathematical problem-solving
- Step-by-step reasoning
- Complex logical tasks
- Code debugging and analysis

---

## Quick Reference Table

### By Use Case

| Use Case | OpenAI Model | Ollama Equivalent | Why |
|----------|--------------|-------------------|-----|
| **General chat** | gpt-3.5-turbo | `qwen3:8b` | Fast, good quality |
| **High-quality chat** | gpt-4o | `qwen3:32b` | Best overall |
| **Long context** | gpt-4-turbo | `qwen3:30b` | 262K context |
| **Fast responses** | gpt-3.5-turbo | `llama3.2:3b` | Lightweight |
| **Vision understanding** | gpt-4-vision | `llama3.2-vision:11b` | Stable, tested |
| **Vision + long context** | gpt-4o (vision) | `qwen3-vl:8b` | 262K context |
| **Embeddings (quality)** | text-embedding-3-large | `qwen3-embedding:8b` | Highest quality |
| **Embeddings (speed)** | text-embedding-3-small | `nomic-embed-text` | Very fast |
| **Reasoning** | o1-preview | `deepseek-r1:14b` | Reasoning-focused |
| **Code generation** | gpt-4 | `qwen2.5-coder:14b` | Code-optimized |

### By Model Size (Parameters)

| Size Tier | OpenAI Equivalent | Ollama Models | Best For |
|-----------|-------------------|---------------|----------|
| **Small (1-4B)** | gpt-3.5-turbo | `llama3.2:3b`, `qwen3:4b` | Speed, low resource |
| **Medium (7-14B)** | gpt-4 | `qwen3:8b`, `deepseek-r1:14b`, `mistral:7b` | Balanced |
| **Large (30-70B)** | gpt-4-turbo | `qwen3:32b`, `llama3.3:70b` | Quality |

### By Context Window

| Context Need | OpenAI Models | Ollama Models |
|--------------|---------------|---------------|
| **< 16K** | gpt-3.5-turbo (16K) | `mistral:7b` (33K) |
| **16K - 32K** | gpt-3.5-turbo-16k | `qwen3:8b` (41K) |
| **32K - 128K** | gpt-4, gpt-4-turbo | `llama3.1:8b` (128K), `qwen3:14b` (262K) |
| **> 128K** | gpt-4-turbo (128K) | `qwen3:30b` (262K), `qwen3:4b` (262K) |

---

## Migration Guide

### Step 1: Identify Your Current Usage

```python
# Example: Current OpenAI usage
import openai

response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Step 2: Choose Equivalent Ollama Model

Based on the mappings above:
- `gpt-4o` → `qwen3:32b` (best quality)
- `gpt-4o` → `qwen3:8b` (speed/efficiency)

### Step 3: Update to Ollama

```python
# Using Ollama with OpenAI-compatible API
import openai

# Point to Ollama server
openai.api_base = "http://localhost:11434/v1"
openai.api_key = "dummy"  # Ollama doesn't need a key

response = openai.ChatCompletion.create(
    model="qwen3:8b",  # Ollama model
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Step 4: Register with LiteLLM (Recommended)

For centralized model management:

```bash
curl -X POST http://localhost:4000/model/new \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "gpt-4o-replacement",
    "litellm_params": {
      "model": "ollama/qwen3:8b",
      "api_base": "http://ollama:11434",
      "tags": ["local", "replacement"]
    },
    "model_info": {
      "litellm_provider": "ollama",
      "mode": "chat",
      "max_tokens": 40960,
      "input_cost_per_token": 0.0,
      "output_cost_per_token": 0.0
    }
  }'
```

Then use through LiteLLM:

```python
# Use LiteLLM proxy
openai.api_base = "http://localhost:4000"
openai.api_key = "sk-1234"

response = openai.ChatCompletion.create(
    model="gpt-4o-replacement",  # Your registered name
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

## Performance Considerations

### Latency

| Model Size | Relative Speed | Use When |
|------------|----------------|----------|
| 3-4B | 🟢 Very Fast | Real-time chat, high throughput |
| 7-8B | 🟢 Fast | General use, balanced |
| 14B | 🟡 Moderate | Quality matters more than speed |
| 30-32B | 🟠 Slow | Highest quality needed |
| 70B | 🔴 Very Slow | Offline processing, best quality |

### Resource Requirements

| Model Size | RAM (Q4) | RAM (FP16) | VRAM (GPU) |
|------------|----------|------------|------------|
| 3B | ~2GB | ~6GB | ~4GB |
| 7-8B | ~4GB | ~14GB | ~8GB |
| 14B | ~8GB | ~28GB | ~16GB |
| 32B | ~16GB | ~64GB | ~32GB |
| 70B | ~35GB | ~140GB | ~70GB |

*Q4 = 4-bit quantization (default for most Ollama models)*

---

## Best Practices

### 1. Start with Smaller Models

Don't assume you need the largest model. Try this progression:
1. Start: `llama3.2:3b` or `qwen3:4b`
2. If quality insufficient: `qwen3:8b`
3. If still insufficient: `qwen3:14b`
4. Only if necessary: `qwen3:32b` or `llama3.3:70b`

### 2. Match Context Needs

- Short conversations (< 4K tokens): Any model works
- Medium context (4-32K): `qwen3:8b`, `llama3.1:8b`
- Long context (> 32K): `qwen3` series (262K context)

### 3. Specialized Tasks

- **Code**: `qwen2.5-coder` series
- **Vision**: `llama3.2-vision:11b` or `qwen3-vl` series
- **Reasoning**: `deepseek-r1` series
- **Embeddings**: `qwen3-embedding:8b` or `nomic-embed-text`

### 4. Testing Strategy

```python
# Test multiple models to find best fit
models_to_test = [
    "llama3.2:3b",      # Baseline
    "qwen3:8b",         # Balanced
    "qwen3:14b",        # High quality
]

for model in models_to_test:
    # Run your test queries
    # Measure: quality, latency, resource usage
    # Choose best trade-off
    pass
```

---

## Limitations and Differences

### What Ollama Models Can't Do (vs OpenAI)

1. **No native function calling** (most models)
   - Workaround: Use LiteLLM's function calling adapter
2. **No guaranteed availability** (self-hosted)
   - Mitigation: Use LiteLLM for fallback to OpenAI
3. **Variable quality** depending on quantization
   - Solution: Test different quantizations (Q4 vs Q8 vs FP16)

### What Ollama Models CAN Do Better

1. **Privacy**: Complete data privacy (local execution)
2. **Cost**: $0 after initial setup
3. **Customization**: Fine-tune, modify prompts, adjust parameters
4. **Offline**: No internet dependency
5. **No rate limits**: Limited only by your hardware

---

## Summary Recommendations

### Top 5 Ollama Models for OpenAI Replacement

1. **`qwen3:8b`** - Best all-around replacement for GPT-3.5/GPT-4o-mini
   - Fast, good quality, large context (41K)
2. **`qwen3:32b`** - Best replacement for GPT-4o/GPT-4-turbo
   - High quality, 262K context
3. **`llama3.2-vision:11b`** - Best vision model
   - Stable, well-tested, good quality
4. **`qwen3-embedding:8b`** - Best embeddings
   - Highest quality, 4096 dimensions
5. **`deepseek-r1:14b`** - Best reasoning
   - Complex problem-solving, step-by-step thinking

---

**Document Version:** 1.0
**Last Updated:** 2025-11-29
**Maintainer:** LiteLLM Updater Project
