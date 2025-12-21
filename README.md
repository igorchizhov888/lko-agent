# Local Knowledge & Operations Assistant (LKO Agent)

## Overview
A local, autonomous agent that uses Phi-3 Mini (3.8B) via llama.cpp to perform intelligent system diagnostics through natural language queries. Features institutional memory that learns from every interaction and intelligent resource management with graceful remediation.

## Current Capabilities

### Phase 1: Core Agent (Complete)
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

### Phase 2: Memory & RAG (Complete)
- **Vector Store**: FAISS-based semantic search over past incidents
- **Incident Logging**: Every query, plan, and result is recorded
- **Historical Search**: Find similar past problems and solutions
- **Pattern Recognition**: Track recurring issues and preferred solutions
- **Operational Statistics**: View tool usage, outcomes, and trends
- **Institutional Knowledge**: Agent learns from your specific system over time

### Phase 3: Intelligent Resource Management (Complete)
- **Resource Monitoring**: Detect CPU/memory hogs automatically
- **Smart Remediation**: Three-tier escalation strategy
  1. **Renice** (gentle): Reduce process priority first
  2. **Graceful Stop** (SIGTERM): Allow clean shutdown
  3. **Force Kill** (SIGKILL): Last resort only
- **Process Intelligence**: Wait and verify after each step
- **Safety First**: All actions respect dry-run mode
- **Remediation History**: Track all actions and outcomes

### Phase 4: Autonomous Operation (Complete)
- **Systemd Service**: Background daemon with auto-restart
- **Scheduled Monitoring**: Health checks every 6 hours, resource checks every 5 minutes
- **Proactive Alerts**: Desktop notifications for critical issues
- **Alert Logging**: All alerts saved to agent/logs/alerts.log
- **Autonomous Remediation**: Automatic renice of resource-hogging processes
- **Log Rotation**: Automatic cleanup (100MB max, 30 day retention)
- **One-Command Control**: Simple CLI for daemon management

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
│   └── resource_manager.py # Process management
├── memory/           # Memory & RAG system
│   ├── embeddings.py      # Text-to-vector conversion
│   ├── vector_store.py    # FAISS vector database
│   └── incident_logger.py # Operational history tracking
├── alerts.py         # Alert and notification system
├── log_rotation.py   # Log management
├── logs/             # Query and execution logs
│   ├── incidents.jsonl    # Full incident history
│   └── alerts.log         # Alert history
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
./install.sh  # Installs the 'agent' command
# Then install llama.cpp and download Phi-3 model (see SETUP.md)
```

## Usage

### On-Demand Queries
```bash
agent ask "Why is my disk filling up?"
agent ask "What processes are using the most memory?"
agent ask "Is my system healthy? Check everything."
```

### Search Past Incidents
```bash
agent search "disk space"
agent search "slow system"
agent search "memory issues"
```

### View Statistics
```bash
agent stats
```

### Daemon Control (Autonomous Mode)
```bash
agent start    # Start 24/7 autonomous monitoring
agent stop     # Stop daemon
agent status   # Check daemon status
agent restart  # Restart daemon
agent logs     # View live logs
```

### Testing
```bash
python3 test_all_phases.py  # Comprehensive test suite
python3 status.py           # Show current configuration
```

## Autonomous Operation

When running as a daemon, the agent:

**Every 5 minutes:**
- Monitors CPU and memory usage
- Detects resource-hogging processes
- Automatically renices processes using excessive resources (priority 0 → 19)
- Sends desktop notifications for critical issues
- Logs all detections and actions

**Every 6 hours:**
- Performs comprehensive system health check
- Rotates logs if they exceed 100MB
- Updates incident history

**Alert Thresholds (configurable):**
- CPU usage > 80%
- Memory usage > 50%
- Disk usage > 95%

## How It Works

### Intelligent Resource Management

**Detection:**
The agent continuously monitors all processes and identifies those consuming excessive CPU or memory.

**Three-Tier Remediation:**
1. **Renice (Gentle):** Reduces process priority from 0 to 19, allowing it to continue but with lower priority
2. **Graceful Stop:** If renice doesn't help, sends SIGTERM for clean shutdown
3. **Force Kill:** Only as last resort, sends SIGKILL

**Example:**
```
[2025-12-21 17:52:45] WARNING: Found 3 resource-intensive processes
  - PID 12345: stress - CPU: 99.9%
[2025-12-21 17:52:45] Attempting remediation for PID 12345...
[2025-12-21 17:52:45]   renice: Reniced PID 12345: 0 -> 19
```

### Memory & Learning

**Incident Recording:**
Every query is embedded as a 384-dimensional vector and stored in FAISS for semantic search.

**Pattern Recognition:**
Over time, the agent learns:
- Which issues occur frequently
- Which solutions work best
- System-specific quirks and behaviors
- Operational patterns and trends

**Example:**
After weeks of operation, searching for "disk space" will find all related incidents, showing you patterns in how your disk fills up.

## Configuration

Edit `agent/config.yaml`:
```yaml
# Daemon settings
daemon:
  check_interval: 3600           # General monitoring (1 hour)
  health_check_interval: 21600   # Full health check (6 hours)
  resource_check_interval: 300   # Resource monitoring (5 minutes)
  alerts:
    enabled: true
    critical_disk_threshold: 95
    critical_memory_threshold: 90
    critical_cpu_threshold: 90

# Memory settings
memory:
  vector_store: "faiss"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"

# Safety settings
safety:
  dry_run: false
  log_all_actions: true

# Resource management
resource_management:
  cpu_threshold: 80
  memory_threshold: 50
  renice_value: 19
```

## Technical Stack

- **Language**: Python 3.12
- **LLM Runtime**: llama.cpp (native binary)
- **Model**: Phi-3 Mini 4K Instruct Q4 (2.4GB)
- **Vector DB**: FAISS (CPU version)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2, 384d)
- **Process Management**: psutil
- **Notifications**: notify-send (Ubuntu)
- **Dependencies**: PyYAML, FAISS, sentence-transformers, psutil
- **Platform**: Linux (Ubuntu 24)

## Performance

- **Model Load**: ~2-3 seconds (first query)
- **Query Planning**: ~1-2 seconds
- **Vector Search**: <100ms over 1000s of incidents
- **Process Renice**: <50ms
- **Daemon Memory Usage**: ~300-400MB
- **Daemon CPU Usage**: <1% idle, ~5% during checks
- **Total Response**: ~5-10 seconds typical

## Roadmap

### Phase 5: Advanced Features (Future)
- Docker container monitoring
- Network diagnostics tools
- Application-specific plugins
- Custom runbook integration
- Multi-system monitoring
- Email/Slack alert integration

## Files

- `agent_cli.py` - Main CLI interface with memory
- `agent_daemon.py` - Autonomous monitoring daemon
- `test_all_phases.py` - Comprehensive test suite
- `status.py` - Display current status
- `install.sh` - Installation script
- `lko-agent.service` - Systemd service file
- `agent/` - Core agent modules
- `README.md` - This file
- `BUILD_SUMMARY.md` - Implementation details
- `SETUP.md` - Installation guide

## Development Status

**Current Version**: 0.4.0 (All Phases Complete)
**Status**: Production Ready
**Total Incidents Logged**: Grows with usage
**Commits**: 21+
**Lines of Code**: ~3,500+

## Contributing

This is a demonstration project showcasing real agent architecture with memory, autonomous operation, and intelligent resource management.

## License

MIT License

## Tested Functionality

- Autonomous detection of resource hogs
- Automatic process priority reduction
- Desktop notifications for critical alerts
- 36+ hours continuous operation without crashes
- Successful remediation of CPU-intensive processes
- Pattern recognition over multiple incidents
- Complete audit trail of all actions
