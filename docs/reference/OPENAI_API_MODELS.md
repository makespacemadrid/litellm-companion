# OpenAI API Models Configuration

**Date:** 2025-11-29
**Purpose:** Guide for registering OpenAI-exclusive models (TTS, STT, Image Generation)

---

## Overview

The following model types are NOT available in Ollama and require a real OpenAI API key:

1. **TTS (Text-to-Speech)**: `tts-1`, `tts-1-hd`
2. **STT (Speech-to-Text)**: `whisper-1`
3. **Image Generation**: `dall-e-2`, `dall-e-3`

These models must be registered separately with your OpenAI API key.

---

## Prerequisites

You need a valid OpenAI API key. Get one from: https://platform.openai.com/api-keys

Set it as an environment variable:
```bash
export OPENAI_API_KEY=sk-your-actual-openai-key-here
```

---

## Registration Commands

### TTS Models

#### tts-1 (Standard Quality)

```bash
curl -X POST http://localhost:4000/model/new \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "tts-1",
    "litellm_params": {
      "model": "tts-1",
      "api_key": "os.environ/OPENAI_API_KEY",
      "tags": ["compat", "openai-real", "tts"]
    },
    "model_info": {
      "litellm_provider": "openai",
      "mode": "audio_speech",
      "input_cost_per_character": 0.000015,
      "tags": ["compat", "openai-real", "tts"]
    }
  }'
```

#### tts-1-hd (High Quality)

```bash
curl -X POST http://localhost:4000/model/new \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "tts-1-hd",
    "litellm_params": {
      "model": "tts-1-hd",
      "api_key": "os.environ/OPENAI_API_KEY",
      "tags": ["compat", "openai-real", "tts", "hd"]
    },
    "model_info": {
      "litellm_provider": "openai",
      "mode": "audio_speech",
      "input_cost_per_character": 0.00003,
      "tags": ["compat", "openai-real", "tts", "hd"]
    }
  }'
```

### STT Models

#### whisper-1 (Speech-to-Text)

```bash
curl -X POST http://localhost:4000/model/new \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "whisper-1",
    "litellm_params": {
      "model": "whisper-1",
      "api_key": "os.environ/OPENAI_API_KEY",
      "tags": ["compat", "openai-real", "stt"]
    },
    "model_info": {
      "litellm_provider": "openai",
      "mode": "audio_transcription",
      "input_cost_per_second": 0.0001,
      "tags": ["compat", "openai-real", "stt"]
    }
  }'
```

### Image Generation Models

#### dall-e-2

```bash
curl -X POST http://localhost:4000/model/new \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "dall-e-2",
    "litellm_params": {
      "model": "dall-e-2",
      "api_key": "os.environ/OPENAI_API_KEY",
      "tags": ["compat", "openai-real", "image-gen"]
    },
    "model_info": {
      "litellm_provider": "openai",
      "mode": "image_generation",
      "output_cost_per_image": 0.02,
      "tags": ["compat", "openai-real", "image-gen"]
    }
  }'
```

#### dall-e-3

```bash
curl -X POST http://localhost:4000/model/new \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "dall-e-3",
    "litellm_params": {
      "model": "dall-e-3",
      "api_key": "os.environ/OPENAI_API_KEY",
      "tags": ["compat", "openai-real", "image-gen", "hd"]
    },
    "model_info": {
      "litellm_provider": "openai",
      "mode": "image_generation",
      "output_cost_per_image": 0.04,
      "tags": ["compat", "openai-real", "image-gen", "hd"]
    }
  }'
```

---

## Automated Registration Script

Create a script to register all OpenAI models at once:

```bash
#!/bin/bash
# scripts/register_openai_models.sh

if [ -z "$OPENAI_API_KEY" ]; then
  echo "Error: OPENAI_API_KEY environment variable not set"
  echo "Get your key from: https://platform.openai.com/api-keys"
  exit 1
fi

LITELLM_URL="http://localhost:4000"
LITELLM_KEY="sk-1234"

echo "Registering OpenAI models to LiteLLM..."

# TTS Models
echo "Registering tts-1..."
curl -s -X POST $LITELLM_URL/model/new \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "tts-1",
    "litellm_params": {
      "model": "tts-1",
      "api_key": "os.environ/OPENAI_API_KEY",
      "tags": ["compat", "openai-real", "tts"]
    },
    "model_info": {
      "litellm_provider": "openai",
      "mode": "audio_speech",
      "input_cost_per_character": 0.000015,
      "tags": ["compat", "openai-real", "tts"]
    }
  }' > /dev/null && echo "✓ tts-1 registered" || echo "✗ tts-1 failed"

echo "Registering tts-1-hd..."
curl -s -X POST $LITELLM_URL/model/new \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "tts-1-hd",
    "litellm_params": {
      "model": "tts-1-hd",
      "api_key": "os.environ/OPENAI_API_KEY",
      "tags": ["compat", "openai-real", "tts", "hd"]
    },
    "model_info": {
      "litellm_provider": "openai",
      "mode": "audio_speech",
      "input_cost_per_character": 0.00003,
      "tags": ["compat", "openai-real", "tts", "hd"]
    }
  }' > /dev/null && echo "✓ tts-1-hd registered" || echo "✗ tts-1-hd failed"

# STT Models
echo "Registering whisper-1..."
curl -s -X POST $LITELLM_URL/model/new \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "whisper-1",
    "litellm_params": {
      "model": "whisper-1",
      "api_key": "os.environ/OPENAI_API_KEY",
      "tags": ["compat", "openai-real", "stt"]
    },
    "model_info": {
      "litellm_provider": "openai",
      "mode": "audio_transcription",
      "input_cost_per_second": 0.0001,
      "tags": ["compat", "openai-real", "stt"]
    }
  }' > /dev/null && echo "✓ whisper-1 registered" || echo "✗ whisper-1 failed"

# Image Generation Models
echo "Registering dall-e-2..."
curl -s -X POST $LITELLM_URL/model/new \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "dall-e-2",
    "litellm_params": {
      "model": "dall-e-2",
      "api_key": "os.environ/OPENAI_API_KEY",
      "tags": ["compat", "openai-real", "image-gen"]
    },
    "model_info": {
      "litellm_provider": "openai",
      "mode": "image_generation",
      "output_cost_per_image": 0.02,
      "tags": ["compat", "openai-real", "image-gen"]
    }
  }' > /dev/null && echo "✓ dall-e-2 registered" || echo "✗ dall-e-2 failed"

echo "Registering dall-e-3..."
curl -s -X POST $LITELLM_URL/model/new \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "dall-e-3",
    "litellm_params": {
      "model": "dall-e-3",
      "api_key": "os.environ/OPENAI_API_KEY",
      "tags": ["compat", "openai-real", "image-gen", "hd"]
    },
    "model_info": {
      "litellm_provider": "openai",
      "mode": "image_generation",
      "output_cost_per_image": 0.04,
      "tags": ["compat", "openai-real", "image-gen", "hd"]
    }
  }' > /dev/null && echo "✓ dall-e-3 registered" || echo "✗ dall-e-3 failed"

echo ""
echo "Done! All OpenAI models registered."
echo "Note: These models require OPENAI_API_KEY to be set in your environment."
```

Make it executable:
```bash
chmod +x scripts/register_openai_models.sh
```

Run it:
```bash
export OPENAI_API_KEY=sk-your-key-here
./scripts/register_openai_models.sh
```

---

## Important Notes

1. **API Key Security**: Never commit your API key to version control
2. **Environment Variable**: LiteLLM will read from `os.environ/OPENAI_API_KEY`
3. **Costs**: These models have real costs per usage (see OpenAI pricing)
4. **No Ollama Alternative**: These model types cannot run locally via Ollama
5. **Optional**: Only register these if you need TTS/STT/Image features

---

## Verification

Check registered models:
```bash
curl -H "Authorization: Bearer sk-1234" http://localhost:4000/model/info | jq '.data[] | select(.tags[] | contains("openai-real")) | {model_name, mode: .model_info.mode}'
```

Expected output:
```json
{
  "model_name": "tts-1",
  "mode": "audio_speech"
}
{
  "model_name": "tts-1-hd",
  "mode": "audio_speech"
}
{
  "model_name": "whisper-1",
  "mode": "audio_transcription"
}
{
  "model_name": "dall-e-2",
  "mode": "image_generation"
}
{
  "model_name": "dall-e-3",
  "mode": "image_generation"
}
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-29
**Maintainer:** LiteLLM Companion Project
