# Setup Guide

This guide covers everything you need to set up and run the Fantasy Draft Multi-Agent Demo.

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd fantasy-draft-agent
   ```

2. **Set up Python environment** (Python 3.8+ required)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up API key**
   ```bash
   export OPENAI_API_KEY='your-key-here'
   # Or create a .env file with: OPENAI_API_KEY=your-key-here
   ```

4. **Run the app**
   ```bash
   python apps/app.py
   ```

## Detailed Setup

### Environment Setup

The app requires Python 3.8+ and the following main dependencies:
- `gradio>=4.0.0` - Web interface
- `any-agent` - Multi-agent framework
- `openai` - LLM integration
- `python-dotenv` - Environment management
- `nest-asyncio` - Async support for Gradio

### Virtual Environment (Recommended)

Using a virtual environment keeps dependencies isolated:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

### Configuration

1. **API Keys**: The app requires an OpenAI API key. Set it via:
   - Environment variable: `export OPENAI_API_KEY='sk-...'`
   - `.env` file: Create `.env` in project root with `OPENAI_API_KEY=sk-...`

2. **Port Configuration**: 
   - Default web interface: Port 7860
   - A2A mode uses dynamic ports (5000-9000 range)
   - Modify in `apps/app.py` if needed

## Running Different Modes

### Basic Mode (Recommended for Development)
```bash
python apps/app.py
```
- Single process, fast execution
- Good for testing and development
- Supports multiple users

### A2A Mode (Distributed Agents)
- Automatically enabled via the UI toggle
- Each agent runs on its own HTTP server
- Dynamic port allocation for multi-user support
- Production-ready architecture

## Deployment Options

### Local Deployment
- Just run the app as shown above
- Access at `http://localhost:7860`
- Share link provided by Gradio

### Hugging Face Spaces
1. Create a new Space on Hugging Face
2. Upload all files maintaining structure
3. Set the OpenAI API key as a Space secret
4. The app will auto-detect and run

### Server Deployment
1. Ensure Python 3.8+ is installed
2. Clone repository to server
3. Set up systemd service or process manager
4. Configure reverse proxy (nginx/Apache) if needed
5. Set environment variables securely

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not found"**
   - Ensure the API key is set correctly
   - Check `.env` file location (project root)
   - Verify key starts with `sk-`

2. **Port already in use**
   - Change port in `apps/app.py`: `demo.launch(server_port=7861)`
   - Or kill the process using the port

3. **Module not found errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again
   - Check Python version (3.8+ required)

4. **A2A mode fails to start**
   - Check firewall settings for ports 5000-9000
   - Ensure no other services using these ports
   - Try Basic Multiagent mode as fallback

### Performance Tips

- Use Basic Multiagent mode for faster response times
- Adjust `TYPING_DELAY_SECONDS` in `constants.py` for faster demos
- Run on a machine with good CPU for multiple A2A agents
- Consider GPU instance if using larger models

## Next Steps

- Read [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) for architecture details
- See [FEATURES_AND_ENHANCEMENTS.md](FEATURES_AND_ENHANCEMENTS.md) for all features
- Check the main [README.md](../README.md) for project overview 