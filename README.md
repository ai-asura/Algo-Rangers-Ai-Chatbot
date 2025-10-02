# 🤖 Algo Rangers AI Chatbot

A full-featured AI customer support chatbot built with Streamlit, powered by Groq's AI models, and backed by PostgreSQL for persistent conversation storage.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://algo-rangers-ai-chatbot.streamlit.app/)

## 🌐 Live Demo

**Access the live application**: [https://algo-rangers-ai-chatbot.streamlit.app/](https://algo-rangers-ai-chatbot.streamlit.app/)

The application is automatically deployed to Streamlit Cloud via GitHub CI/CD. Any push to the `main` branch triggers an automatic deployment.

## ✨ Features

- 🤖 **AI-Powered Customer Support**: Intelligent intent classification using Groq AI models
- 🎯 **Smart Query Classification**: Automatically understands customer intent without hardcoded keywords
- 🎫 **Ticket Management**: Create, track, and manage support tickets with unique IDs
- 💾 **Persistent Storage**: All conversations and tickets saved to PostgreSQL database
- 👤 **User Session Management**: Simple user onboarding and session tracking
- 🔄 **Conversation History**: Load and continue previous conversations
- 📱 **Responsive Interface**: Clean, intuitive chat interface
- 🔒 **Secure Configuration**: API keys and database credentials stored securely

## 🏗️ Architecture

- **Frontend**: Streamlit for the web interface
- **AI**: Groq API for language model inference and intent classification
- **Database**: PostgreSQL (Supabase) for data persistence
- **Package Management**: uv for fast dependency management
- **Deployment**: Streamlit Cloud with GitHub CI/CD integration

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- uv package manager
- PostgreSQL database (we use Supabase)
- Groq API key

### Installation

1. **Install uv** (if you haven't already)

   ```bash
   pip install uv
   ```

2. **Clone and setup the project**

   ```bash
   git clone <your-repo-url>
   cd Algo-Rangers-Ai-Chatbot
   ```

3. **Configure secrets**

   Create a `.streamlit/secrets.toml` file with:

   ```toml
   GROQ_AI_KEY = "your_groq_api_key_here"
   SUPABASE_URI = "your_postgresql_connection_string"
   ```

   - Get your Groq API key from [Groq Console](https://console.groq.com/keys)
   - Get your PostgreSQL URI from your database provider

4. **Install dependencies**

   ```bash
   uv sync
   ```

5. **Run the application**

   ```bash
   uv run streamlit run streamlit_app.py
   ```

## 🗄️ Database Schema

The application uses two main tables:

- **users**: Store user sessions and basic info
- **conversations**: Store all chat messages and responses

Tables are automatically created on first run.

## 🎛️ Usage

1. **Visit the Live App**: Go to [https://algo-rangers-ai-chatbot.streamlit.app/](https://algo-rangers-ai-chatbot.streamlit.app/)
2. **First Visit**: Enter your name and email (optional) to create a session
3. **Start Chatting**: Use the chat interface for all support needs:
   - Ask questions about shipping, refunds, returns
   - Check ticket status by providing ticket ID
   - Create support tickets for complex issues
   - Get help with account or login problems
4. **Clear Chat**: Use the sidebar button to reset the conversation

## 🚀 Deployment & CI/CD

### Automatic Deployment
- **Live URL**: [https://algo-rangers-ai-chatbot.streamlit.app/](https://algo-rangers-ai-chatbot.streamlit.app/)
- **Deployment**: Streamlit Cloud with GitHub integration
- **CI/CD**: Automatic deployment on every push to `main` branch
- **Requirements**: Uses `pyproject.toml` for dependency management as per project requirements

### Manual Development Setup

If you want to run locally for development:

## 🔧 Configuration

### Environment Variables (in `.streamlit/secrets.toml`)

- `GROQ_AI_KEY`: Your Groq API key for AI model access
- `SUPABASE_URI`: PostgreSQL connection string for data storage

### Model Selection

The app automatically selects the best available model from Groq based on:
- Model size (larger = better performance)
- Model version (newer = better capabilities)
- Model type (instruction-tuned preferred)

## 📊 Features in Detail

### AI-Powered Intent Classification
- Uses Groq AI models to understand customer queries without hardcoded keywords
- Supports multiple intent categories: greetings, shipping, refunds, returns, login issues, etc.
- Provides confidence scores and reasoning for classification decisions
- Automatic fallback to keyword-based classification if AI is unavailable

### Customer Support Capabilities
- **FAQ Handling**: Instant answers to common questions
- **Ticket Creation**: Automated ticket generation with unique IDs (TCKT-YYYYMMDD-XXX format)
- **Ticket Tracking**: Check status of existing support tickets
- **Smart Escalation**: Knows when to escalate to human agents

### Technical Features
- **Smart Model Selection**: Dynamically queries Groq for available models and selects the best one
- **Database Integration**: PostgreSQL with SQLAlchemy for robust data persistence
- **Session Management**: Secure user sessions with UUID
- **Error Handling**: Graceful handling of API limits and network issues

## 🛠️ Development

Built with modern Python tools as per project requirements:
- `uv` for fast package management (replacing pip)
- `streamlit` for the web interface
- `groq` for AI model access (replacing OpenAI)
- `sqlalchemy` + `psycopg2` for database operations
- **GitHub CI/CD** for automatic deployment to Streamlit Cloud

## 📝 License

Apache License 2.0 - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository/or clone if you are invited
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request to branch 'main'

**Note**: Pushes to `main` branch automatically deploy to [https://algo-rangers-ai-chatbot.streamlit.app/](https://algo-rangers-ai-chatbot.streamlit.app/)

## 🚀 Project Requirements Compliance

This project fulfills all requirements from the specification:
- ✅ **Streamlit** frontend as requested
- ✅ **Groq AI** instead of OpenAI for language models
- ✅ **uv package manager** replacing pip for dependency management
- ✅ **PostgreSQL** backend storage as recommended
- ✅ **GitHub + Streamlit** deployment pipeline
- ✅ **AI-powered intent classification** without hardcoded keywords
- ✅ **Support ticket management** with proper ID format
- ✅ **Session-based chat history** and user management
