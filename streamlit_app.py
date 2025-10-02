import streamlit as st
from groq import Groq
import uuid
from database import get_database_manager
from support_logic import support_agent
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="Customer Support Assistant",
    page_icon="🎧",
    layout="wide"
)

# Initialize database
@st.cache_resource
def init_database():
    return get_database_manager()

db_manager = init_database()

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "user_initialized" not in st.session_state:
    st.session_state.user_initialized = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_ticket_creation" not in st.session_state:
    st.session_state.pending_ticket_creation = False

if "pending_ticket_info" not in st.session_state:
    st.session_state.pending_ticket_info = {}

# Get the Groq API key from Streamlit secrets
try:
    groq_api_key = st.secrets["GROQ_AI_KEY"]
    client = Groq(api_key=groq_api_key)
except KeyError:
    st.error("Groq API key not found in secrets. Please configure GROQ_AI_KEY in .streamlit/secrets.toml")
    st.stop()
except Exception as e:
    st.error(f"Error initializing Groq client: {str(e)}")
    st.stop()

# Function to get the best available chat model
@st.cache_data(ttl=3600)
def get_best_chat_model():
    """Intelligently select the best available chat model from Groq without hardcoding"""
    try:
        models = client.models.list()
        available_models = [model.id for model in models.data]
        
        # Filter out non-chat models
        chat_models = []
        for model_id in available_models:
            model_lower = model_id.lower()
            if any(exclude in model_lower for exclude in ['whisper', 'tts', 'audio', 'speech']):
                continue
            if any(include in model_lower for include in ['chat', 'instruct', 'llama', 'gemma', 'qwen', 'mistral', 'gpt']):
                chat_models.append(model_id)
        
        if not chat_models:
            return available_models[0] if available_models else None
        
        # Intelligent selection based on model characteristics
        def model_score(model_id):
            score = 0
            model_lower = model_id.lower()
            
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
            
            if '3.3' in model_lower or '4.' in model_lower:
                score += 50
            elif '3.1' in model_lower or '3.2' in model_lower:
                score += 40
            elif '2.' in model_lower:
                score += 20
            
            if 'versatile' in model_lower:
                score += 30
            if 'instruct' in model_lower:
                score += 25
            
            if 'instant' in model_lower and ('8b' in model_lower or '7b' in model_lower):
                score += 20
            
            if 'llama' in model_lower:
                score += 10
            
            return score
        
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

# Sidebar for user info and chat controls
with st.sidebar:
    st.title("🎧 Customer Support")
    
    # User initialization
    if not st.session_state.user_initialized:
        st.subheader("Welcome to Support!")
        username = st.text_input("Your name (optional):")
        email = st.text_input("Your email (optional):")
        
        if st.button("Start Support Session"):
            try:
                user = db_manager.get_or_create_user(
                    session_id=st.session_state.session_id,
                    username=username if username else None,
                    email=email if email else None
                )
                st.session_state.user_initialized = True
                st.session_state.user_info = {
                    'username': username if username else 'Guest User',
                    'email': email if email else 'Not provided'
                }
                st.rerun()
            except Exception as e:
                st.error(f"Database error: {str(e)}")
    else:
        # Display user information
        st.subheader("👤 User Information")
        user_info = getattr(st.session_state, 'user_info', {})
        
        # Get user info from database if not in session state
        if not user_info:
            try:
                user = db_manager.get_or_create_user(st.session_state.session_id)
                st.session_state.user_info = {
                    'username': user.username if user.username else 'Guest User',
                    'email': user.email if user.email else 'Not provided'
                }
                user_info = st.session_state.user_info
            except:
                user_info = {'username': 'Guest User', 'email': 'Not provided'}
        
        st.write(f"**Name:** {user_info.get('username', 'Guest User')}")
        st.write(f"**Email:** {user_info.get('email', 'Not provided')}")
        
        st.divider()
        
        # Chat controls
        st.subheader("💬 Chat Controls")
        st.write("Use the chat below for all support needs:")
        st.write("• Ask questions")
        st.write("• Check ticket status")
        st.write("• Create support tickets")
        st.write("• Get help with orders")
        
        st.divider()
        
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.session_state.pending_ticket_creation = False
            st.session_state.pending_ticket_info = {}
            st.rerun()

# Main chat interface
if not st.session_state.user_initialized:
    st.title("🎧 Customer Support Assistant")
    st.write("Please complete the setup in the sidebar to start your support session.")
    st.stop()

# Header
st.title("🎧 Customer Support Assistant")
st.write("Hi! I'm here to help with your questions. I can assist with FAQs, create support tickets, and check ticket status.")

# Display the existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("How can I help you today?"):
    
    # Store and display the current prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process the user query
    try:
        # Check if we're waiting for ticket creation confirmation
        if st.session_state.pending_ticket_creation:
            if any(word in prompt.lower() for word in ['yes', 'please', 'create', 'y']):
                # Create the ticket
                ticket_info = st.session_state.pending_ticket_info
                ticket = db_manager.create_support_ticket(
                    session_id=st.session_state.session_id,
                    issue_description=ticket_info.get('description', prompt),
                    category=ticket_info.get('category', 'General Support'),
                    priority=ticket_info.get('priority', 'Medium')
                )
                
                response = f"Perfect! I've created a support ticket for you.\n\n**Ticket ID: {ticket.ticket_id}**\n\nOur support team will review your issue and contact you soon. You can check the status anytime using the ticket ID."
                
                # Reset pending state
                st.session_state.pending_ticket_creation = False
                st.session_state.pending_ticket_info = {}
                
            elif any(word in prompt.lower() for word in ['no', 'cancel', 'nevermind']):
                response = "No problem! Is there anything else I can help you with today?"
                st.session_state.pending_ticket_creation = False
                st.session_state.pending_ticket_info = {}
            else:
                response = "I didn't understand your response. Would you like me to create a support ticket? Please answer 'yes' or 'no'."
        else:
            # Classify the query using support logic
            query_type, query_info = support_agent.classify_query(prompt)
            
            if query_type == 'ticket_lookup':
                # Handle ticket lookup
                ticket_id = query_info['ticket_id']
                ticket = db_manager.get_ticket_by_id(ticket_id)
                
                if ticket:
                    if ticket.status.lower() == 'open':
                        status_msg = "currently being reviewed by our support team"
                    elif ticket.status.lower() == 'in progress':
                        status_msg = "being actively worked on by our support team"
                    elif ticket.status.lower() == 'resolved':
                        status_msg = "has been resolved"
                    else:
                        status_msg = f"has status: {ticket.status}"
                    
                    response = f"Thank you for providing your ticket ID. Your ticket **{ticket.ticket_id}** {status_msg}. You'll receive an update shortly."
                else:
                    response = f"I couldn't find a ticket with ID {ticket_id}. Please double-check the ticket ID or contact our support team if you continue to have issues."
            
            elif query_type == 'ticket_status_request':
                # Handle general ticket status request (without specific ID)
                response = query_info['response']
            
            elif query_info.get('can_answer', False):
                # FAQ that can be answered directly
                response = query_info['response']
                
            else:
                # Query that needs ticket creation
                if query_info.get('needs_ticket', False) or not query_info.get('can_answer', True):
                    response = query_info['response']
                    if query_info.get('follow_up'):
                        response += f"\n\n{query_info['follow_up']}"
                        
                        # Set up for ticket creation
                        st.session_state.pending_ticket_creation = True
                        st.session_state.pending_ticket_info = {
                            'description': prompt,
                            'category': support_agent.get_ticket_category(query_type),
                            'priority': support_agent.get_ticket_priority(prompt)
                        }
                else:
                    # Use AI for complex responses
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": "system", "content": "You are a helpful customer support assistant. Be polite, professional, and concise. If you cannot resolve an issue, suggest creating a support ticket."},
                            {"role": "user", "content": prompt}
                        ],
                        stream=True,
                    )

                    def response_generator():
                        for chunk in stream:
                            if chunk.choices[0].delta.content is not None:
                                yield chunk.choices[0].delta.content

                    with st.chat_message("assistant"):
                        response = st.write_stream(response_generator())
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Save conversation to database
                    try:
                        db_manager.save_conversation(
                            session_id=st.session_state.session_id,
                            message=prompt,
                            response=response,
                            model_used=selected_model,
                            tokens_used=0
                        )
                    except Exception as e:
                        st.warning(f"Failed to save conversation: {str(e)}")
                    
                    # Exit early since we handled the AI response
                    st.stop()

        # Display the response for non-AI responses
        with st.chat_message("assistant"):
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Save conversation to database
        try:
            db_manager.save_conversation(
                session_id=st.session_state.session_id,
                message=prompt,
                response=response,
                model_used="support_agent",
                tokens_used=0
            )
        except Exception as e:
            st.warning(f"Failed to save conversation: {str(e)}")
        
    except Exception as e:
        st.error(f"Error processing your request: {str(e)}")
        # Remove the user message from history if processing failed
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            st.session_state.messages.pop()
