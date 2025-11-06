# Installing Python 3.11 for MedCPT/BioLORD Embeddings

## Current Status
- ✅ Embedding system works with OpenAI
- ❌ Python 3.13 is not compatible with torch (required for MedCPT/BioLORD)
- Need Python 3.11 or 3.10

## Option 1: Install Python 3.11 via Official Installer (Recommended)

1. Download Python 3.11 from: https://www.python.org/downloads/release/python-3119/
   - Choose: "macOS 64-bit universal2 installer" (or Intel if on Intel Mac)

2. Run the installer and follow the prompts

3. After installation, verify:
   ```bash
   python3.11 --version
   ```

4. Create a virtual environment with Python 3.11:
   ```bash
   python3.11 -m venv venv311
   source venv311/bin/activate
   pip install -r requirements.txt
   pip install sentence-transformers torch
   ```

## Option 2: Install via Homebrew (if you have/want Homebrew)

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Use Python 3.11
python3.11 -m venv venv311
source venv311/bin/activate
pip install -r requirements.txt
pip install sentence-transformers torch
```

## Option 3: Use pyenv (Recommended for managing multiple Python versions)

```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to ~/.zshrc (or ~/.bash_profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Install Python 3.11
pyenv install 3.11.9

# Set as local version for this project
cd "/Users/apple/Desktop/MediBot Analysis"
pyenv local 3.11.9

# Create virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install sentence-transformers torch
```

## After Installing Python 3.11

1. Activate the virtual environment
2. Set EMBEDDING_MODEL in .env:
   ```bash
   EMBEDDING_MODEL=medcpt  # or biolord
   ```

3. Test embeddings:
   ```bash
   python test_embeddings.py
   ```

4. Run indexing:
   ```bash
   python run_indexing.py
   ```

## Quick Test After Installation

```bash
python3.11 -c "import torch; import sentence_transformers; print('✓ All dependencies installed!')"
```


