# 🤖 Algo Rangers AI Chatbot

A full-featured AI chatbot application built with Streamlit, powered by Groq's AI models, and backed by PostgreSQL for persistent conversation storage.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

## ✨ Features

- 🤖 **AI-Powered Conversations**: Uses Groq's latest AI models with dynamic model selection
- 💾 **Persistent Storage**: All conversations saved to PostgreSQL database
- 👤 **User Management**: Simple user session management
- 📊 **Usage Statistics**: Track conversations and token usage
- 🔄 **Conversation History**: Load and continue previous conversations
- 🎯 **Intelligent Model Selection**: Automatically selects the best available AI model
- 🔒 **Secure Configuration**: API keys and database credentials stored securely

## 🏗️ Architecture

- **Frontend**: Streamlit for the web interface
- **AI**: Groq API for language model inference
- **Database**: PostgreSQL (Supabase) for data persistence
- **Package Management**: uv for fast dependency management

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

1. **First Visit**: Enter your name and email (optional) to create a session
2. **Start Chatting**: Type messages and get AI responses
3. **View Stats**: See your conversation count and token usage in the sidebar
4. **Load History**: Click "Load Previous Conversations" to continue old chats
5. **Clear Chat**: Reset the current conversation

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

### Smart Model Selection
- Dynamically queries Groq for available models
- Scores models based on capabilities
- Automatically falls back if preferred models are unavailable
- Caches model list for performance

### Conversation Persistence
- Every message and response saved to database
- User statistics tracked (conversation count, tokens used)
- Conversation history can be loaded across sessions
- Secure session management with UUID

### User Experience
- Clean, responsive interface
- Real-time streaming responses
- Error handling and recovery
- Optional user profile information

## 🛠️ Development

Built with modern Python tools:
- `uv` for fast package management
- `streamlit` for the web interface
- `groq` for AI model access
- `sqlalchemy` + `psycopg2` for database operations

## 📝 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]
