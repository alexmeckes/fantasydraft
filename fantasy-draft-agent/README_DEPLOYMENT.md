# Fantasy Draft App Deployment Guide

## Option 1: Hugging Face Spaces (Recommended)

### Steps:
1. Create a free account at [huggingface.co](https://huggingface.co)
2. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
3. Choose:
   - Space name: `fantasy-draft-demo`
   - Select **Gradio** as the SDK
   - Choose **Public** visibility
   - Select hardware: **CPU Basic** (free tier)

4. Clone your new space locally:
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/fantasy-draft-demo
cd fantasy-draft-demo
```

5. Copy your app files:
```bash
cp -r /path/to/fantasy-draft-agent/* .
```

6. Create a `requirements.txt` if you don't have one:
```txt
gradio>=4.0.0
openai>=1.0.0
python-dotenv
```

7. Create or update `app.py` to ensure it runs:
```python
# At the bottom of app.py, make sure you have:
if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch()
```

8. Set up secrets in your Space settings:
   - Go to your Space settings
   - Add secret: `OPENAI_API_KEY` = your API key

9. Push to Hugging Face:
```bash
git add .
git commit -m "Initial deployment"
git push
```

Your app will be live at: `https://huggingface.co/spaces/YOUR_USERNAME/fantasy-draft-demo`

## Option 2: Gradio Share Link (Temporary)

For quick sharing (link expires after 72 hours):

```python
# In app.py, modify the launch line:
demo.launch(share=True)
```

This generates a public URL like `https://xxxxx.gradio.live`

## Option 3: Railway (Simple Cloud Deployment)

1. Install Railway CLI: `npm install -g @railway/cli`
2. In your project directory:
```bash
railway login
railway init
railway up
```
3. Add environment variables in Railway dashboard

## Option 4: Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t fantasy-draft .
docker run -p 7860:7860 -e OPENAI_API_KEY=your_key fantasy-draft
```

## Environment Variables

Regardless of deployment method, ensure these are set:
- `OPENAI_API_KEY`: Your OpenAI API key

## Tips for Production

1. **Add error handling** for API failures
2. **Set up rate limiting** to control costs
3. **Add a loading message** for slow API responses
4. **Consider caching** common responses
5. **Monitor API usage** to avoid surprises

## Sharing Your Deployed App

Once deployed, share your app by:
1. Sending the direct URL
2. Embedding in a website: `<iframe src="YOUR_APP_URL"></iframe>`
3. Adding to GitHub README with a "Try it out" button 