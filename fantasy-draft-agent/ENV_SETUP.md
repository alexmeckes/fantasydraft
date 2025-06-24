# Setting Up Your OpenAI API Key

## Quick Setup

1. **Create your `.env` file** (if not already created):
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file**:
   ```bash
   nano .env  # or use your favorite editor
   ```

3. **Add your OpenAI API key**:
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
   ```
   Replace `sk-proj-xxxxxxxxxxxxxxxxxxxxx` with your actual API key.

## Getting an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (you won't be able to see it again!)
5. Add it to your `.env` file

## Important Notes

- **Never commit your `.env` file** - It's already in `.gitignore`
- **Keep your API key secret** - Don't share it publicly
- **The `.env` file is automatically loaded** - No need to export manually

## Alternative Methods

### Method 1: Export in Terminal (Temporary)
```bash
export OPENAI_API_KEY='sk-proj-xxxxxxxxxxxxxxxxxxxxx'
```
This only lasts for the current terminal session.

### Method 2: Add to Shell Profile (Permanent)
Add to `~/.bashrc`, `~/.zshrc`, or equivalent:
```bash
export OPENAI_API_KEY='sk-proj-xxxxxxxxxxxxxxxxxxxxx'
```
Then reload: `source ~/.bashrc`

### Method 3: Use .env File (Recommended)
The `.env` file is the best approach because:
- It's project-specific
- It's not committed to git
- It's automatically loaded by the app
- It's easy to manage

## Verify Your Setup

Run this to check if your key is loaded:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ Key loaded!' if os.getenv('OPENAI_API_KEY') else '❌ Key not found')"
```

## Troubleshooting

### Key not loading?
1. Make sure `.env` is in the project root (same folder as `app.py`)
2. Check that the key name is exactly `OPENAI_API_KEY`
3. Ensure there are no spaces around the `=` sign
4. Try restarting your terminal/IDE

### Getting API errors?
1. Verify your key is valid at https://platform.openai.com/api-keys
2. Check your API usage/limits at https://platform.openai.com/usage
3. Ensure your key has the necessary permissions 