# Local Knowledge & Operations Assistant (LKO Agent)

## Overview
A local, autonomous agent that uses Phi-3 Mini (3.8B) via llama.cpp to perform intelligent system diagnostics through natural language queries. **Now with institutional memory** - the agent learns from every interaction and builds operational knowledge over time.

## Current Capabilities

### ✅ Phase 1: Core Agent (Complete)
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

### ✅ Phase 2: Memory & RAG (Complete)
- **Vector Store**: FAISS-based semantic search over past incidents
- **Incident Logging**: Every query, plan, and result is recorded
- **Historical Search**: Find similar past problems and solutions
- **Pattern Recognition**: Track recurring issues and preferred solutions
- **Operational Statistics**: View tool usage, outcomes, and trends
- **Institutional Knowledge**: Agent learns from your specific system over time

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
├── memory/           # Memory & RAG system (NEW)
│   ├── embeddings.py      # Text-to-vector conversion
│   ├── vector_store.py    # FAISS vector database
│   └── incident_logger.py # Operational history tracking
├── logs/             # Query and execution logs
│   └── incidents.jsonl    # Full incident history
└── config.yaml       # Configuration
```

## Installation

See [SETUP.md](SETUP.md) for detailed installation instructions.

**Quick setup:**
```bash
git clone https://github.com/igorchizhov888/lko-agent.git
cd lko-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Then install llama.cpp and download Phi-3 model (see SETUP.md)
```

## Usage

### Ask Questions (with Memory)
```bash
# The agent checks past incidents and learns from each query
python3 agent_cli.py ask "Why is my disk filling up?"
python3 agent_cli.py ask "What processes are using the most memory?"
python3 agent_cli.py ask "Is my system healthy? Check everything."
```

### Search Past Incidents
```bash
# Find how you solved similar problems before
python3 agent_cli.py search "disk space"
python3 agent_cli.py search "slow system"
python3 agent_cli.py search "memory issues"
```

### View Statistics
```bash
# See operational history and patterns
python3 agent_cli.py stats
```

### Example Output
```
$ python3 agent_cli.py search "slow system"

Searching past incidents for: slow system
============================================================

Result 1 (similarity: 54.9%):
  Date: 2025-12-18T15:26:59
  Query: Why is my system slow?
  Goal: Identify causes of system slowness
  Tools: memory_status, cpu_load, process_list
  Outcome: success
```

## How Memory Works

### Incident Recording
Every query you ask is:
1. Embedded as a 384-dimensional vector
2. Stored in FAISS for semantic search
3. Logged to JSONL with full details
4. Available for future similarity searches

### Building Institutional Knowledge
Over time, the agent:
- **Recognizes patterns**: "This looks similar to an issue from last week..."
- **Learns solutions**: Tracks which fixes worked vs. failed
- **Identifies trends**: "Docker issues happen 2x/month on your system"
- **Provides context**: "You resolved this before by running X"

### Memory Files
- `agent/memory/faiss.index` - Vector database (semantic search)
- `agent/memory/metadata.pkl` - Incident metadata
- `agent/logs/incidents.jsonl` - Full incident history

## Configuration

Edit `agent/config.yaml`:
```yaml
# Memory settings
memory:
  vector_store: "faiss"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  max_short_term: 10
  sqlite_path: "./agent/memory/agent.db"
  faiss_index_path: "./agent/memory/faiss.index"

# Safety settings
safety:
  dry_run: false          # Set to true to simulate actions
  log_all_actions: true
```

## Technical Stack

- **Language**: Python 3.12
- **LLM Runtime**: llama.cpp (native binary)
- **Model**: Phi-3 Mini 4K Instruct Q4 (2.4GB)
- **Vector DB**: FAISS (CPU version)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2, 384d)
- **Dependencies**: PyYAML, FAISS, sentence-transformers
- **Platform**: Linux (Ubuntu 24)

## Roadmap

### Phase 3: Automated Remediation (Next)
- [ ] Restart services
- [ ] Clean temp directories
- [ ] Kill runaway processes
- [ ] Policy-driven auto-actions

### Phase 4: Autonomous Operation
- [ ] Systemd service
- [ ] Scheduled health checks
- [ ] Anomaly detection
- [ ] Proactive alerts

### Phase 5: Advanced Features
- [ ] Docker monitoring
- [ ] Network diagnostics
- [ ] Application-specific tools
- [ ] Custom runbook integration

## Performance

- **Model Load**: ~2-3 seconds (first query)
- **Query Planning**: ~1-2 seconds
- **Vector Search**: <100ms over 1000s of incidents
- **Total Response**: ~5-10 seconds typical
- **Memory Usage**: ~2.8GB (model + embeddings)

## Files

- `agent_cli.py` - Main CLI interface with memory integration
- `agent/config.yaml` - Configuration
- `agent/memory/` - Memory & RAG system
- `agent/logs/incidents.jsonl` - Operational history
- `README.md` - This file
- `BUILD_SUMMARY.md` - Implementation details
- `SETUP.md` - Installation guide

## Development Status

**Current Version**: 0.2.0 (Phase 2 Complete)
**Status**: ✅ Functional with institutional memory
**Next Milestone**: Automated remediation

## Contributing

This is a personal project demonstrating real agent architecture with memory capabilities.

## License

MIT License - See LICENSE file
