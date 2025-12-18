#!/bin/bash
# LKO Agent Installation Script

echo "Installing LKO Agent launcher..."

# Create bin directory if it doesn't exist
mkdir -p ~/bin

# Create the agent launcher script
cat > ~/bin/agent << 'SCRIPT'
#!/bin/bash
cd ~/myagent_cli
source venv/bin/activate
python3 agent_cli.py "$@"
SCRIPT

# Make it executable
chmod +x ~/bin/agent

# Add to PATH if not already there
if ! echo $PATH | grep -q "$HOME/bin"; then
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
    echo "Added ~/bin to PATH in ~/.bashrc"
    echo "Run 'source ~/.bashrc' or restart your terminal"
fi

echo "Installation complete!"
echo ""
echo "Usage:"
echo "  agent ask \"your question\""
echo "  agent search \"keyword\""
echo "  agent stats"
