"""API endpoints for response retrieval."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from src.services.response_storage import get_response_storage
import logging


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/responses", tags=["responses"])


@router.get("/{response_id}", response_class=HTMLResponse)
async def get_response_html(response_id: str):
    """
    Get a stored response as HTML for viewing in browser.
    
    Args:
        response_id: The response ID
        
    Returns:
        HTML page with formatted response
    """
    storage = get_response_storage()
    response_data = storage.get_response(response_id)
    
    if not response_data:
        raise HTTPException(status_code=404, detail=f"Response not found: {response_id}")
    
    content = response_data.get("content", "")
    metadata = response_data.get("metadata", {})
    
    # Format metadata for display
    metadata_html = ""
    if metadata:
        metadata_html = "<div style='background-color: #f5f5f5; padding: 10px; margin-bottom: 20px; border-radius: 5px;'>"
        metadata_html += "<strong>Metadata:</strong><br>"
        for key, value in metadata.items():
            metadata_html += f"<em>{key}:</em> {value}<br>"
        metadata_html += "</div>"
    
    # Escape HTML in content
    import html
    content_html = html.escape(content)
    
    # Format as preformatted text with syntax highlighting for code blocks
    content_html = content_html.replace("\n```", "\n</pre>").replace("```\n", "<pre>")
    content_html = f"<pre style='background-color: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto;'>{content_html}</pre>"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Piddy Response</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
                color: #333;
            }}
            h1 {{
                color: #0366d6;
                border-bottom: 2px solid #0366d6;
                padding-bottom: 10px;
            }}
            pre {{
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 16px;
                overflow-x: auto;
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 13px;
            }}
            .metadata {{
                background-color: #f6f8fa;
                padding: 12px;
                border-left: 4px solid #0366d6;
                margin-bottom: 20px;
                border-radius: 3px;
            }}
            .metadata em {{
                color: #0366d6;
                font-style: normal;
                font-weight: 600;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e1e4e8;
                color: #666;
                text-align: center;
                font-size: 12px;
            }}
            .copy-button {{
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 14px;
                margin-bottom: 10px;
            }}
            .copy-button:hover {{
                background-color: #218838;
            }}
        </style>
    </head>
    <body>
        <h1>🤖 Piddy Response</h1>
        {metadata_html}
        <button class="copy-button" onclick="copyToClipboard()">📋 Copy to Clipboard</button>
        {content_html}
        <div class="footer">
            <p>This response will be automatically deleted after 7 days.</p>
        </div>
        <script>
            function copyToClipboard() {{
                const text = document.querySelector('pre').innerText;
                navigator.clipboard.writeText(text).then(() => {{
                    alert('Copied to clipboard!');
                }}).catch(err => {{
                    console.error('Failed to copy:', err);
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    return html_content


@router.get("/{response_id}/raw")
async def get_response_raw(response_id: str):
    """
    Get a stored response as raw text.
    
    Args:
        response_id: The response ID
        
    Returns:
        Raw response text
    """
    storage = get_response_storage()
    response_data = storage.get_response(response_id)
    
    if not response_data:
        raise HTTPException(status_code=404, detail=f"Response not found: {response_id}")
    
    return {
        "content": response_data.get("content", ""),
        "metadata": response_data.get("metadata", {}),
        "length": response_data.get("length", 0),
        "created_at": response_data.get("created_at", 0)
    }
