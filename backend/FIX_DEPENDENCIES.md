# Fixing Dependency Conflicts

If you encounter dependency conflicts after installing strands-agents, update your requirements.txt and reinstall:

## Updated Requirements

The requirements.txt has been updated to use compatible versions:
- `uvicorn[standard]>=0.31.1` (was 0.24.0)
- `pydantic>=2.11.0,<3.0.0` (was 2.5.0)
- `python-multipart>=0.0.9` (was 0.0.6)
- `anyio>=4.7.0` (new dependency)

## Fix on EC2

```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Upgrade conflicting packages
pip install --upgrade uvicorn[standard] pydantic python-multipart anyio

# Or reinstall all requirements
pip install -r requirements.txt --upgrade

# Verify installation
python -c "from strands import Agent; print('OK')"
python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"

deactivate

# Restart service
sudo systemctl restart diagram-api.service
```

## If Issues Persist

Try a clean reinstall:

```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate

# Uninstall conflicting packages
pip uninstall -y uvicorn pydantic python-multipart anyio

# Reinstall with correct versions
pip install uvicorn[standard]>=0.31.1
pip install 'pydantic>=2.11.0,<3.0.0'
pip install python-multipart>=0.0.9
pip install anyio>=4.7.0

# Install strands-agents
pip install git+https://github.com/strands-agents/sdk-python.git

# Install rest of requirements
pip install -r requirements.txt

deactivate
```

