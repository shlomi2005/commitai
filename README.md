# commitai ✨

> AI-powered git commit messages that actually make sense.

[![PyPI version](https://img.shields.io/pypi/v/commitai-cli.svg)](https://pypi.org/project/commitai-cli/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Stop writing `fix bug`, `update stuff`, and `wip` forever. **commitai** reads your staged diff and generates meaningful [Conventional Commits](https://www.conventionalcommits.org/) messages — powered by Claude, GPT-4, or a **fully local Ollama model (free, no API key needed)**.

```
$ git add -p
$ commitai --provider ollama

  Branch: main

  [1]  feat(auth): add JWT refresh token rotation
  [2]  feat: implement sliding session expiry for tokens
  [3]  fix(auth): prevent token reuse after refresh
  [4]  refactor(auth): extract token lifecycle management
  [5]  security: rotate JWT tokens on each refresh request

  Select (1-5), edit, or quit: 1

  ✓ Committed: feat(auth): add JWT refresh token rotation
```

---

## Features

- **Multi-provider** — Claude (Anthropic), GPT-4 (OpenAI), or **local Ollama (free!)**
- **Context-aware** — uses your branch name and recent commits for style consistency
- **Interactive** — pick a suggestion, edit it, or bail out
- **Conventional Commits** — enforces `type(scope): description` format
- **Git hook** — install once, runs automatically on every `git commit`
- **Zero config** — just set your API key and go

---

## Installation

```bash
pipx install commitai-cli
```

Or with pip:
```bash
pip install commitai-cli
```

---

## Quick Start

### Option A — Free, local (no API key needed)

```bash
# 1. Install Ollama: https://ollama.com
ollama pull llama3.2

# 2. Run in your repo
git add .
commitai --provider ollama
```

### Option B — Claude (Anthropic)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
git add .
commitai
```

### Option C — OpenAI

```bash
pip install 'commitai-cli[openai]'
export OPENAI_API_KEY=sk-...
git add .
commitai --provider openai
```

---

## Usage

```
commitai [OPTIONS] COMMAND [ARGS]...

Options:
  -p, --provider [anthropic|openai|ollama]   AI provider  [default: anthropic]
  -m, --model TEXT                           Model override
  -n, --count INTEGER                        Number of suggestions  [default: 5]
  -y, --yes                                  Auto-select first suggestion
  -v, --version                              Show version and exit.

Commands:
  install-hook  Install as a prepare-commit-msg git hook.
```

---

## Provider Comparison

| Provider | Default Model | API Key | Cost |
|---|---|---|---|
| `ollama` | llama3.2 | ❌ No | **Free** (local) |
| `anthropic` | claude-haiku-4-5 | ✅ Yes | ~$0.001/commit |
| `openai` | gpt-4o-mini | ✅ Yes | ~$0.001/commit |

---

## License

MIT — see [LICENSE](LICENSE).
