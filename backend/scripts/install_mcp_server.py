#!/usr/bin/env python3
"""
Install AWS Diagram MCP Server locally.

This script provides a cross-platform way to install the MCP server.
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path


def check_command(cmd):
    """Check if a command exists."""
    return shutil.which(cmd) is not None


def run_command(cmd, check=True):
    """Run a shell command."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd.split(),
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except FileNotFoundError:
        return False, "", f"Command not found: {cmd}"


def install_with_uv():
    """Install MCP server using uv."""
    print("\n" + "=" * 60)
    print("Installing MCP Server using uv")
    print("=" * 60)
    
    # Check if uv is installed
    if not check_command("uv"):
        print("❌ uv is not installed")
        print("\nInstall uv:")
        if sys.platform == "win32":
            print("  powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        else:
            print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False
    
    print("✓ uv is installed")
    
    # Check Python version
    python_ok, stdout, _ = run_command(["uv", "python", "list"], check=False)
    if python_ok:
        print(f"Python versions available:\n{stdout}")
    
    # Install Python 3.10+ if needed
    print("\nChecking Python 3.10+ installation...")
    python_list_ok, python_list, _ = run_command(["uv", "python", "list"], check=False)
    if python_list_ok and "3.10" not in python_list and "3.11" not in python_list and "3.12" not in python_list:
        print("Installing Python 3.10...")
        ok, _, err = run_command(["uv", "python", "install", "3.10"])
        if not ok:
            print(f"⚠ Warning: Could not install Python 3.10: {err}")
    
    # Install MCP server
    print("\nInstalling awslabs.aws-diagram-mcp-server...")
    ok, stdout, stderr = run_command(["uv", "tool", "install", "awslabs.aws-diagram-mcp-server"])
    
    if ok:
        print("✓ MCP server installed successfully")
        
        # Verify installation
        print("\nVerifying installation...")
        verify_ok, _, _ = run_command(["uv", "tool", "run", "awslabs.aws-diagram-mcp-server", "--help"], check=False)
        if verify_ok:
            print("✓ Installation verified")
            print("\n" + "=" * 60)
            print("Installation Complete!")
            print("=" * 60)
            print("\nTo use the installed version, set:")
            if sys.platform == "win32":
                print('  $env:MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"')
            else:
                print('  export MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"')
            return True
        else:
            print("⚠ Installation completed but verification failed")
            return False
    else:
        print(f"❌ Installation failed: {stderr}")
        return False


def check_graphviz():
    """Check if GraphViz is installed."""
    if check_command("dot"):
        ok, stdout, _ = run_command(["dot", "-V"], check=False)
        if ok:
            print(f"✓ GraphViz is installed: {stdout.split()[0] if stdout else 'OK'}")
            return True
    
    print("⚠ GraphViz is not installed")
    print("\nInstall GraphViz:")
    if sys.platform == "win32":
        print("  Download from: https://www.graphviz.org/download/")
        print("  Or use: choco install graphviz")
    elif sys.platform == "darwin":
        print("  brew install graphviz")
    else:
        print("  sudo apt-get install graphviz  # Ubuntu/Debian")
        print("  sudo yum install graphviz      # CentOS/RHEL")
        print("  sudo dnf install graphviz      # Fedora")
    return False


def main():
    """Main installation function."""
    print("=" * 60)
    print("AWS Diagram MCP Server Installation")
    print("=" * 60)
    
    # Check GraphViz
    print("\nChecking prerequisites...")
    graphviz_ok = check_graphviz()
    
    # Install MCP server
    if install_with_uv():
        print("\n✅ Installation successful!")
        print("\nNext steps:")
        print("1. Set USE_MCP_DIAGRAM_SERVER=true")
        print("2. Test with: python examples/mcp_integration_example.py")
        return 0
    else:
        print("\n❌ Installation failed")
        print("\nAlternative: Use uvx (on-demand download)")
        print("  export MCP_DIAGRAM_SERVER_COMMAND=\"uvx awslabs.aws-diagram-mcp-server\"")
        return 1


if __name__ == "__main__":
    sys.exit(main())
