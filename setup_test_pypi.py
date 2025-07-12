#!/usr/bin/env python3
"""
Setup script for publishing research-scout to Test PyPI
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False

def setup_test_pypi():
    """Setup and publish to Test PyPI"""
    
    print("🚀 Research Scout Test PyPI Publishing Setup")
    print("=" * 50)
    
    # Check if poetry is installed
    if not run_command("poetry --version", "Checking Poetry installation"):
        print("❌ Poetry is required. Install it first: https://python-poetry.org/docs/#installation")
        return False
    
    # Update version for test publishing
    print("\n📝 Updating version for test publishing...")
    version_cmd = 'poetry version prerelease'
    if not run_command(version_cmd, "Updating version"):
        return False
    
    # Configure test PyPI repository
    print("\n🔧 Configuring Test PyPI repository...")
    config_cmd = 'poetry config repositories.test-pypi https://test.pypi.org/legacy/'
    if not run_command(config_cmd, "Configuring Test PyPI repository"):
        return False
    
    # Build the package
    print("\n🏗️  Building the package...")
    if not run_command("poetry build", "Building package"):
        return False
    
    # Check build artifacts
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ Build failed: dist directory not found")
        return False
    
    built_files = list(dist_dir.glob("*"))
    if not built_files:
        print("❌ Build failed: no files in dist directory")
        return False
    
    print(f"✅ Built files: {[f.name for f in built_files]}")
    
    # Instructions for manual publishing
    print("\n📋 Manual Publishing Instructions")
    print("=" * 40)
    print("1. Create a Test PyPI account at: https://test.pypi.org/account/register/")
    print("2. Generate an API token at: https://test.pypi.org/manage/account/token/")
    print("3. Configure the token:")
    print("   poetry config pypi-token.test-pypi <your-token>")
    print("4. Publish to Test PyPI:")
    print("   poetry publish --repository test-pypi")
    print("\n🔍 To install the published package:")
    print("   pip install --index-url https://test.pypi.org/simple/ research-scout")
    
    return True

def main():
    """Main setup function"""
    
    # Ensure we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Run this script from the project root.")
        sys.exit(1)
    
    success = setup_test_pypi()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("Follow the manual instructions above to complete publishing.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
