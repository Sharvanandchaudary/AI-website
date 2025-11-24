@echo off
echo ========================================
echo XGENAI - Production Deployment Script
echo ========================================
echo.

cd "c:\Users\vsaravan\OneDrive - Cadence Design Systems Inc\Desktop\AI-website"

echo Step 1: Initialize Git Repository
git init
echo.

echo Step 2: Add all files
git add .
echo.

echo Step 3: Create initial commit
git commit -m "XGENAI platform - ready for production deployment"
echo.

echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Go to https://github.com/new
echo 2. Create a repository named: xgenai-platform
echo 3. Copy the repository URL
echo 4. Run these commands (replace YOUR_USERNAME):
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/xgenai-platform.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 5. Then follow DEPLOY_STEPS.md for the rest!
echo.
pause
