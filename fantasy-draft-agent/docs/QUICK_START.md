# 🚀 Quick Start - Sharing Your App

## Option 1: Complete Setup & Share (Recommended for First Time)
```bash
./setup_and_share.sh
```
This will:
- Create a virtual environment
- Install all dependencies
- Create a public share link

## Option 2: Quick Share (If Already Set Up)
```bash
./share.sh
```
This will create a public URL that works for 72 hours.

## Option 2: Using Command Line Flag
```bash
python app.py --share
# or use the short version:
python app.py -s
```

## Option 3: Run Locally (No Public URL)
```bash
python app.py
```
Access at: http://localhost:7860

## 🔑 Don't Forget Your API Key!
```bash
export OPENAI_API_KEY='your-key-here'
```

## 🌐 What You'll Get
When sharing is enabled, you'll see something like:
```
Running on local URL: http://127.0.0.1:7860
Running on public URL: https://abcd1234.gradio.live
```

Share the public URL with anyone! It expires after 72 hours.

## 💡 Pro Tips
- The public URL works from anywhere - no firewall issues!
- Perfect for demos and quick sharing
- For permanent hosting, use Hugging Face Spaces (see README_DEPLOYMENT.md) 