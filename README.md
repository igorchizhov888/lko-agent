# Local Knowledge & Operations Assistant (LKO Agent)

## Overview
A local, autonomous agent that continuously observes system activity, answers operational questions, automates diagnostics, and recommends actions using structured reasoning.

## Current Capabilities

### ✅ Implemented (MVP)
- **Natural Language Queries**: Ask questions in plain English
- **Intelligent Planning**: LLM-based tool selection using Phi-3 Mini
- **System Monitoring Tools**:
  - Disk usage analysis
  - CPU load monitoring
  - Memory status checking
  - Process list inspection
  - Recent error log analysis
- **Safe Execution**: Dry-run mode and logging
- **CLI Interface**: Simple command-line interaction

## Architecture
```
agent/
├── planner/          # LLM-based reasoning and tool selection
│   ├── llm.py       # Interface to Phi-3 via llama.cpp
│   └── planner.py   # Query planning logic
├── executor/         # Safe tool execution
│   └── executor.py  # Runs planned tools with safety checks
├── tools/            # System monitoring capabilities
│   └── system_tools.py
├── memory/           # (Future: RAG and persistent memory)
├── retriever/        # (Future: Knowledge base search)
├── prompts/          # (Future: Prompt templates)
├── logs/             # Query and execution logs
└── config.yaml       # Configuration
```

## Installation

### Prerequisites
- Python 3.11+
- llama.cpp compiled with Phi-3 model
- Linux system (Ubuntu/Debian)

### Setup
```bash
# Already done in your setup:
cd ~/myagent_cli
source venv/bin/activate
pip install pyyaml
```

## Usage

### Basic Queries
```bash
# Check disk usage
python3 agent_cli.py ask "Why is my disk filling up?"

# Monitor memory
python3 agent_cli.py ask "What processes are using the most memory?"

# System health check
python3 agent_cli.py ask "Is my system healthy? Check everything."

# CPU investigation
python3 agent_cli.py ask "Why is my CPU usage high?"

# Error investigation
python3 agent_cli.py ask "Show me recent system errors"
```

## Configuration

Edit `agent/config.yaml` to customize:
```yaml
# Safety settings
safety:
  dry_run: false          # Set to true to simulate actions
  require_confirmation: true
  log_all_actions: true

# LLM settings
llm:
  temperature: 0.1        # Lower = more deterministic
  max_tokens: 512         # Response length limit
  threads: 6              # CPU threads for inference
```

## Next Steps (Roadmap)

### Phase 2: Memory & RAG
- [ ] Vector store integration (FAISS)
- [ ] Embed and index system logs
- [ ] Query past incidents: "How did I fix this last time?"
- [ ] Build institutional knowledge over time

### Phase 3: Automated Remediation
- [ ] Restart services
- [ ] Clean temp directories
- [ ] Kill runaway processes
- [ ] Policy-driven auto-actions

### Phase 4: Autonomous Operation
- [ ] Scheduled health checks (cron/systemd)
- [ ] Anomaly detection
- [ ] Proactive alerts
- [ ] Weekly summaries

### Phase 5: Advanced Features
- [ ] Custom runbook integration
- [ ] Docker/container monitoring
- [ ] Network diagnostics
- [ ] Application-specific tools

## Technical Details

### Model
- **Phi-3 Mini 4K Instruct** (Q4 quantization)
- 3.8B parameters, ~2.4GB on disk
- Runs locally via llama.cpp
- Context window: 4096 tokens

### Safety Features
- Command timeout limits (30s default)
- Output size restrictions (10KB default)
- Tool allow-list enforcement
- All actions logged to JSONL

## Examples of Real Output

**Query**: "Why is my disk filling up?"
**Plan**: Use disk_usage and process_list tools
**Result**: Shows filesystem usage and memory-consuming processes

**Query**: "Is my system healthy?"
**Plan**: Execute all 5 diagnostic tools
**Result**: Comprehensive system health report

## Development Status

**Current Version**: 0.1.0 (MVP)
**Status**: ✅ Functional for read-only system diagnostics
**Next Milestone**: Add memory/RAG layer

## Files

- `agent_cli.py` - Main CLI interface
- `agent/config.yaml` - Configuration
- `agent/planner/` - Intelligence layer
- `agent/executor/` - Execution layer
- `agent/tools/` - System tools
- `agent/logs/` - Activity logs

## Notes

This is a production-oriented architecture, not a demo. The agent:
- Uses structured reasoning (plan → execute → results)
- Enforces safety boundaries
- Logs all activities
- Handles errors gracefully
- Provides clear, actionable output

**Author**: Built step-by-step with Claude
**Date**: December 2025
