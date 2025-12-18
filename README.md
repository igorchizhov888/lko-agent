# Local Knowledge & Operations Assistant (LKO Agent)

## Overview
A local, autonomous agent that uses Phi-3 Mini (3.8B) via llama.cpp to perform intelligent system diagnostics through natural language queries. Features **institutional memory** that learns from every interaction and **intelligent resource management** with graceful remediation.

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
- **Safe Execution**: Dry-run mode and comprehensive logging
- **CLI Interface**: Simple command-line interaction

### ✅ Phase 2: Memory & RAG (Complete)
- **Vector Store**: FAISS-based semantic search over past incidents
- **Incident Logging**: Every query, plan, and result is recorded
- **Historical Search**: Find similar past problems and solutions
- **Pattern Recognition**: Track recurring issues and preferred solutions
- **Operational Statistics**: View tool usage, outcomes, and trends
- **Institutional Knowledge**: Agent learns from your specific system over time

### ✅ Phase 3: Intelligent Resource Management (Complete)
- **Resource Monitoring**: Detect CPU/memory hogs automatically
- **Smart Remediation**: Three-tier escalation strategy
  1. **Renice** (gentle): Reduce process priority first
  2. **Graceful Stop** (SIGTERM): Allow clean shutdown
  3. **Force Kill** (SIGKILL): Last resort only
- **Process Intelligence**: Wait and verify after each step
- **Safety First**: All actions respect dry-run mode
- **Remediation History**: Track all actions and outcomes

## Architecture
```
agent/
├── planner/          # LLM-based reasoning and tool selection
│   ├── llm.py       # Interface to Phi-3 via llama.cpp
│   └── planner.py   # Query planning logic
├── executor/         # Safe tool execution
│   └── executor.py  # Runs planned tools with safety checks
├── tools/            # System monitoring and management
│   ├── system_tools.py    # Monitoring tools
│   └── resource_manager.py # Process management (NEW)
├── memory/           # Memory & RAG system
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

### Test All Phases
```bash
# Run comprehensive test suite
python3 test_all_phases.py
```

## Intelligent Resource Management

### How It Works

When a process consumes excessive resources:

**Step 1: Renice (Gentle)**
- Increases process nice value (reduces priority)
- Allows process to continue but with less CPU time
- System remains responsive
- Waits to see if behavior improves

**Step 2: Graceful Stop (if renice didn't help)**
- Sends SIGTERM signal
- Process can clean up and save state
- Waits 5 seconds for graceful shutdown

**Step 3: Force Kill (last resort)**
- Sends SIGKILL signal only if SIGTERM failed
- Immediate termination
- Used only when necessary

### Example
```python
from agent.tools.resource_manager import ResourceManager

manager = ResourceManager(dry_run=False)

# Find resource hogs
hogs = manager.find_resource_hogs(cpu_threshold=80, memory_threshold=50)

# Smart remediation with escalation
results = manager.smart_remediate(hogs[0]['pid'])
```

## Configuration

Edit `agent/config.yaml`:
```yaml
# Memory settings
memory:
  vector_store: "faiss"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"

# Safety settings
safety:
  dry_run: false          # Set to true to simulate actions
  log_all_actions: true

# Resource management thresholds
resource_management:
  cpu_threshold: 80       # CPU % to consider problematic
  memory_threshold: 50    # Memory % to consider problematic
  renice_value: 19        # Nice value for deprioritization
```

## Technical Stack

- **Language**: Python 3.12
- **LLM Runtime**: llama.cpp (native binary)
- **Model**: Phi-3 Mini 4K Instruct Q4 (2.4GB)
- **Vector DB**: FAISS (CPU version)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2, 384d)
- **Process Management**: psutil
- **Dependencies**: PyYAML, FAISS, sentence-transformers, psutil
- **Platform**: Linux (Ubuntu 24)

## Roadmap

### Phase 4: Autonomous Operation (Next)
- [ ] Systemd service for background operation
- [ ] Scheduled health checks (hourly/daily)
- [ ] Proactive monitoring and alerts
- [ ] Email/Slack notifications
- [ ] Automatic log rotation and cleanup

### Phase 5: Advanced Features
- [ ] Docker container monitoring
- [ ] Network diagnostics tools
- [ ] Application-specific plugins
- [ ] Custom runbook integration
- [ ] Multi-system monitoring

## Performance

- **Model Load**: ~2-3 seconds (first query)
- **Query Planning**: ~1-2 seconds
- **Vector Search**: <100ms over 1000s of incidents
- **Process Renice**: <50ms
- **Total Response**: ~5-10 seconds typical
- **Memory Usage**: ~2.8GB (model + embeddings)

## Development Status

**Current Version**: 0.3.0 (Phase 3 Complete)
**Status**: ✅ Production-ready with intelligent resource management
**Next Milestone**: Autonomous scheduling

## Files

- `agent_cli.py` - Main CLI interface with memory
- `test_all_phases.py` - Comprehensive test suite
- `agent/tools/resource_manager.py` - Resource management
- `agent/memory/` - Memory & RAG system
- `README.md` - This file
- `BUILD_SUMMARY.md` - Implementation details
- `SETUP.md` - Installation guide

## Contributing

This is a demonstration project showcasing real agent architecture with memory and autonomous capabilities.

## License

MIT License
