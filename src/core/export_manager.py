"""Export functionality for emails and data."""

import json
from datetime import datetime
from typing import Dict, Any, Optional


class ExportManager:
    """Handles export operations for emails and metadata."""
    
    @staticmethod
    def export_to_txt(email_content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Export email content to text format."""
        output = []
        
        if metadata:
            output.append("=" * 60)
            output.append("EMAIL METADATA")
            output.append("=" * 60)
            output.append(f"Generated: {metadata.get('timestamp', 'N/A')}")
            output.append(f"Profile: {metadata.get('user_type', 'N/A')}")
            output.append(f"Tone: {metadata.get('tone', 'N/A')}")
            output.append(f"Intent: {metadata.get('intent', 'N/A')}")
            output.append("")
            output.append("=" * 60)
            output.append("EMAIL CONTENT")
            output.append("=" * 60)
        
        output.append(email_content)
        
        return "\n".join(output)
    
    @staticmethod
    def export_to_json(email_data: Dict[str, Any]) -> str:
        """Export email data to JSON format."""
        export_data = {
            "export_metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "format": "ai-email-assistant-export"
            },
            "email_data": email_data
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def create_filename(base_name: str, extension: str) -> str:
        """Create timestamped filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{extension}"
