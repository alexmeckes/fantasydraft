---
title: fantasy-draft-demo
emoji: 🏈
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.36.0
app_file: app.py
pinned: false
license: mit
python_version: 3.11
---

# 🏈 Fantasy Draft Multi-Agent Demo

Experience AI agents with distinct personalities competing in a fantasy football draft! You play as Team 4 with an AI advisor.

## Features

- **6 AI Agents** with unique strategies (Zero RB, Best Player Available, Robust RB, etc.)
- **Two Communication Modes**:
  - **Basic Multiagent**: Fast, single-process execution
  - **A2A Mode**: Distributed agents on HTTP servers (limited on free tier)
- **Interactive Participation**: Draft alongside AI with strategic advice
- **Real-time Communication**: Agents comment and react to picks
- **Multi-User Support**: Each user gets their own draft session

## Setup

1. Add your OpenAI API key in **Settings → Repository secrets** as `OPENAI_API_KEY`
2. The app will start automatically once deployed

## About Communication Modes

- **Basic Multiagent (Recommended)**: Works perfectly on HF Spaces! All agents run in a single process with fast, reliable communication.
- **A2A Mode (Experimental)**: Distributed agents on separate servers. Due to dependency issues with `a2a-sdk` on HF Spaces, this mode may not work. Basic Multiagent provides the same great experience!

## About

Built with the [any-agent](https://github.com/any-agent/any-agent) framework, showcasing how modern LLMs can create engaging multi-agent experiences.

[View Source Code](https://github.com/alexmeckes/fantasydraft) 