"""Streamlit web interface for AI Email Assistant."""

import streamlit as st
import os
import sys
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.workflow.langgraph_flow import EmailWorkflow
from src.memory import ProfileManager
from src.core.context_manager import ContextManager
from src.core.export_manager import ExportManager
from src.core.state_models import ConversationEntry
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EmailAssistantUI:
    """Streamlit UI for Email Assistant."""
    
    def __init__(self):
        self.workflow = EmailWorkflow()
        self.profile_manager = ProfileManager()
        self.context_manager = ContextManager()
        self.export_manager = ExportManager()
        
        # Initialize session state
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'current_email' not in st.session_state:
            st.session_state.current_email = None
    
    def render_sidebar(self):
        """Render sidebar with configuration options."""
        st.sidebar.title("Configuration")
        
        # User Profile Selection
        st.sidebar.subheader("User Profile")
        profiles = self.profile_manager.list_profiles()
        
        user_type = st.sidebar.selectbox(
            "Select Profile",
            options=profiles,
            format_func=lambda x: x.replace('_', ' ').title(),
            help="Choose your professional profile"
        )
        
        # Display selected profile info
        profile = self.profile_manager.get_profile(user_type)
        if profile:
            with st.sidebar.expander("Profile Details"):
                st.write(f"**Role:** {profile.get('role', 'N/A')}")
                st.write(f"**Name:** {profile.get('name', 'N/A')}")
                if 'company' in profile:
                    st.write(f"**Company:** {profile['company']}")
                if 'institution' in profile:
                    st.write(f"**Institution:** {profile['institution']}")
        
        # Tone Selection
        st.sidebar.subheader("Email Tone")
        tone = st.sidebar.select_slider(
            "Select Tone",
            options=["very_formal", "formal", "professional", "friendly", "casual"],
            value="professional",
            help="Choose the tone for your email"
        )
        
        # Context Memory Toggle
        st.sidebar.subheader("Context Settings")
        enable_context = os.getenv('ENABLE_CONTEXT_MEMORY', 'true').lower() == 'true'
        use_context = st.sidebar.checkbox(
            "Use conversation history",
            value=enable_context,
            help="Include context from previous emails"
        )
        
        max_context = int(os.getenv('MAX_CONTEXT_ENTRIES', '3'))
        if use_context and st.session_state.conversation_history:
            st.sidebar.info(
                f"Using last {min(len(st.session_state.conversation_history), max_context)} emails as context"
            )
        
        # History Management
        st.sidebar.subheader("History")
        if st.session_state.conversation_history:
            st.sidebar.write(f"**Emails generated:** {len(st.session_state.conversation_history)}")
            if st.sidebar.button("Clear History"):
                st.session_state.conversation_history = []
                st.rerun()
        else:
            st.sidebar.write("No emails generated yet")
        
        return user_type, tone, use_context
    
    def render_main_content(self, user_type: str, tone: str, use_context: bool):
        """Render main content area."""
        st.title("AI-Powered Email Assistant")
        st.markdown("*Generate professional emails using multi-agent AI orchestration*")
        
        # Email Request Input
        st.subheader("What would you like to write?")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Initialize prompt state if not exists
            if 'email_prompt_value' not in st.session_state:
                st.session_state.email_prompt_value = ""
            
            email_prompt = st.text_area(
                "Describe your email request",
                value=st.session_state.email_prompt_value,
                height=150,
                placeholder="Example: Write a follow-up email to my professor asking about the research project deadline extension...",
                help="Describe what you want to communicate in the email"
            )
        
        with col2:
            st.markdown("**Quick Templates:**")
            templates = {
                "Follow-up": "Write a follow-up email about...",
                "Request": "Request information about...",
                "Thank you": "Thank someone for...",
                "Apology": "Apologize for...",
                "Introduction": "Introduce myself regarding...",
            }
            
            for name, template in templates.items():
                if st.button(name, use_container_width=True):
                    st.session_state.email_prompt_value = template
                    st.rerun()
        
        
        # Generate Button
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            generate_button = st.button(
                "Generate Email",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            if st.session_state.current_email:
                regenerate_button = st.button(
                    "Regenerate",
                    use_container_width=True
                )
            else:
                regenerate_button = False
        
        # Process email generation
        if generate_button or regenerate_button:
            if not email_prompt or email_prompt.strip() == "":
                st.warning("Please describe what you want to write about.")
            else:
                self.generate_email(email_prompt, user_type, tone, use_context)
        
        # Display generated email
        if st.session_state.current_email:
            self.display_email_result()
    
    def generate_email(self, prompt: str, user_type: str, tone: str, use_context: bool):
        """Generate email using the workflow."""
        with st.spinner("AI agents are crafting your email..."):
            try:
                # Prepare context
                context_summary = None
                if use_context and st.session_state.conversation_history:
                    context_summary = self.context_manager.get_context_summary(
                        st.session_state.conversation_history
                    )
                
                # Get user profile
                user_profile = self.profile_manager.get_profile(user_type)
                
                # Create initial state
                initial_state = {
                    "raw_prompt": prompt,
                    "tone": tone,
                    "user_type": user_type,
                    "user_profile": user_profile,
                    "context_history": context_summary,
                    "parsed_input": None,
                    "intent": None,
                    "tone_guidelines": None,
                    "draft": None,
                    "personalized_draft": None,
                    "review_feedback": None,
                    "review_passed": None,
                    "retry_count": 0,
                    "final_email": None,
                    "generation_metadata": None,
                }
                
                # Execute workflow
                result = self.workflow.generate_email(initial_state)
                
                # Store result
                st.session_state.current_email = {
                    "email": result.get("final_email", ""),
                    "metadata": result.get("generation_metadata", {}),
                    "intent": result.get("intent", ""),
                    "prompt": prompt,
                    "tone": tone,
                    "user_type": user_type,
                    "timestamp": datetime.now().isoformat(),
                }
                
                # Add to history
                history_entry = self.context_manager.create_history_entry(
                    prompt=prompt,
                    tone=tone,
                    user_type=user_type,
                    email=result.get("final_email", ""),
                    intent=result.get("intent", ""),
                    metadata=result.get("generation_metadata", {})
                )
                
                st.session_state.conversation_history = self.context_manager.add_to_history(
                    st.session_state.conversation_history,
                    history_entry
                )
                
                st.success("Email generated successfully!")
                
            except Exception as e:
                logger.error(f"Error generating email: {str(e)}")
                st.error(f"Error generating email: {str(e)}")
    
    def display_email_result(self):
        """Display the generated email with metadata."""
        st.subheader("Generated Email")
        
        email_data = st.session_state.current_email
        metadata = email_data.get("metadata", {})
        
        # Email content
        st.text_area(
            "Email Content",
            value=email_data["email"],
            height=400,
            help="Copy this email to use it"
        )
        
        # Metadata in expander
        with st.expander("Generation Details"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Profile:** {email_data['user_type'].replace('_', ' ').title()}")
                st.write(f"**Tone:** {email_data['tone'].replace('_', ' ').title()}")
                st.write(f"**Generated:** {email_data['timestamp'][:19]}")
            
            with col2:
                st.write(f"**Intent:** {email_data.get('intent', 'N/A')[:50]}...")
                
                # Review routing info
                review_passed = metadata.get("review_passed", True)
                retry_count = metadata.get("retry_count", 0)
                forced = metadata.get("forced_finalization", False)
                
                if forced:
                    st.write(f"**Review:** FAIL (forced after {retry_count} retries)")
                    st.warning("Email was finalized after max retries. Consider regenerating.")
                elif retry_count > 0:
                    st.write(f"**Review:** PASS (after {retry_count} retry{'ies' if retry_count > 1 else ''})")
                else:
                    st.write("**Review:** PASS (first draft)")
        
        # Export Options
        st.subheader("Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Copy to Clipboard", use_container_width=True):
                st.code(email_data["email"], language=None)
                st.info("Select and copy the text above")
        
        with col2:
            txt_export = self.export_manager.export_to_txt(
                email_data["email"],
                {
                    "timestamp": email_data["timestamp"],
                    "user_type": email_data["user_type"],
                    "tone": email_data["tone"],
                    "intent": email_data.get("intent", "N/A"),
                }
            )
            st.download_button(
                "Download TXT",
                data=txt_export,
                file_name=self.export_manager.create_filename("email", "txt"),
                mime="text/plain",
                use_container_width=True
            )
        
        with col3:
            json_export = self.export_manager.export_to_json(email_data)
            st.download_button(
                "Download JSON",
                data=json_export,
                file_name=self.export_manager.create_filename("email", "json"),
                mime="application/json",
                use_container_width=True
            )
    
    def run(self):
        """Run the Streamlit application."""
        st.set_page_config(
            page_title=os.getenv('APP_TITLE', 'AI Email Assistant'),
            page_icon="✉️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
        }
        .stTextArea textarea {
            font-family: monospace;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Render UI components
        user_type, tone, use_context = self.render_sidebar()
        self.render_main_content(user_type, tone, use_context)
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: gray;'>"
            "AI Email Assistant v0.1.0 | Powered by LangGraph & GPT-4o-mini"
            "</div>",
            unsafe_allow_html=True
        )


def main():
    """Main entry point for Streamlit app."""
    app = EmailAssistantUI()
    app.run()


if __name__ == "__main__":
    main()
