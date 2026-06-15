# psaios — Python AI Automation Project

## Overview

`psaios` is a Python project I built as my primary AI-assisted development and automation platform. It served as the codebase used to train a LoRA (Low-Rank Adaptation) adapter for code-completion fine-tuning on Qwen2.5-Coder 14B.

## Project Context

- **Language:** Python
- **Purpose:** AI-assisted automation workflows and tooling
- **Significance:** The codebase became the training corpus for a local LoRA experiment, demonstrating the ability to fine-tune LLMs on personal codebases using owned GPU hardware

## LoRA Fine-Tuning Experiment

Using the T5810's dual A4500 GPUs, I trained a LoRA adapter (`20260429T133650Z-fc3ecc58`) on the psaios Python source code:

- **Base model:** Qwen2.5-Coder 14B Instruct
- **Training data:** psaios Python files (code-completion format)
- **Training hardware:** 2× RTX A4500, tensor parallel
- **Objective:** Code-completion style — predicting continuation of psaios-specific patterns

### What the LoRA Does (and Doesn't Do)

The LoRA is a **code-completion adapter** fine-tuned on psaios Python patterns. It's NOT:
- A biographical fine-tune (no personal info training)
- A chat model (not instruction-tuned on conversation data)
- Used in production (the portfolio chat uses the base instruct model + RAG instead)

For the portfolio AI chat, RAG with the knowledge base gives better results than the LoRA because it retrieves actual documented facts rather than predicting code tokens.

## Infrastructure Lesson

This project demonstrated the full fine-tuning pipeline on personal hardware:
1. Data preparation from a real codebase
2. LoRA training on tensor-parallel GPUs
3. Adapter evaluation and comparison vs. base model
4. Decision-making: when to use fine-tuning vs. RAG (RAG won for factual recall)

The psaios LoRA is kept as a reference but not loaded in the production service. Fine-tuning is valuable for style transfer and code completion on domain-specific patterns; RAG is better for factual grounding on structured documents.
