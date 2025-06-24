#!/usr/bin/env python3
"""
Prepare the Fantasy Draft app for deployment
"""

import os
import shutil

print("🚀 Preparing Fantasy Draft App for Deployment\n")

# Create deployment directory
deploy_dir = "fantasy-draft-deploy"
if os.path.exists(deploy_dir):
    shutil.rmtree(deploy_dir)
os.makedirs(deploy_dir)

# Files to copy
files_to_copy = [
    "app.py",
    "agent.py",
    "data.py",
    "multiagent_draft.py",
    "multiagent_scenarios.py",
    "scenarios.py",
    "requirements.txt",
    ".env.example"
]

# Copy files
for file in files_to_copy:
    if os.path.exists(file):
        shutil.copy(file, deploy_dir)
        print(f"✅ Copied {file}")
    else:
        print(f"⚠️  {file} not found")

# Create a minimal README for the Space
readme_content = """---
title: Fantasy Draft Multi Agent Demo
emoji: 🏈
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.19.2
app_file: app.py
pinned: false
---

# Fantasy Draft Multi-Agent Demo 🏈

An AI-powered fantasy football draft simulator with multiple intelligent agents!

## Features
- 6 AI agents with distinct draft strategies
- Real-time agent-to-agent communication
- Multi-turn memory system
- Interactive user participation

## How to Use
1. Click "Start Mock Draft"
2. Watch AI agents make picks and comment
3. Make your pick when it's your turn
4. See how different strategies play out!

Check out the [GitHub repo](https://github.com/alexmeckes/fantasydraft) for more details.
"""

with open(os.path.join(deploy_dir, "README.md"), "w") as f:
    f.write(readme_content)
print("✅ Created README.md")

# Update requirements.txt for deployment
requirements_content = """gradio>=4.19.2
openai>=1.0.0
python-dotenv>=1.0.0
"""

with open(os.path.join(deploy_dir, "requirements.txt"), "w") as f:
    f.write(requirements_content)
print("✅ Updated requirements.txt")

# Create .gitignore
gitignore_content = """.env
__pycache__/
*.pyc
.DS_Store
venv/
.idea/
"""

with open(os.path.join(deploy_dir, ".gitignore"), "w") as f:
    f.write(gitignore_content)
print("✅ Created .gitignore")

print(f"\n✨ Deployment files ready in '{deploy_dir}/' directory!")
print("\nNext steps:")
print("1. Create a new Space on Hugging Face")
print("2. Copy the files from fantasy-draft-deploy/ to your Space")
print("3. Add your OPENAI_API_KEY as a secret in Space settings")
print("4. Push to Hugging Face and your app will be live!") 