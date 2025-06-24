# Fantasy Draft Agent - Screenshots

## Gradio Web Interface

The Fantasy Draft Agent includes a beautiful web interface built with Gradio. Here's what you'll see:

### 1. Draft Assistant Tab
The main chat interface where you interact with the AI agent:
- **Chat Panel**: Full conversation history with context retention
- **Your Roster**: Live-updating sidebar showing your current picks
- **Example Prompts**: Quick-start questions to try

### 2. Player Analysis Tab
Compare players and analyze positions:
- **Player Comparison**: Side-by-side stats for two players
- **Position Analysis**: Scarcity analysis showing tier breakdowns

### 3. Available Players Tab
Browse all available players:
- **Filter by Position**: View all players or filter by RB, WR, QB, TE
- **Sorted by ADP**: Players listed in order of average draft position
- **Live Updates**: Automatically removes drafted players

### 4. Demo Scenarios Tab
Run pre-built conversation demonstrations:
- **The Opening Pick**: Shows strategy adaptation
- **The Position Run**: Demonstrates patience during runs
- **The Sleeper Question**: Displays deep player knowledge
- **The Stack Builder**: Shows correlation strategies

### 5. Draft Board Tab
Visual representation of the draft:
- **Round-by-Round View**: See all picks organized by round
- **Pick Numbers**: Shows draft order for each selection
- **Auto-Updates**: Refreshes as picks are made

## Features Demonstrated

- **Multi-Turn Conversations**: The chat maintains full context across messages
- **Visual Feedback**: ASCII player cards and comparisons
- **Real-Time Updates**: All tabs sync with the current draft state
- **Mobile Responsive**: Works great on phones and tablets
- **Dark Mode Support**: Gradio's soft theme is easy on the eyes

## Color Scheme

The interface uses Gradio's Soft theme with:
- Primary colors: Blue accents for buttons and links
- Background: Light gray/white for readability
- Text: High contrast for accessibility
- Emojis: Visual indicators for different sections

To see it in action, run:
```bash
python app.py
```

Then open http://localhost:7860 in your browser! 