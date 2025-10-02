import streamlit as st
from groq import Groq

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses Groq's AI models to generate responses. "
    "The API key is securely stored in the application configuration. "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Get the Groq API key from Streamlit secrets
try:
    groq_api_key = st.secrets["GROQ_AI_KEY"]
    # Create a Groq client.
    client = Groq(api_key=groq_api_key)
except KeyError:
    st.error("Groq API key not found in secrets. Please configure GROQ_AI_KEY in .streamlit/secrets.toml")
    st.stop()
except Exception as e:
    st.error(f"Error initializing Groq client: {str(e)}")
    st.stop()

# Function to get the best available chat model
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_best_chat_model():
    """Intelligently select the best available chat model from Groq without hardcoding"""
    try:
        models = client.models.list()
        available_models = [model.id for model in models.data]
        
        # Filter out non-chat models (audio, TTS, etc.)
        chat_models = []
        for model_id in available_models:
            model_lower = model_id.lower()
            # Exclude models that are clearly not for chat/text generation
            if any(exclude in model_lower for exclude in ['whisper', 'tts', 'audio', 'speech']):
                continue
            # Include models that indicate chat/instruction capabilities
            if any(include in model_lower for include in ['chat', 'instruct', 'llama', 'gemma', 'qwen', 'mistral', 'gpt']):
                chat_models.append(model_id)
        
        if not chat_models:
            # If no obvious chat models found, return first available model
            return available_models[0] if available_models else None
        
        # Intelligent selection based on model characteristics
        def model_score(model_id):
            """Score models based on likely capability and size"""
            score = 0
            model_lower = model_id.lower()
            
            # Prefer larger models (higher parameter counts usually mean better performance)
            if '70b' in model_lower or '72b' in model_lower:
                score += 100
            elif '32b' in model_lower or '34b' in model_lower:
                score += 80
            elif '13b' in model_lower or '15b' in model_lower:
                score += 60
            elif '8b' in model_lower or '9b' in model_lower:
                score += 40
            elif '7b' in model_lower:
                score += 30
            
            # Prefer newer versions
            if '3.3' in model_lower or '4.' in model_lower:
                score += 50
            elif '3.1' in model_lower or '3.2' in model_lower:
                score += 40
            elif '2.' in model_lower:
                score += 20
            
            # Prefer versatile/instruct models
            if 'versatile' in model_lower:
                score += 30
            if 'instruct' in model_lower:
                score += 25
            
            # Prefer instant/fast models if they're reasonable size
            if 'instant' in model_lower and ('8b' in model_lower or '7b' in model_lower):
                score += 20
            
            # Slight preference for llama models (generally well-tested)
            if 'llama' in model_lower:
                score += 10
            
            return score
        
        # Sort models by score and return the best one
        best_model = max(chat_models, key=model_score)
        return best_model
        
    except Exception as e:
        st.error(f"Error fetching available models: {str(e)}")
        return None

# Get the best available model
selected_model = get_best_chat_model()

if not selected_model:
    st.error("No suitable chat model available from Groq API")
    st.stop()

# Display which model is being used
with st.sidebar:
    st.info(f"🤖 Using model: {selected_model}")

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using the Groq API.
    try:
        stream = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using a custom generator
        def response_generator():
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        with st.chat_message("assistant"):
            response = st.write_stream(response_generator())
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        # Remove the user message from history if API call failed
        st.session_state.messages.pop()
        
        # If it's a model decommissioned error, clear the cache and try again
        if "decommissioned" in str(e).lower():
            st.cache_data.clear()
            st.rerun()
