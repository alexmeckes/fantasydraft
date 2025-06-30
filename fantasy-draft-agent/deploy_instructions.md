# Gradio Deploy Instructions

## Prerequisites
1. Make sure you're in the `fantasy-draft-agent` directory
2. Activate your virtual environment: `source venv/bin/activate`
3. Have your Hugging Face account ready

## Run the Deploy Command

```bash
gradio deploy
```

## What You'll Be Asked:

1. **Hugging Face Token**: 
   - Go to https://huggingface.co/settings/tokens
   - Create a new token with 'write' permissions
   - Copy and paste it when prompted

2. **Space Name**: Enter something like `fantasy-draft-demo`

3. **Hardware**: Choose `cpu-basic` (free tier)

4. **Want to create a secret?**: 
   - Type `yes`
   - Secret name: `OPENAI_API_KEY`
   - Secret value: Your OpenAI API key

5. **Space visibility**: Choose `public` or `private`

## After Deployment

The command will:
- Automatically create the Space
- Upload all your files
- Set up the environment
- Provide you with the Space URL

## Important Notes

- The deploy command uses `app.py` as the entry point (which we already created)
- It will automatically detect and upload your `requirements.txt`
- The README_HF.md metadata will be used if you rename it to README.md first
- You can run `gradio deploy` again to update an existing Space 