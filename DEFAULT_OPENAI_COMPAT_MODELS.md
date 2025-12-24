# Default OpenAI-Compatible Model Configuration

**Purpose:** Standard set of OpenAI-compatible model aliases using Ollama as backend
**Date:** 2025-11-29
**Status:** Production Ready

---

## Overview

This configuration provides drop-in replacements for OpenAI models using local Ollama models. Applications can use standard OpenAI model names (like `gpt-4`, `gpt-3.5-turbo`) and they will be routed to equivalent Ollama models.

### Coverage

| Category | OpenAI Models | Ollama Backend | Status |
|----------|---------------|----------------|--------|
| Chat (Fast) | ✅ gpt-3.5-turbo | qwen3:8b | Available |
| Chat (Quality) | ✅ gpt-4 | qwen3:32b | Available |
| Chat (Premium) | ✅ gpt-4-turbo | llama3.3:70b | Available |
| Vision | ✅ gpt-4-vision-preview | llama3.2-vision:11b | Available |
| Embedding (Large) | ✅ text-embedding-3-large | qwen3-embedding:8b | Available |
| Embedding (Small) | ✅ text-embedding-3-small | nomic-embed-text | Available |
| Reasoning | ✅ o1-preview | deepseek-r1:14b | Available |
| Code | ✅ code-davinci-002 | qwen2.5-coder:14b | Available |
| TTS | ⚠️ tts-1 | N/A | Requires OpenAI |
| STT | ⚠️ whisper-1 | N/A | Requires OpenAI |
| Image Gen | ⚠️ dall-e-3 | N/A | Requires OpenAI |

---

## Model Definitions

### 1. Chat Models (General Purpose)

#### gpt-3.5-turbo → qwen3:8b

**Use case:** Fast responses, general chat, cost-effective

```json
{
  "model_name": "gpt-3.5-turbo",
  "litellm_params": {
    "model": "ollama/qwen3:8b",
    "api_base": "https://olm.mksmad.org",
    "tags": ["compat", "openai-alias", "chat", "fast"]
  },
  "model_info": {
    "litellm_provider": "ollama",
    "mode": "chat",
    "max_tokens": 40960,
    "max_input_tokens": 40960,
    "max_output_tokens": 4096,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "supports_system_messages": true,
    "supports_native_streaming": true,
    "tags": ["compat", "openai-alias", "chat", "fast", "family:qwen3", "size:8.2B"]
  }
}
```

#### gpt-3.5-turbo-16k → qwen3:8b

Alias for extended context (same as gpt-3.5-turbo since qwen3:8b has 40K context)

#### gpt-4 → qwen3:32b

**Use case:** High-quality responses, complex tasks

```json
{
  "model_name": "gpt-4",
  "litellm_params": {
    "model": "ollama/qwen3:32b",
    "api_base": "https://olm.mksmad.org",
    "tags": ["compat", "openai-alias", "chat", "premium"]
  },
  "model_info": {
    "litellm_provider": "ollama",
    "mode": "chat",
    "max_tokens": 262144,
    "max_input_tokens": 262144,
    "max_output_tokens": 16384,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "supports_system_messages": true,
    "supports_native_streaming": true,
    "tags": ["compat", "openai-alias", "chat", "premium", "family:qwen3", "size:32.8B"]
  }
}
```

#### gpt-4-turbo → llama3.3:70b

**Use case:** Best quality, long context

```json
{
  "model_name": "gpt-4-turbo",
  "litellm_params": {
    "model": "ollama/llama3.3:70b",
    "api_base": "https://olm.mksmad.org",
    "tags": ["compat", "openai-alias", "chat", "best-quality"]
  },
  "model_info": {
    "litellm_provider": "ollama",
    "mode": "chat",
    "max_tokens": 128000,
    "max_input_tokens": 128000,
    "max_output_tokens": 16384,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "supports_system_messages": true,
    "supports_native_streaming": true,
    "tags": ["compat", "openai-alias", "chat", "best-quality", "family:llama", "size:70B"]
  }
}
```

#### gpt-4o → qwen3:32b

Alias for gpt-4 (using same backend)

#### gpt-4o-mini → qwen3:8b

Alias for gpt-3.5-turbo (using same backend)

---

### 2. Vision Models

#### gpt-4-vision-preview → llama3.2-vision:11b

**Use case:** Image understanding, multimodal

```json
{
  "model_name": "gpt-4-vision-preview",
  "litellm_params": {
    "model": "ollama/llama3.2-vision:11b",
    "api_base": "https://olm.mksmad.org",
    "tags": ["compat", "openai-alias", "vision"]
  },
  "model_info": {
    "litellm_provider": "ollama",
    "mode": "chat",
    "max_tokens": 131072,
    "max_input_tokens": 131072,
    "max_output_tokens": 16384,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "supports_system_messages": true,
    "supports_vision": true,
    "supports_native_streaming": true,
    "tags": ["compat", "openai-alias", "vision", "family:mllama", "size:10.7B"]
  }
}
```

#### gpt-4-turbo-vision → qwen3-vl:32b

**Use case:** High-quality vision with large context

```json
{
  "model_name": "gpt-4-turbo-vision",
  "litellm_params": {
    "model": "ollama/qwen3-vl:32b",
    "api_base": "https://olm.mksmad.org",
    "tags": ["compat", "openai-alias", "vision", "premium"]
  },
  "model_info": {
    "litellm_provider": "ollama",
    "mode": "chat",
    "max_tokens": 262144,
    "max_input_tokens": 262144,
    "max_output_tokens": 16384,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "supports_system_messages": true,
    "supports_vision": true,
    "supports_native_streaming": true,
    "tags": ["compat", "openai-alias", "vision", "premium", "family:qwen3vl", "size:32B"]
  }
}
```

---

### 3. Embedding Models

#### text-embedding-3-large → qwen3-embedding:8b

**Use case:** High-quality embeddings, RAG, semantic search

```json
{
  "model_name": "text-embedding-3-large",
  "litellm_params": {
    "model": "ollama/qwen3-embedding:8b",
    "api_base": "https://olm.mksmad.org",
    "tags": ["compat", "openai-alias", "embedding"]
  },
  "model_info": {
    "litellm_provider": "ollama",
    "mode": "embedding",
    "max_input_tokens": 40960,
    "output_vector_size": 4096,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "tags": ["compat", "openai-alias", "embedding", "family:qwen3", "size:7.6B"]
  }
}
```

#### text-embedding-3-small → nomic-embed-text

**Use case:** Fast embeddings, lightweight

```json
{
  "model_name": "text-embedding-3-small",
  "litellm_params": {
    "model": "ollama/nomic-embed-text:latest",
    "api_base": "https://olm.mksmad.org",
    "tags": ["compat", "openai-alias", "embedding", "fast"]
  },
  "model_info": {
    "litellm_provider": "ollama",
    "mode": "embedding",
    "max_input_tokens": 2048,
    "output_vector_size": 768,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "tags": ["compat", "openai-alias", "embedding", "fast", "family:nomic-bert", "size:137M"]
  }
}
```

#### text-embedding-ada-002 → nomic-embed-text

Alias for text-embedding-3-small (legacy compatibility)

---

### 4. Reasoning Models

#### o1-preview → deepseek-r1:14b

**Use case:** Complex problem-solving, reasoning

```json
{
  "model_name": "o1-preview",
  "litellm_params": {
    "model": "ollama/deepseek-r1:14b",
    "api_base": "https://olm.mksmad.org",
    "tags": ["compat", "openai-alias", "reasoning"]
  },
  "model_info": {
    "litellm_provider": "ollama",
    "mode": "chat",
    "max_tokens": 131072,
    "max_input_tokens": 131072,
    "max_output_tokens": 16384,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "supports_system_messages": true,
    "supports_reasoning": true,
    "supports_native_streaming": true,
    "tags": ["compat", "openai-alias", "reasoning", "family:qwen2", "size:14B"]
  }
}
```

#### o1-mini → deepseek-r1:7b

**Use case:** Fast reasoning

```json
{
  "model_name": "o1-mini",
  "litellm_params": {
    "model": "ollama/deepseek-r1:7b",
    "api_base": "https://olm.mksmad.org",
    "tags": ["compat", "openai-alias", "reasoning", "fast"]
  },
  "model_info": {
    "litellm_provider": "ollama",
    "mode": "chat",
    "max_tokens": 131072,
    "max_input_tokens": 131072,
    "max_output_tokens": 16384,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "supports_system_messages": true,
    "supports_reasoning": true,
    "supports_native_streaming": true,
    "tags": ["compat", "openai-alias", "reasoning", "fast", "family:qwen2", "size:7.6B"]
  }
}
```

---

### 5. Code Models

#### code-davinci-002 → qwen2.5-coder:14b

**Use case:** Code generation, completion

```json
{
  "model_name": "code-davinci-002",
  "litellm_params": {
    "model": "ollama/qwen2.5-coder:14b",
    "api_base": "https://olm.mksmad.org",
    "tags": ["compat", "openai-alias", "code"]
  },
  "model_info": {
    "litellm_provider": "ollama",
    "mode": "chat",
    "max_tokens": 32768,
    "max_input_tokens": 32768,
    "max_output_tokens": 8192,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "supports_system_messages": true,
    "supports_native_streaming": true,
    "tags": ["compat", "openai-alias", "code", "family:qwen2.5", "size:14B"]
  }
}
```

---

### 6. Models NOT Available in Ollama

These require OpenAI API or alternative services:

#### TTS (Text-to-Speech)

```json
{
  "model_name": "tts-1",
  "litellm_params": {
    "model": "tts-1",
    "api_key": "os.environ/OPENAI_API_KEY"
  },
  "model_info": {
    "litellm_provider": "openai",
    "mode": "audio_speech",
    "input_cost_per_character": 0.000015,
    "tags": ["compat", "openai-real", "tts"]
  }
}
```

**Note:** Requires real OpenAI API key. No Ollama equivalent available.

#### STT (Speech-to-Text)

```json
{
  "model_name": "whisper-1",
  "litellm_params": {
    "model": "whisper-1",
    "api_key": "os.environ/OPENAI_API_KEY"
  },
  "model_info": {
    "litellm_provider": "openai",
    "mode": "audio_transcription",
    "input_cost_per_second": 0.0001,
    "tags": ["compat", "openai-real", "stt"]
  }
}
```

**Note:** Requires real OpenAI API key. No Ollama equivalent available.

#### Image Generation

```json
{
  "model_name": "dall-e-3",
  "litellm_params": {
    "model": "dall-e-3",
    "api_key": "os.environ/OPENAI_API_KEY"
  },
  "model_info": {
    "litellm_provider": "openai",
    "mode": "image_generation",
    "output_cost_per_image": 0.04,
    "tags": ["compat", "openai-real", "image-gen"]
  }
}
```

**Note:** Requires real OpenAI API key. No Ollama equivalent available.

---

## Summary

### Available via Ollama (11 models)

1. ✅ `gpt-3.5-turbo` → qwen3:8b
2. ✅ `gpt-3.5-turbo-16k` → qwen3:8b
3. ✅ `gpt-4` → qwen3:32b
4. ✅ `gpt-4-turbo` → llama3.3:70b
5. ✅ `gpt-4o` → qwen3:32b
6. ✅ `gpt-4o-mini` → qwen3:8b
7. ✅ `gpt-4-vision-preview` → llama3.2-vision:11b
8. ✅ `gpt-4-turbo-vision` → qwen3-vl:32b
9. ✅ `text-embedding-3-large` → qwen3-embedding:8b
10. ✅ `text-embedding-3-small` → nomic-embed-text
11. ✅ `text-embedding-ada-002` → nomic-embed-text
12. ✅ `o1-preview` → deepseek-r1:14b
13. ✅ `o1-mini` → deepseek-r1:7b
14. ✅ `code-davinci-002` → qwen2.5-coder:14b

### Require OpenAI API (3 models)

1. ⚠️ `tts-1` → OpenAI (no Ollama equivalent)
2. ⚠️ `whisper-1` → OpenAI (no Ollama equivalent)
3. ⚠️ `dall-e-3` → OpenAI (no Ollama equivalent)

---

## Installation Script

See `scripts/register_default_compat_models.sh` for automated registration.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-29
**Maintainer:** LiteLLM Companion Project
