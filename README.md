# 💬 Chatbot template

A simple Streamlit app that shows how to build a chatbot using Groq's AI models.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

### How to run it on your own machine

1. Install uv (if you haven't already)

   ```
   $ pip install uv
   ```

2. Set up your Groq API key

   - Get your free API key from [Groq Console](https://console.groq.com/keys)
   - Create a `.streamlit/secrets.toml` file in the project root
   - Add your key: `GROQ_AI_KEY = "your_groq_api_key_here"`

3. Install the project dependencies

   ```
   $ uv sync
   ```

4. Run the app

   ```
   $ uv run streamlit run streamlit_app.py
   ```
