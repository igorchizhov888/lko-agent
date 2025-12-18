# Setup Instructions for LKO Agent

## Prerequisites

- Python 3.11+ with venv support
- Git and Git LFS
- CMake and C++ compiler
- 4GB+ RAM available
- Linux (Ubuntu 24+ recommended)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/igorchizhov888/lko-agent.git
cd lko-agent
```

### 2. Set Up Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install llama.cpp
```bash
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build with CMake
mkdir build
cd build
cmake ..
cmake --build . --config Release

# Verify the binary exists
ls -la bin/llama-run
cd ../..
```

### 4. Download Phi-3 Model
```bash
# Create model directory
mkdir -p llama.cpp/models/phi3
cd llama.cpp/models/phi3

# Download the model (2.4GB)
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# Verify download
ls -lh Phi-3-mini-4k-instruct-q4.gguf
cd ../../..
```

### 5. Update Configuration Paths

The paths in `agent/config.yaml` are absolute. Update them to match your installation:
```yaml
llm:
  binary_path: "/path/to/your/llama.cpp/build/bin/llama-run"
  model_path: "/path/to/your/llama.cpp/models/phi3/Phi-3-mini-4k-instruct-q4.gguf"
```

Or use relative paths:
```yaml
llm:
  binary_path: "./llama.cpp/build/bin/llama-run"
  model_path: "./llama.cpp/models/phi3/Phi-3-mini-4k-instruct-q4.gguf"
```

### 6. Test the Installation
```bash
# Activate virtual environment if not already
source venv/bin/activate

# Check status
python3 status.py

# Test with a query
python3 agent_cli.py ask "Is my system healthy?"
```

## Troubleshooting

### llama-run not found
- Verify the binary path in config.yaml
- Check that cmake build completed successfully
- Try: `find . -name "llama-run" -type f`

### Model not found
- Verify the model path in config.yaml
- Check that wget download completed (should be ~2.4GB)
- Try: `find . -name "*.gguf" -type f`

### Python module errors
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall requirements: `pip install -r requirements.txt`

### Permission denied
- Make scripts executable: `chmod +x agent_cli.py status.py`

## Quick Start After Setup
```bash
cd lko-agent
source venv/bin/activate
python3 agent_cli.py ask "YOUR QUESTION HERE"
```

## Directory Structure After Setup
```
lko-agent/
├── agent/              # Agent code (in Git)
├── llama.cpp/          # llama.cpp installation (NOT in Git)
│   ├── build/bin/llama-run
│   └── models/phi3/Phi-3-mini-4k-instruct-q4.gguf
├── venv/               # Python virtual environment (NOT in Git)
├── agent_cli.py        # Main interface
└── requirements.txt    # Python dependencies
```

## Notes

- The llama.cpp directory and model file are NOT included in Git due to size
- Total setup time: ~15-20 minutes (including model download)
- Disk space required: ~5GB (llama.cpp build + model)
