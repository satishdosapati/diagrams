# Deployment Updates - EC2 Linux 3 (Amazon Linux 2023)

## Summary

Updated all deployment scripts and documentation for Amazon EC2 Linux 3 (Amazon Linux 2023). The deployment process is now more robust, automated, and includes comprehensive health checks and rollback capabilities.

## Changes Made

### 1. Updated Setup Script (`ec2-setup-amazon-linux.sh`)

**Improvements:**
- ✅ Uses `dnf` package manager (preferred for AL2023) with fallback to `yum`
- ✅ Explicitly installs Python 3.11+ (AL2023 default)
- ✅ Installs Node.js 20 LTS from NodeSource
- ✅ Better error handling and colored output
- ✅ Creates logs directory structure
- ✅ Sets proper file permissions
- ✅ More detailed version verification

### 2. Enhanced Deployment Script (`deploy-git.sh`)

**New Features:**
- ✅ Automatic backup creation before deployment
- ✅ Health checks after service restart
- ✅ Better error handling with exit codes
- ✅ Colored output for better visibility
- ✅ Branch name parameter support
- ✅ Service status verification
- ✅ HTTP endpoint health checks

### 3. Updated Systemd Service Files

**Backend Service (`diagram-api-amazon-linux.service`):**
- ✅ Added security hardening (NoNewPrivileges, PrivateTmp, ProtectSystem)
- ✅ Configured resource limits (MemoryLimit: 2G, LimitNOFILE: 65536)
- ✅ Added multiple uvicorn workers (2 workers for better performance)
- ✅ Proper PATH environment configuration
- ✅ Syslog identifier for better log filtering

**Frontend Service (`diagram-frontend-amazon-linux.service`):**
- ✅ Added security hardening
- ✅ Configured resource limits (MemoryLimit: 512M)
- ✅ Proper NODE_ENV=production setting
- ✅ Syslog identifier for better log filtering

### 4. New Scripts

**`health-check.sh`:**
- Comprehensive health monitoring
- Checks service status, HTTP endpoints, disk/memory usage
- Validates dependencies and builds
- Returns exit codes for automation

**`rollback.sh`:**
- Lists available backups
- Interactive rollback confirmation
- Automatic backup before rollback
- Service restart with health verification

**`install-services.sh`:**
- Automated systemd service installation
- Validates service files exist
- Enables services for auto-start
- Provides next-step instructions

### 5. Comprehensive Documentation

**`docs/DEPLOYMENT.md`:**
- Complete deployment guide
- Step-by-step instructions
- Troubleshooting section
- Security best practices
- Maintenance guidelines
- Backup strategies

**`deployment/README.md`:**
- Quick reference guide
- Script overview
- Common commands
- File permissions guide

## Migration Guide

### For Existing Deployments

If you have an existing deployment on EC2:

1. **Update systemd services:**
   ```bash
   cd /opt/diagram-generator/diagrams
   sudo bash deployment/install-services.sh
   sudo systemctl daemon-reload
   sudo systemctl restart diagram-api diagram-frontend
   ```

2. **Update deployment script:**
   ```bash
   git pull origin main
   # Future deployments will use the new script automatically
   ```

3. **Test health check:**
   ```bash
   bash deployment/health-check.sh
   ```

### For New Deployments

Follow the complete guide in `docs/DEPLOYMENT.md` or use the quick start in `README.md`.

## Key Improvements

1. **Better Error Handling**: All scripts now have proper error handling and exit codes
2. **Automated Health Checks**: Deployment includes automatic health verification
3. **Rollback Capability**: Easy rollback to previous deployments
4. **Security Hardening**: Systemd services include security best practices
5. **Better Logging**: Colored output and structured logging throughout
6. **Comprehensive Docs**: Complete documentation for all deployment scenarios

## Testing Checklist

Before deploying to production:

- [ ] Run `ec2-setup-amazon-linux.sh` on a fresh EC2 instance
- [ ] Verify Python 3.11+ is installed
- [ ] Verify Node.js 20+ is installed
- [ ] Test `deploy-git.sh` with a test branch
- [ ] Run `health-check.sh` and verify all checks pass
- [ ] Test rollback procedure
- [ ] Verify services start on boot
- [ ] Check logs are properly captured
- [ ] Verify security group allows ports 8000 and 3000

## Notes

- All scripts use `/opt/diagram-generator/diagrams` as the application directory
- Backups are stored in `/opt/diagram-generator-backups/`
- Services run as `ec2-user` for security
- Python 3.11 is explicitly used (AL2023 default)
- Node.js 20 LTS is recommended for stability

## Support

For issues or questions:
1. Check `docs/DEPLOYMENT.md` troubleshooting section
2. Run `bash deployment/health-check.sh`
3. Review service logs: `sudo journalctl -u diagram-api.service -f`
