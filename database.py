"""
Database utilities for the Algo Rangers AI Chatbot
"""
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False)
    username = Column(String(100))
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String(50), unique=True, nullable=False)  # TCKT-YYYYMMDD-XXX format
    user_session_id = Column(String(255), nullable=False)
    issue_description = Column(Text, nullable=False)
    status = Column(String(50), default='Open')  # Open, In Progress, Resolved, Closed
    priority = Column(String(20), default='Medium')  # Low, Medium, High, Urgent
    category = Column(String(100))  # Login, Refund, Shipping, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    assigned_agent = Column(String(100))

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_session_id = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model_used = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer, default=0)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL database using secrets"""
        try:
            database_url = st.secrets["SUPABASE_URI"]
            self.engine = create_engine(database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables if they don't exist
            Base.metadata.create_all(bind=self.engine)
            
        except Exception as e:
            st.error(f"Database connection failed: {str(e)}")
            raise e
    
    def get_db_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def get_or_create_user(self, session_id: str, username: str = None, email: str = None):
        """Get existing user or create new one"""
        db = self.get_db_session()
        try:
            user = db.query(User).filter(User.session_id == session_id).first()
            if not user:
                user = User(
                    session_id=session_id,
                    username=username,
                    email=email
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            return user
        finally:
            db.close()
    
    def save_conversation(self, session_id: str, message: str, response: str, model_used: str, tokens_used: int = 0):
        """Save conversation to database"""
        db = self.get_db_session()
        try:
            conversation = Conversation(
                user_session_id=session_id,
                message=message,
                response=response,
                model_used=model_used,
                tokens_used=tokens_used
            )
            db.add(conversation)
            db.commit()
            return conversation.id
        finally:
            db.close()
    
    def get_conversation_history(self, session_id: str, limit: int = 50):
        """Get conversation history for a user"""
        db = self.get_db_session()
        try:
            conversations = db.query(Conversation).filter(
                Conversation.user_session_id == session_id
            ).order_by(Conversation.created_at.desc()).limit(limit).all()
            return conversations
        finally:
            db.close()
    
    def get_user_stats(self, session_id: str):
        """Get user statistics"""
        db = self.get_db_session()
        try:
            total_conversations = db.query(Conversation).filter(
                Conversation.user_session_id == session_id
            ).count()
            
            total_tokens = db.query(Conversation).filter(
                Conversation.user_session_id == session_id
            ).with_entities(Conversation.tokens_used).all()
            
            total_tokens_used = sum([t[0] or 0 for t in total_tokens])
            
            total_tickets = db.query(SupportTicket).filter(
                SupportTicket.user_session_id == session_id
            ).count()
            
            return {
                'total_conversations': total_conversations,
                'total_tokens_used': total_tokens_used,
                'total_tickets': total_tickets
            }
        finally:
            db.close()
    
    def generate_ticket_id(self):
        """Generate a unique ticket ID in format TCKT-YYYYMMDD-XXX"""
        from datetime import datetime
        today = datetime.now().strftime("%Y%m%d")
        
        db = self.get_db_session()
        try:
            # Count tickets created today
            today_tickets = db.query(SupportTicket).filter(
                SupportTicket.ticket_id.like(f"TCKT-{today}-%")
            ).count()
            
            ticket_number = str(today_tickets + 1).zfill(3)
            return f"TCKT-{today}-{ticket_number}"
        finally:
            db.close()
    
    def create_support_ticket(self, session_id: str, issue_description: str, category: str = None, priority: str = "Medium"):
        """Create a new support ticket"""
        db = self.get_db_session()
        try:
            ticket_id = self.generate_ticket_id()
            
            ticket = SupportTicket(
                ticket_id=ticket_id,
                user_session_id=session_id,
                issue_description=issue_description,
                category=category,
                priority=priority,
                status='Open'
            )
            
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            return ticket
        finally:
            db.close()
    
    def get_ticket_by_id(self, ticket_id: str):
        """Get support ticket by ticket ID"""
        db = self.get_db_session()
        try:
            ticket = db.query(SupportTicket).filter(
                SupportTicket.ticket_id == ticket_id.upper()
            ).first()
            return ticket
        finally:
            db.close()
    
    def get_user_tickets(self, session_id: str):
        """Get all tickets for a user session"""
        db = self.get_db_session()
        try:
            tickets = db.query(SupportTicket).filter(
                SupportTicket.user_session_id == session_id
            ).order_by(SupportTicket.created_at.desc()).all()
            return tickets
        finally:
            db.close()
    
    def update_ticket_status(self, ticket_id: str, status: str, assigned_agent: str = None):
        """Update ticket status"""
        db = self.get_db_session()
        try:
            ticket = db.query(SupportTicket).filter(
                SupportTicket.ticket_id == ticket_id.upper()
            ).first()
            
            if ticket:
                ticket.status = status
                ticket.updated_at = datetime.utcnow()
                if assigned_agent:
                    ticket.assigned_agent = assigned_agent
                if status.lower() in ['resolved', 'closed']:
                    ticket.resolved_at = datetime.utcnow()
                
                db.commit()
                return ticket
            return None
        finally:
            db.close()

# Initialize database manager
@st.cache_resource
def get_database_manager():
    """Cached database manager instance"""
    return DatabaseManager()