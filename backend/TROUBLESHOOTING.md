# Troubleshooting Backend Errors

## Common Import Errors

### 1. ModuleNotFoundError: No module named 'strands'

**Solution:**
```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
pip install git+https://github.com/strands-agents/sdk-python.git
deactivate
```

### 2. NameError: name 'model_validator' is not defined

**Solution:** Already fixed in `src/models/spec.py`. Make sure you have the latest code:
```bash
cd /opt/diagram-generator/diagrams
git pull origin main
```

### 3. Import Errors During Startup

**Check full error:**
```bash
sudo journalctl -u diagram-api.service -n 100 --no-pager
```

**Test imports manually:**
```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
python -c "from src.api.routes import router; print('OK')"
python -c "from src.agents.diagram_agent import DiagramAgent; print('OK')"
python -c "from src.models.spec import ArchitectureSpec; print('OK')"
deactivate
```

### 4. Python Version Issues

**Check Python version:**
```bash
python3 --version
python3.11 --version
```

**If Python 3.10+ not available:**
```bash
sudo yum install -y python3.11 python3.11-pip python3.11-devel
cd /opt/diagram-generator/diagrams/backend
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Dependency Conflicts

**Check for conflicts:**
```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
pip check
deactivate
```

**Fix conflicts:**
```bash
source venv/bin/activate
pip install --upgrade 'uvicorn[standard]>=0.31.1'
pip install --upgrade 'pydantic>=2.11.0,<3.0.0'
pip install --upgrade 'python-multipart>=0.0.9'
pip install --upgrade 'anyio>=4.7.0'
deactivate
```

### 6. Service Won't Start

**Check service file:**
```bash
sudo cat /etc/systemd/system/diagram-api.service
```

**Verify paths exist:**
```bash
ls -la /opt/diagram-generator/diagrams/backend/
ls -la /opt/diagram-generator/diagrams/backend/venv/bin/uvicorn
ls -la /opt/diagram-generator/diagrams/backend/.env
ls -la /opt/diagram-generator/diagrams/backend/main.py
```

**Test command manually:**
```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
# If this works, Ctrl+C and restart service
deactivate
```

### 7. AWS Credentials Issues

**Check .env file:**
```bash
cat /opt/diagram-generator/diagrams/backend/.env
```

**Test AWS access:**
```bash
aws sts get-caller-identity
aws bedrock list-foundation-models --region us-east-1
```

## Getting Full Error Messages

```bash
# View last 100 lines of logs
sudo journalctl -u diagram-api.service -n 100 --no-pager

# Follow logs in real-time
sudo journalctl -u diagram-api.service -f

# View errors only
sudo journalctl -u diagram-api.service -p err -n 50
```

