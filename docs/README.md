# Documentation Index

This directory contains user guides, technical references, and development documentation for LiteLLM Companion.

## 📖 User Guides

### Getting Started
- [Main README](../README.md) - Project overview, quick start, and configuration
- [MODEL_STATISTICS](../MODEL_STATISTICS.md) - Model coverage and OpenAI API statistics

### Setup & Migration
- [MIGRATION.md](guides/MIGRATION.md) - Upgrade guide from previous versions
- [FIM_CODE_COMPLETION.md](guides/FIM_CODE_COMPLETION.md) - Fill-in-the-Middle setup for code editors
- [COMPAT_MAPPING_PROPOSAL.md](guides/COMPAT_MAPPING_PROPOSAL.md) - Model mapping strategies and recommendations

## 🔧 Technical Reference

### API Documentation
- [ollama-api.md](reference/ollama-api.md) - Ollama API reference
- [LITELLM_MODEL_PARAMETERS.md](reference/LITELLM_MODEL_PARAMETERS.md) - LiteLLM model parameter reference
- [OPENAI_API_MODELS.md](reference/OPENAI_API_MODELS.md) - OpenAI API model list

### Model Mappings
- [OLLAMA_TO_LITELLM_MAPPING.md](reference/OLLAMA_TO_LITELLM_MAPPING.md) - Ollama → LiteLLM parameter mapping
- [OPENAI_TO_OLLAMA_MAPPING.md](reference/OPENAI_TO_OLLAMA_MAPPING.md) - OpenAI → Ollama model mapping
- [DEFAULT_OPENAI_COMPAT_MODELS.md](reference/DEFAULT_OPENAI_COMPAT_MODELS.md) - Default OpenAI compatibility models

## 🛠️ Developer Documentation

### Architecture & Contributing
- [CLAUDE.md](../CLAUDE.md) - Development guide, architecture overview, and coding patterns
- See main README for contribution guidelines

## 📂 Directory Structure

```
docs/
├── README.md (this file)
├── guides/
│   ├── MIGRATION.md
│   ├── FIM_CODE_COMPLETION.md
│   └── COMPAT_MAPPING_PROPOSAL.md
└── reference/
    ├── ollama-api.md
    ├── LITELLM_MODEL_PARAMETERS.md
    ├── OPENAI_API_MODELS.md
    ├── OLLAMA_TO_LITELLM_MAPPING.md
    ├── OPENAI_TO_OLLAMA_MAPPING.md
    └── DEFAULT_OPENAI_COMPAT_MODELS.md
```

## 🔍 Quick Links by Topic

### Setting Up Providers
- [Main README - Provider Configuration](../README.md#provider-configuration)
- [MIGRATION.md](guides/MIGRATION.md) - For upgrading from older versions

### Code Completion Integration
- [FIM_CODE_COMPLETION.md](guides/FIM_CODE_COMPLETION.md) - Configure for Continue.dev or Cursor

### Understanding Model Parameters
- [LITELLM_MODEL_PARAMETERS.md](reference/LITELLM_MODEL_PARAMETERS.md) - Full parameter reference
- [OLLAMA_TO_LITELLM_MAPPING.md](reference/OLLAMA_TO_LITELLM_MAPPING.md) - How Ollama params map to LiteLLM

### Creating Compat Models
- [COMPAT_MAPPING_PROPOSAL.md](guides/COMPAT_MAPPING_PROPOSAL.md) - Strategies for OpenAI API aliases
- [DEFAULT_OPENAI_COMPAT_MODELS.md](reference/DEFAULT_OPENAI_COMPAT_MODELS.md) - Pre-configured mappings

### API Integration
- [ollama-api.md](reference/ollama-api.md) - Ollama API endpoints and responses
- [OPENAI_API_MODELS.md](reference/OPENAI_API_MODELS.md) - OpenAI model list and capabilities

## 📝 Documentation Conventions

- **Guides** - Step-by-step tutorials and how-to documentation
- **Reference** - Technical specifications, API docs, parameter lists
- **Main README** - Quick start, installation, basic configuration

## 🆘 Need Help?

1. Check the [Main README](../README.md) for quick start instructions
2. Review [MODEL_STATISTICS](../MODEL_STATISTICS.md) for supported models
3. Read [CLAUDE.md](../CLAUDE.md) for architecture details
4. Report issues at the project repository

---

**Version**: 0.6.0 | **Last Updated**: 2025-12-29
