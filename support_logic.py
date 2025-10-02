"""
Support logic for the Algo Rangers AI Chatbot
Handles FAQ responses, ticket creation decisions, and customer support workflows with AI-powered intent classification
"""

import re
import json
from typing import Dict, Tuple, Optional
import streamlit as st
from groq import Groq

class SupportAgent:
    """AI Support Agent that handles customer queries and ticket management"""
    
    def __init__(self):
        # Initialize Groq client for intent classification
        try:
            self.client = Groq(api_key=st.secrets["GROQ_AI_KEY"])
        except:
            self.client = None
        
        # AI System Prompt for Intent Classification
        self.intent_classification_prompt = """You are an expert customer support intent classifier. Your job is to analyze customer messages and classify them into specific support categories.

CLASSIFICATION CATEGORIES:

1. **ticket_lookup** - When user provides a specific ticket ID (format: TCKT-YYYYMMDD-XXX)
2. **ticket_status_request** - When user wants to check ticket status but hasn't provided ticket ID yet
3. **greeting** - Simple greetings without specific requests (hi, hello, hey, good morning)
4. **shipping** - Questions about delivery, shipping times, tracking, when orders will arrive
5. **refund** - Questions about getting money back, refund process, canceling orders
6. **return** - Questions about returning items, exchanges, defective products
7. **login** - Problems with logging in, password issues, account access
8. **account** - Account information changes, profile updates, billing
9. **order_status** - Checking order status, where is my order
10. **ticket_request** - Explicit requests to create new tickets
11. **complex** - Complex issues that need human support but don't fit other categories

RESPONSE FORMAT:
Return ONLY a JSON object with this exact structure:
{
    "intent": "category_name",
    "confidence": 0.95,
    "reasoning": "brief explanation"
}

CLASSIFICATION RULES:
- If message contains ticket ID pattern (TCKT-YYYYMMDD-XXX), always classify as "ticket_lookup"
- If user wants to check ticket status but no ID provided, use "ticket_status_request"
- Simple greetings (1-3 words) should be "greeting"
- Be very specific about shipping vs order_status vs return intent
- If user explicitly asks to create ticket, use "ticket_request"
- When in doubt between categories, choose the most specific one
- Complex technical issues or complaints should be "complex"

Examples:
"Hi" → {"intent": "greeting", "confidence": 0.99, "reasoning": "Simple greeting"}
"TCKT-20241002-001" → {"intent": "ticket_lookup", "confidence": 0.99, "reasoning": "Contains ticket ID"}
"Check my ticket status" → {"intent": "ticket_status_request", "confidence": 0.95, "reasoning": "Wants ticket status without providing ID"}
"When will my order arrive?" → {"intent": "shipping", "confidence": 0.90, "reasoning": "Asking about delivery time"}
"I want to return this broken item" → {"intent": "return", "confidence": 0.95, "reasoning": "Return request for defective product"}
"I can't log into my account" → {"intent": "login", "confidence": 0.95, "reasoning": "Login access issue"}

Analyze this customer message and classify it:"""
        
        # FAQ responses based on intent
        self.faq_responses = {
            'shipping': {
                'response': "Our standard shipping takes 3-5 business days. Express shipping is available for 1-2 business days. You'll receive a tracking number once your order ships.",
                'can_answer': True
            },
            'refund': {
                'response': "Refunds are processed within 5-7 business days after we receive your return. The refund will be credited to your original payment method.",
                'can_answer': True
            },
            'return': {
                'response': "You can return items within 30 days of delivery. Items must be in original condition. Please visit our returns page or I can create a return ticket for you.",
                'can_answer': False,  # Needs ticket for return processing
                'follow_up': "Would you like me to create a return ticket for you?"
            },
            'login': {
                'response': "For login issues, please try resetting your password first. If that doesn't work, I'll create a support ticket for our technical team.",
                'can_answer': False,  # Usually needs technical support
                'follow_up': "Would you like me to create a support ticket for your login issue?"
            },
            'account': {
                'response': "For account changes, you can update most information in your profile settings. For billing or sensitive changes, I'll need to create a support ticket.",
                'can_answer': False,
                'follow_up': "Would you like me to create a ticket for account assistance?"
            },
            'order_status': {
                'response': "To check your order status, I'll need your order number or ticket ID. Please share it with me.",
                'can_answer': True
            },
            'greeting': {
                'response': "Hello! I'm your customer support assistant. How can I help you today?",
                'can_answer': True
            },
            'ticket_status_request': {
                'response': "Sure! Please provide your ticket ID (format: TCKT-YYYYMMDD-XXX).",
                'can_answer': True
            },
            'ticket_request': {
                'response': "I'd be happy to create a support ticket for you. Could you please describe your issue in detail?",
                'can_answer': False,
                'needs_ticket': True
            },
            'complex': {
                'response': "I understand you need assistance, but this seems like a complex issue that would be best handled by our support team.",
                'can_answer': False,
                'follow_up': "Would you like me to create a support ticket for you?",
                'needs_ticket': True
            }
        }
    
    def classify_query_with_ai(self, user_message: str) -> Tuple[str, float, str]:
        """Use AI to classify user query intent with rate limiting protection"""
        if not self.client:
            # Fallback to simple classification if AI is unavailable
            return self._fallback_classification(user_message)
        
        try:
            # Check for ticket ID pattern first (always high priority)
            ticket_pattern = r'TCKT-\d{8}-\d{3}'
            if re.search(ticket_pattern, user_message.upper()):
                return 'ticket_lookup', 0.99, 'Contains ticket ID pattern'
            
            # Use AI for intent classification with shorter timeout and rate limit handling
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Use a reliable model
                messages=[
                    {"role": "system", "content": self.intent_classification_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=100,   # Reduced tokens
                timeout=5         # Shorter timeout
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            
            # Clean up response if it contains extra text
            if '{' in ai_response and '}' in ai_response:
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                ai_response = ai_response[json_start:json_end]
            
            # Parse JSON response
            result = json.loads(ai_response)
            
            intent = result.get('intent', 'complex')
            confidence = result.get('confidence', 0.5)
            reasoning = result.get('reasoning', 'AI classification')
            
            # Validate intent is in our known categories
            valid_intents = ['ticket_lookup', 'ticket_status_request', 'greeting', 'shipping', 
                           'refund', 'return', 'login', 'account', 'order_status', 
                           'ticket_request', 'complex']
            
            if intent not in valid_intents:
                intent = 'complex'
                confidence = 0.5
            
            return intent, confidence, reasoning
            
        except json.JSONDecodeError:
            # If JSON parsing fails, use fallback
            return self._fallback_classification(user_message)
        except Exception as e:
            # Any other error (including rate limiting), use fallback
            error_msg = str(e).lower()
            if '429' in error_msg or 'rate limit' in error_msg:
                return self._fallback_classification(user_message)
            else:
                return self._fallback_classification(user_message)
    
    def _fallback_classification(self, user_message: str) -> Tuple[str, float, str]:
        """Fallback classification using simple keyword matching"""
        message_lower = user_message.lower()
        
        # Check for ticket ID pattern
        ticket_pattern = r'TCKT-\d{8}-\d{3}'
        if re.search(ticket_pattern, user_message.upper()):
            return 'ticket_lookup', 0.99, 'Contains ticket ID'
        
        # Simple keyword-based classification
        if any(word in message_lower for word in ['check status', 'ticket status', 'status of my ticket']):
            return 'ticket_status_request', 0.8, 'Ticket status keywords'
        
        if any(word in message_lower for word in ['hi', 'hello', 'hey']) and len(message_lower.split()) <= 3:
            return 'greeting', 0.9, 'Simple greeting'
        
        if any(word in message_lower for word in ['ship', 'delivery', 'tracking']):
            return 'shipping', 0.7, 'Shipping keywords'
        
        if any(word in message_lower for word in ['refund', 'money back']):
            return 'refund', 0.7, 'Refund keywords'
        
        if any(word in message_lower for word in ['return', 'exchange', 'broken']):
            return 'return', 0.7, 'Return keywords'
        
        if any(word in message_lower for word in ['login', 'password', 'sign in']):
            return 'login', 0.7, 'Login keywords'
        
        if any(word in message_lower for word in ['account', 'profile', 'billing']):
            return 'account', 0.7, 'Account keywords'
        
        if any(word in message_lower for word in ['order status', 'where is my order']):
            return 'order_status', 0.7, 'Order status keywords'
        
        if any(word in message_lower for word in ['create ticket', 'new ticket', 'need help']):
            return 'ticket_request', 0.8, 'Ticket creation keywords'
        
        return 'complex', 0.5, 'No specific category matched'
    
    def classify_query(self, user_message: str) -> Tuple[str, Dict]:
        """Classify user query and determine response strategy"""
        # Use AI-powered classification
        intent, confidence, reasoning = self.classify_query_with_ai(user_message)
        
        # Handle ticket lookup specially
        if intent == 'ticket_lookup':
            ticket_pattern = r'TCKT-\d{8}-\d{3}'
            ticket_id = re.search(ticket_pattern, user_message.upper()).group()
            return 'ticket_lookup', {'ticket_id': ticket_id}
        
        # Get response configuration for the intent
        if intent in self.faq_responses:
            response_config = self.faq_responses[intent].copy()
            response_config['ai_confidence'] = confidence
            response_config['ai_reasoning'] = reasoning
            return intent, response_config
        
        # Default fallback
        return 'complex', {
            'response': "I understand you need assistance, but this seems like a complex issue that would be best handled by our support team.",
            'can_answer': False,
            'follow_up': "Would you like me to create a support ticket for you?",
            'needs_ticket': True,
            'ai_confidence': confidence,
            'ai_reasoning': reasoning
        }
    
    def should_create_ticket(self, query_type: str, user_response: str = None) -> bool:
        """Determine if a ticket should be created based on query type and user response"""
        if query_type in ['return', 'login', 'account', 'complex']:
            return True
        
        if user_response and any(phrase in user_response.lower() for phrase in ['yes', 'please', 'create ticket', 'yes please']):
            return True
            
        return False
    
    def get_ticket_category(self, query_type: str) -> str:
        """Get appropriate ticket category based on query type"""
        category_map = {
            'return': 'Returns',
            'refund': 'Refunds', 
            'login': 'Technical',
            'account': 'Account',
            'shipping': 'Shipping',
            'order_status': 'Orders',
            'complex': 'General Support',
            'ticket_request': 'General Support'
        }
        return category_map.get(query_type, 'General Support')
    
    def get_ticket_priority(self, user_message: str) -> str:
        """Determine ticket priority based on message content"""
        urgent_keywords = ['urgent', 'emergency', 'asap', 'immediately', 'critical', 'broken']
        high_keywords = ['important', 'soon', 'quickly', 'deadline']
        
        message_lower = user_message.lower()
        
        if any(keyword in message_lower for keyword in urgent_keywords):
            return 'Urgent'
        elif any(keyword in message_lower for keyword in high_keywords):
            return 'High'
        else:
            return 'Medium'

# Initialize the support agent
support_agent = SupportAgent()