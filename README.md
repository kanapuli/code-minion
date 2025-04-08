# Code Minion (Work in Progress)

An AI-powered code review assistant that runs completely local using Ollama.

## Overview

Code Minion is a command-line tool that analyzes codebases to find bugs, security issues, and quality problems. It uses local LLMs through Ollama to provide intelligent, context-aware reviews without sending code to external services.

## Key Features

- **Fully Local**: All analysis runs on your machine using Ollama - no code leaves your system
- **Language-Agnostic**: Works with any programming language through LLM analysis
- **Git-Aware**: Analyzes diffs between branches to provide targeted reviews
- **Multiple Analysis Types**: Combines LLM-based analysis with optional static analyzers
- **Clean Reports**: Generates markdown reports organized by severity

## Installation

### Prerequisites

1. Python 3.12+
2. [Ollama](https://ollama.ai) installed and running. Prefer to use CodeGemma, deepseekcoder models. They perform better at code analysis and reviews.
3. Git

### Setup

1. Clone the repository
```bash
git clone https://github.com/kanapuli/code-minion.git
cd code-minion
```

2. Set up a virtual environment using uv
```bash
# Install uv if not already installed
pip install uv

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies
```bash
uv install # This will install the dependencies in pyproject.toml
```

4. Pull a CodeLlama model using Ollama
```bash
ollama pull codegemma:7b
```

## Usage

### Review Changes Between Branches

```bash
# Run from your git repository
python -m code_minion review-diff --base-branch main

# Specify output file
python -m code_minion review-diff --base-branch main --output review.md

# Use a different model
python -m code_minion review-diff --base-branch main --model codellama:13b
```

### Review Specific Files

```bash
# Review specific files
python -m code_minion review-files path/to/file.py another/file.js

# Review all files in a directory
python -m code_minion review-dir src/
```

### Configuration

Create a `.code_minion.json` file in your home directory to customize the tool:

```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "model": "codellama:7b",
    "temperature": 0.2
  },
  "analysis": {
    "max_files": 100,
    "max_file_size": 1000000,
    "ignore_patterns": [
      "**/.git/**",
      "**/node_modules/**",
      "**/__pycache__/**"
    ]
  },
  "reporting": {
    "format": "markdown",
    "output_file": "code_minion_report.md"
  }
}
```

## Architecture

Code Minion follows a modular architecture:

- **Repository Manager**: Handles git operations and file access
- **Analyzer Framework**: Pluggable system for different analysis methods
- **LLM Integration**: Structures prompts and parses responses from Ollama
- **Formatters**: Generates readable reports from analysis results

## Development


### Adding New Analyzers

To create a new analyzer, extend the `BaseAnalyzer` class:

```python
from code_minion.analyzers.base import BaseAnalyzer
from code_minion.core.models import AnalysisResult

class MyCustomAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__(name="my-custom-analyzer")
        
    def analyze_file(self, file_path, file_content, metadata):
        # Your analysis logic here
        result = AnalysisResult(analyzer_name=self.name)
        # Add issues to result.issues
        return result
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
