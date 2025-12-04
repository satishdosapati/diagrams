# Installing Strands Agents

If `strands-agents` fails to install from requirements.txt, install it manually:

## Option 1: Install from GitHub (Recommended)

```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
pip install git+https://github.com/strands-agents/sdk-python.git
deactivate
```

## Option 2: Install from PyPI (if available)

```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
pip install strands-agents
deactivate
```

## Verify Installation

```bash
source venv/bin/activate
python -c "from strands import Agent; print('Strands installed successfully')"
deactivate
```

## Troubleshooting

If you get Python version errors, ensure Python 3.10+ is installed:

```bash
python3 --version  # Should be 3.10 or higher
python3.11 --version  # Check if 3.11 is available
```

If Python 3.10+ is not available, install it:

```bash
# For Amazon Linux 2023
sudo yum install -y python3.11 python3.11-pip python3.11-devel

# Then recreate venv
cd /opt/diagram-generator/diagrams/backend
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

