# Ollama to LiteLLM Parameter Mapping Guide

**Target Audience:** AI Agents / Developers
**Last Updated:** 2025-11-29
**Models Analyzed:** 11 Ollama models (Chat, Vision, Embedding)

---

## Table of Contents

1. [Overview](#overview)
2. [Complete Field Mapping](#complete-field-mapping)
3. [Model Examples with Full Mappings](#model-examples-with-full-mappings)
4. [Architecture-Specific Mapping Logic](#architecture-specific-mapping-logic)
5. [Extraction Functions for Agents](#extraction-functions-for-agents)
6. [Common Patterns](#common-patterns)

---

## Overview

This document provides comprehensive mapping between Ollama's `/api/show` response and LiteLLM's `model_info` structure. Use this as a reference when implementing automatic model synchronization.

### Key Differences

| Aspect | Ollama | LiteLLM |
|--------|--------|---------|
| API Endpoint | `/api/show` (POST with model name) | `/model/new` (POST), `/model/info` (GET) |
| Context naming | Architecture-specific (e.g., `llama.context_length`) | Standardized (`max_tokens`, `max_input_tokens`) |
| Cost model | Always free (local) | Per-token pricing |
| Model type | Inferred from usage | Explicit `mode` field |

---

## Complete Field Mapping

### Top-Level Ollama Response Structure

```json
{
  "modelfile": "string",           // Modelfile content
  "parameters": "string",          // Model parameters string
  "template": "string",            // Chat template
  "system": "string",              // System prompt (optional)
  "details": {                     // Model metadata
    "parent_model": "string",
    "format": "string",
    "family": "string",
    "families": ["string"],
    "parameter_size": "string",
    "quantization_level": "string"
  },
  "model_info": {                  // Architecture-specific technical details
    "general.architecture": "string",
    "general.parameter_count": int,
    "{arch}.context_length": int,
    "{arch}.embedding_length": int,
    "{arch}.block_count": int,
    "{arch}.attention.head_count": int,
    // ... many more architecture-specific fields
  },
  "capabilities": ["string"],      // Model capabilities
  "license": "string",             // License text
  "modified_at": "string",         // ISO timestamp
  "tensors": [...]                 // Tensor info (usually large)
}
```

### Mapping Table: Ollama → LiteLLM

| Ollama Field | Path | LiteLLM Field | Path | Transform |
|--------------|------|---------------|------|-----------|
| **Basic Metadata** |
| `details.family` | `.details.family` | Tags/metadata | `litellm_params.tags` | Add as `family:{value}` tag |
| `details.format` | `.details.format` | Tags/metadata | `litellm_params.tags` | Add as `format:{value}` tag |
| `details.parameter_size` | `.details.parameter_size` | Tags/metadata | `litellm_params.tags` | Add as `size:{value}` tag |
| `details.quantization_level` | `.details.quantization_level` | Tags/metadata | `litellm_params.tags` | Add as `quant:{value}` tag |
| **Token Limits** |
| `{arch}.context_length` | `.model_info["{arch}.context_length"]` | `max_tokens` | `model_info.max_tokens` | Direct copy |
| `{arch}.context_length` | `.model_info["{arch}.context_length"]` | `max_input_tokens` | `model_info.max_input_tokens` | Direct copy |
| N/A (estimated) | N/A | `max_output_tokens` | `model_info.max_output_tokens` | `min(4096, context_length // 4)` for chat |
| `{arch}.embedding_length` | `.model_info["{arch}.embedding_length"]` | `output_vector_size` | `model_info.output_vector_size` | For embedding models only |
| **Capabilities** |
| Model type inference | Based on family/name | `mode` | `model_info.mode` | See "Mode Detection" below |
| Template exists | `.template` present & non-empty | `supports_system_messages` | `model_info.supports_system_messages` | `true` for chat/vision |
| Model type | Inferred | `supports_vision` | `model_info.supports_vision` | `true` if name contains "vision" or "vl" |
| Model type | Inferred | `supports_reasoning` | `model_info.supports_reasoning` | `true` if name contains "r1" or "qwq" |
| Always true | N/A | `supports_native_streaming` | `model_info.supports_native_streaming` | `true` for chat/vision |
| **Provider** |
| Always "ollama" | N/A | `litellm_provider` | `model_info.litellm_provider` | Always `"ollama"` |
| Model name | Input parameter | `model` | `litellm_params.model` | `"ollama/{model_name}"` |
| **Costs** |
| Always free | N/A | `input_cost_per_token` | `model_info.input_cost_per_token` | Always `0.0` |
| Always free | N/A | `output_cost_per_token` | `model_info.output_cost_per_token` | Always `0.0` |
| **Other Metadata** |
| `{arch}.vocab_size` | `.model_info["{arch}.vocab_size"]` | Custom metadata | User-defined | Informational |
| `{arch}.block_count` | `.model_info["{arch}.block_count"]` | Custom metadata | User-defined | Informational |
| `{arch}.attention.head_count` | `.model_info["{arch}.attention.head_count"]` | Custom metadata | User-defined | Informational |

### Mode Detection Logic

```python
def detect_mode(model_name: str, family: str) -> str:
    """Detect LiteLLM mode from Ollama model"""
    name_lower = model_name.lower()
    family_lower = family.lower()

    # Embedding models
    if any(x in name_lower for x in ["embed", "embedding"]):
        return "embedding"
    if any(x in family_lower for x in ["bert", "nomic-bert"]):
        return "embedding"

    # Vision models
    if any(x in name_lower for x in ["vision", "-vl"]):
        return "chat"  # Vision models use chat mode in LiteLLM

    # Default to chat for everything else
    return "chat"
```

---

## Model Examples with Full Mappings

### Example 1: Chat Model (qwen3:8b)

**Ollama `/api/show` Response (relevant fields):**
```json
{
  "details": {
    "family": "qwen3",
    "format": "gguf",
    "parameter_size": "8.2B",
    "quantization_level": "Q4_K_M"
  },
  "model_info": {
    "general.architecture": "qwen3",
    "qwen3.context_length": 40960,
    "qwen3.embedding_length": 4096,
    "qwen3.block_count": 36,
    "qwen3.attention.head_count": 32,
    "qwen3.attention.head_count_kv": 4
  },
  "template": "{{- if .System }}\n<|im_start|>system\n{{ .System }}<|im_end|>...",
  "parameters": "stop \"<|im_start|>\"\nstop \"<|im_end|>\""
}
```

**LiteLLM `/model/new` Payload:**
```json
{
  "model_name": "local/qwen3-8b",
  "litellm_params": {
    "model": "ollama/qwen3:8b",
    "api_base": "http://ollama:11434",
    "tags": [
      "lupdater",
      "provider:ollama-local",
      "type:chat",
      "family:qwen3",
      "size:8.2B",
      "quant:Q4_K_M"
    ]
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
    "supports_function_calling": false
  }
}
```

### Example 2: Reasoning Model (deepseek-r1:7b)

**Ollama `/api/show` Response (relevant fields):**
```json
{
  "details": {
    "family": "qwen2",
    "format": "gguf",
    "parameter_size": "7.6B",
    "quantization_level": "Q4_K_M"
  },
  "model_info": {
    "general.architecture": "qwen2",
    "qwen2.context_length": 131072,
    "qwen2.embedding_length": 3584,
    "qwen2.block_count": 28
  },
  "template": "{{ .Prompt }}"
}
```

**LiteLLM `/model/new` Payload:**
```json
{
  "model_name": "local/deepseek-r1-7b",
  "litellm_params": {
    "model": "ollama/deepseek-r1:7b",
    "api_base": "http://ollama:11434",
    "tags": [
      "lupdater",
      "provider:ollama-local",
      "type:chat",
      "family:qwen2",
      "size:7.6B",
      "quant:Q4_K_M",
      "capability:reasoning"
    ]
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
    "supports_native_streaming": true,
    "supports_reasoning": true
  }
}
```

### Example 3: Vision Model (qwen3-vl:8b)

**Ollama `/api/show` Response (relevant fields):**
```json
{
  "details": {
    "family": "qwen3vl",
    "format": "gguf",
    "parameter_size": "8.8B",
    "quantization_level": "Q4_K_M"
  },
  "model_info": {
    "general.architecture": "qwen3vl",
    "qwen3vl.context_length": 262144,
    "qwen3vl.embedding_length": 4096,
    "qwen3vl.vision.image_size": 1120,
    "qwen3vl.vision.patch_size": 14,
    "qwen3vl.vision.embedding_length": 1152
  }
}
```

**LiteLLM `/model/new` Payload:**
```json
{
  "model_name": "local/qwen3-vl-8b",
  "litellm_params": {
    "model": "ollama/qwen3-vl:8b",
    "api_base": "http://ollama:11434",
    "tags": [
      "lupdater",
      "provider:ollama-local",
      "type:vision",
      "family:qwen3vl",
      "size:8.8B",
      "quant:Q4_K_M",
      "capability:vision"
    ]
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
    "supports_native_streaming": true
  }
}
```

### Example 4: Embedding Model (nomic-embed-text:latest)

**Ollama `/api/show` Response (relevant fields):**
```json
{
  "details": {
    "family": "nomic-bert",
    "format": "gguf",
    "parameter_size": "137M",
    "quantization_level": "F16"
  },
  "model_info": {
    "general.architecture": "nomic-bert",
    "nomic-bert.context_length": 2048,
    "nomic-bert.embedding_length": 768,
    "nomic-bert.block_count": 12,
    "nomic-bert.pooling_type": 1
  }
}
```

**LiteLLM `/model/new` Payload:**
```json
{
  "model_name": "local/nomic-embed-text",
  "litellm_params": {
    "model": "ollama/nomic-embed-text:latest",
    "api_base": "http://ollama:11434",
    "tags": [
      "lupdater",
      "provider:ollama-local",
      "type:embedding",
      "family:nomic-bert",
      "size:137M",
      "quant:F16"
    ]
  },
  "model_info": {
    "litellm_provider": "ollama",
    "mode": "embedding",
    "max_input_tokens": 2048,
    "output_vector_size": 768,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0
  }
}
```

**Important:** Embedding models:
- Do NOT set `max_output_tokens`
- Do NOT set chat capabilities
- MUST set `output_vector_size` from `embedding_length`

---

## Architecture-Specific Mapping Logic

### Context Length Key by Architecture

Different Ollama architectures use different key patterns in `model_info`. The architecture is found at `model_info["general.architecture"]`.

| Architecture | Context Key | Embedding Key | Examples |
|--------------|-------------|---------------|----------|
| `llama` | `llama.context_length` | `llama.embedding_length` | llama3.2:3b, mistral:7b |
| `qwen2` | `qwen2.context_length` | `qwen2.embedding_length` | deepseek-r1:7b |
| `qwen3` | `qwen3.context_length` | `qwen3.embedding_length` | qwen3:4b, qwen3:8b |
| `qwen3vl` | `qwen3vl.context_length` | `qwen3vl.embedding_length` | qwen3-vl:8b |
| `mllama` | `mllama.context_length` | `mllama.embedding_length` | llama3.2-vision:11b |
| `gemma3` | `gemma3.context_length` | `gemma3.embedding_length` | gemma3:12b |
| `bert` | `bert.context_length` | `bert.embedding_length` | bge-large:latest |
| `nomic-bert` | `nomic-bert.context_length` | `nomic-bert.embedding_length` | nomic-embed-text:latest |

### Python Extraction Function

```python
def get_context_length(ollama_response: dict) -> int | None:
    """Extract context length from Ollama response"""
    model_info = ollama_response.get("model_info", {})
    arch = model_info.get("general.architecture", "unknown")

    # Try architecture-specific key
    key = f"{arch}.context_length"
    if key in model_info:
        return model_info[key]

    # Fallback: search all keys
    for k, v in model_info.items():
        if k.endswith(".context_length") and isinstance(v, int):
            return v

    return None

def get_embedding_length(ollama_response: dict) -> int | None:
    """Extract embedding dimension from Ollama response"""
    model_info = ollama_response.get("model_info", {})
    arch = model_info.get("general.architecture", "unknown")

    # Try architecture-specific key
    key = f"{arch}.embedding_length"
    if key in model_info:
        return model_info[key]

    # Fallback: search all keys
    for k, v in model_info.items():
        if k.endswith(".embedding_length") and isinstance(v, int):
            return v

    return None
```

---

## Extraction Functions for Agents

### Complete Mapping Function (Python)

```python
from typing import Dict, Any, Optional

def map_ollama_to_litellm(
    ollama_response: Dict[str, Any],
    model_name: str,
    api_base: str = "http://ollama:11434",
    prefix: str = "local"
) -> Dict[str, Any]:
    """
    Convert Ollama /api/show response to LiteLLM /model/new payload.

    Args:
        ollama_response: Full response from Ollama /api/show
        model_name: Ollama model name (e.g., "qwen3:8b")
        api_base: Ollama server URL
        prefix: Prefix for model_name in LiteLLM

    Returns:
        LiteLLM /model/new payload
    """
    details = ollama_response.get("details", {})
    model_info = ollama_response.get("model_info", {})

    # Extract basic metadata
    family = details.get("family", "unknown")
    format_type = details.get("format", "gguf")
    param_size = details.get("parameter_size", "unknown")
    quant = details.get("quantization_level", "unknown")

    # Get architecture
    arch = model_info.get("general.architecture", family)

    # Extract context and embedding lengths
    context_length = None
    embedding_length = None

    # Try architecture-specific keys
    context_key = f"{arch}.context_length"
    embedding_key = f"{arch}.embedding_length"

    if context_key in model_info:
        context_length = model_info[context_key]
    if embedding_key in model_info:
        embedding_length = model_info[embedding_key]

    # Detect model type
    mode = detect_mode(model_name, family)
    is_embedding = mode == "embedding"
    is_vision = "vision" in model_name.lower() or "vl" in model_name.lower()
    is_reasoning = "r1" in model_name.lower() or "qwq" in model_name.lower()

    # Build tags
    tags = [
        "lupdater",
        f"provider:ollama",
        f"type:{mode}",
        f"family:{family}",
        f"size:{param_size}",
        f"quant:{quant}"
    ]

    if is_vision:
        tags.append("capability:vision")
    if is_reasoning:
        tags.append("capability:reasoning")

    # Build LiteLLM payload
    payload = {
        "model_name": f"{prefix}/{model_name.replace(':', '-')}",
        "litellm_params": {
            "model": f"ollama/{model_name}",
            "api_base": api_base,
            "tags": tags
        },
        "model_info": {
            "litellm_provider": "ollama",
            "mode": mode,
            "input_cost_per_token": 0.0,
            "output_cost_per_token": 0.0
        }
    }

    # Add token limits
    if context_length:
        if is_embedding:
            payload["model_info"]["max_input_tokens"] = context_length
        else:
            payload["model_info"]["max_tokens"] = context_length
            payload["model_info"]["max_input_tokens"] = context_length
            # Estimate max output tokens
            max_output = min(16384, context_length // 4)
            payload["model_info"]["max_output_tokens"] = max_output

    # Add embedding dimension
    if is_embedding and embedding_length:
        payload["model_info"]["output_vector_size"] = embedding_length

    # Add capabilities
    if not is_embedding:
        payload["model_info"]["supports_system_messages"] = True
        payload["model_info"]["supports_native_streaming"] = True

    if is_vision:
        payload["model_info"]["supports_vision"] = True

    if is_reasoning:
        payload["model_info"]["supports_reasoning"] = True

    return payload

def detect_mode(model_name: str, family: str) -> str:
    """Detect LiteLLM mode from Ollama model"""
    name_lower = model_name.lower()
    family_lower = family.lower()

    # Embedding models
    if any(x in name_lower for x in ["embed", "embedding"]):
        return "embedding"
    if any(x in family_lower for x in ["bert", "nomic-bert"]):
        return "embedding"

    # Everything else is chat (including vision)
    return "chat"
```

### Usage Example

```python
import httpx

# Fetch model info from Ollama
ollama_url = "https://olm.mksmad.org"
model_name = "qwen3:8b"

response = httpx.post(
    f"{ollama_url}/api/show",
    json={"name": model_name}
)
ollama_data = response.json()

# Convert to LiteLLM format
litellm_payload = map_ollama_to_litellm(
    ollama_response=ollama_data,
    model_name=model_name,
    api_base=ollama_url,
    prefix="local"
)

# Register with LiteLLM
litellm_url = "http://localhost:4000"
httpx.post(
    f"{litellm_url}/model/new",
    json=litellm_payload,
    headers={"Authorization": "Bearer sk-1234"}
)
```

---

## Common Patterns

### Pattern 1: Chat Model with Large Context

Models like `qwen3:8b` with 40K+ context:

```python
{
  "max_tokens": 40960,
  "max_input_tokens": 40960,
  "max_output_tokens": 4096  # Conservative estimate
}
```

### Pattern 2: Reasoning Model

Models like `deepseek-r1:7b`:

```python
{
  "mode": "chat",
  "supports_reasoning": true,
  "tags": ["capability:reasoning"]
}
```

### Pattern 3: Vision Model

Models with vision capabilities:

```python
{
  "mode": "chat",  # NOT "vision" - use chat mode
  "supports_vision": true,
  "tags": ["capability:vision"]
}
```

### Pattern 4: Embedding Model

Embedding-specific models:

```python
{
  "mode": "embedding",
  "max_input_tokens": 2048,
  "output_vector_size": 768,
  # DO NOT SET: max_output_tokens, supports_system_messages
}
```

### Pattern 5: Tags for Organization

Recommended tag structure:

```python
{
  "tags": [
    "lupdater",                    # System tag
    "provider:ollama-local",       # Provider identifier
    "type:chat",                   # Model type
    "family:qwen3",                # Architecture family
    "size:8.2B",                   # Parameter count
    "quant:Q4_K_M",                # Quantization level
    "capability:vision"            # Special capabilities (optional)
  ]
}
```

---

## Summary of Key Mappings

### Always Map
1. ✅ `context_length` → `max_tokens` AND `max_input_tokens`
2. ✅ `embedding_length` → `output_vector_size` (embeddings only)
3. ✅ `details.family` → tags
4. ✅ `details.parameter_size` → tags
5. ✅ Set costs to `0.0` (local models)
6. ✅ Set `litellm_provider: "ollama"`

### Conditionally Map
1. ⚠️ `max_output_tokens`: Only for chat/vision (NOT embeddings)
2. ⚠️ `supports_vision`: Only if "vision" or "vl" in name
3. ⚠️ `supports_reasoning`: Only if "r1" or "qwq" in name
4. ⚠️ `mode: "embedding"`: Only for embedding models

### Never Map
1. ❌ `tensors` - Too large, not useful for LiteLLM
2. ❌ `modelfile` - Internal Ollama format
3. ❌ Technical details like `block_count`, `attention.head_count` - Not in LiteLLM standard

---

## Models Analyzed

This mapping is based on analysis of the following Ollama models:

**Chat Models (6):**
- llama3.2:3b (3.2B, Q4_K_M)
- qwen3:4b (4.0B, Q4_K_M)
- qwen3:8b (8.2B, Q4_K_M)
- deepseek-r1:7b (7.6B, Q4_K_M, reasoning)
- mistral:7b (7.2B, Q4_K_M)
- gemma3:12b (12.2B, Q4_K_M)

**Vision Models (2):**
- llama3.2-vision:11b (10.7B, Q4_K_M)
- qwen3-vl:8b (8.8B, Q4_K_M)

**Embedding Models (3):**
- bge-large:latest (334M, F16, 1024-dim)
- nomic-embed-text:latest (137M, F16, 768-dim)
- qwen3-embedding:8b (7.6B, Q4_K_M, 4096-dim)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-29
**Maintainer:** LiteLLM Updater Project
