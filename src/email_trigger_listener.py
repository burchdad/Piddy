#!/usr/bin/env python3
"""
📧 Email Trigger Listener - Monitor Emails for Approval Requests

Monitors incoming emails for market gap reports and automatically:
1. Extracts gap details from email
2. Creates approval request
3. Triggers email notifications to approvers
4. Logs all activities

Usage:
    python src/email_trigger_listener.py --start          # Start listener daemon
    python src/email_trigger_listener.py --test-email     # Send test email
    python src/email_trigger_listener.py --check-mailbox  # Check mailbox once
"""

import os
import sys
import json
import time
import argparse
import logging
import imaplib
import email
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from email.parser import Parser
from email.header import decode_header
from abc import ABC, abstractmethod
import signal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/email_trigger.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GapParser(ABC):
    """Abstract base for parsing gaps from email content"""
    
    @abstractmethod
    def can_parse(self, email_subject: str) -> bool:
        """Check if this parser can handle the email"""
        pass
    
    @abstractmethod
    def parse(self, email_subject: str, email_body: str) -> Optional[Dict]:
        """Parse the gap from email content"""
        pass


class PiddyMarketGapParser(GapParser):
    """Parser for Piddy market gap report emails"""
    
    def can_parse(self, email_subject: str) -> bool:
        """Check if this is a Piddy market gap report email"""
        return "market gap report" in email_subject.lower() or "gap detected" in email_subject.lower()
    
    def parse(self, email_subject: str, email_body: str) -> Optional[Dict]:
        """Parse Piddy market gap report email"""
        try:
            # Look for JSON in email body
            json_match = re.search(r'\{.*"gap_id".*\}', email_body, re.DOTALL)
            if json_match:
                gap_data = json.loads(json_match.group())
                return gap_data
            
            # Fall back to parsing from text
            gap_data = {
                "gap_id": self._extract_field(email_body, "Gap ID"),
                "title": self._extract_field(email_body, "Title") or self._extract_from_subject(email_subject),
                "category": self._extract_field(email_body, "Category") or "feature",
                "market_need": self._extract_field(email_body, "Market Need") or "Detected market gap",
                "frequency": self._extract_number(email_body, "Frequency") or 1,
                "estimated_impact": self._extract_float(email_body, "Impact") or 0.5,
                "complexity_score": self._extract_number(email_body, "Complexity") or 5,
                "estimated_build_time_hours": self._extract_float(email_body, "Build Time") or 8.0,
                "security_risk_level": self._extract_risk_level(email_body) or "MEDIUM",
                "security_concerns": self._extract_concerns(email_body),
                "integration_points": self._extract_integration_points(email_body),
            }
            
            return gap_data if gap_data.get("gap_id") else None
        except Exception as e:
            logger.error(f"Error parsing gap email: {e}")
            return None
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract field from email body"""
        pattern = f"{field_name}[:\\s]*([^\\n]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _extract_number(self, text: str, field_name: str) -> Optional[int]:
        """Extract number field"""
        value = self._extract_field(text, field_name)
        if value:
            match = re.search(r'\d+', value)
            return int(match.group()) if match else None
        return None
    
    def _extract_float(self, text: str, field_name: str) -> Optional[float]:
        """Extract float field"""
        value = self._extract_field(text, field_name)
        if value:
            match = re.search(r'\d+\.?\d*', value)
            return float(match.group()) if match else None
        return None
    
    def _extract_risk_level(self, text: str) -> Optional[str]:
        """Extract security risk level"""
        for level in ["HIGH", "MEDIUM", "LOW"]:
            if level in text.upper():
                return level
        return None
    
    def _extract_from_subject(self, subject: str) -> str:
        """Extract title from subject line"""
        # Remove common prefixes
        subject = re.sub(r'^(re:|fwd:|\[.*?\])', '', subject, flags=re.IGNORECASE)
        return subject.strip()
    
    def _extract_concerns(self, text: str) -> List[str]:
        """Extract security concerns"""
        concerns = []
        if "security" in text.lower():
            # Look for bullet points or lines with security keywords
            lines = text.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ["security", "concern", "risk", "vulnerability"]):
                    concern = line.strip().lstrip('•-* ')
                    if concern and len(concern) > 5:
                        concerns.append(concern)
        return concerns[:5]  # Limit to 5 concerns
    
    def _extract_integration_points(self, text: str) -> List[str]:
        """Extract integration points"""
        integration_keywords = ["api", "database", "service", "module", "system", "component"]
        points = []
        
        if "integration" in text.lower():
            lines = text.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in integration_keywords):
                    point = line.strip().lstrip('•-* ')
                    if point and len(point) > 3:
                        points.append(point)
        
        return points[:5]  # Limit to 5


class EmailTriggerListener:
    """Listen for incoming emails and trigger approval workflows"""
    
    def __init__(self):
        """Initialize listener"""
        self.parsers: List[GapParser] = [PiddyMarketGapParser()]
        self.config = self._load_email_config()
        self.running = False
    
    def _load_email_config(self) -> Dict:
        """Load email configuration"""
        config_file = Path("config/email_config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "imap_server": os.getenv("IMAP_SERVER", "imap.gmail.com"),
            "imap_port": int(os.getenv("IMAP_PORT", "993")),
            "email": os.getenv("EMAIL_ADDRESS", ""),
            "password": os.getenv("EMAIL_PASSWORD", ""),
            "use_tls": True
        }
    
    def check_mailbox_once(self) -> int:
        """Check mailbox once and process new emails"""
        logger.info("Checking mailbox for market gap reports...")
        
        if not self.config.get("email"):
            logger.error("Email not configured in config/email_config.json")
            return 0
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.config["imap_server"], self.config["imap_port"])
            mail.login(self.config["email"], self.config["password"])
            mail.select("INBOX")
            
            # Search for unread emails from Piddy reports
            status, email_ids = mail.search(None, 'UNSEEN SUBJECT "market gap"')
            
            if status != "OK":
                logger.warning("Failed to search mailbox")
                mail.close()
                mail.logout()
                return 0
            
            processed_count = 0
            email_list = email_ids[0].split()
            
            logger.info(f"Found {len(email_list)} potential market gap emails")
            
            for email_id in email_list:
                try:
                    # Fetch email
                    status, email_data = mail.fetch(email_id, "(RFC822)")
                    if status != "OK":
                        continue
                    
                    # Parse email
                    raw_email = email_data[0][1]
                    msg = Parser().parsestr(raw_email.decode('utf-8'))
                    
                    # Extract subject and body
                    subject = self._decode_header(msg["Subject"])
                    sender = msg["From"]
                    body = self._extract_body(msg)
                    
                    logger.info(f"Processing email from {sender}: {subject}")
                    
                    # Try to parse gap from email
                    gap = self._parse_email_for_gap(subject, body)
                    
                    if gap:
                        logger.info(f"✅ Extracted gap: {gap.get('gap_id')} - {gap.get('title')}")
                        
                        # Create approval request from gap
                        success = self._create_approval_from_gap(gap)
                        
                        if success:
                            processed_count += 1
                            # Mark email as read
                            mail.store(email_id, '+FLAGS', '\\Seen')
                            logger.info(f"✓ Approval request created for gap {gap.get('gap_id')}")
                    else:
                        logger.warning(f"Could not parse gap from email: {subject}")
                
                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {e}")
            
            mail.close()
            mail.logout()
            
            logger.info(f"Processed {processed_count} market gap emails")
            return processed_count
        
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error checking mailbox: {e}")
            return 0
    
    def start_daemon(self, interval: int = 300):
        """Start listening daemon (check mailbox every interval seconds)"""
        logger.info(f"Starting email trigger listener (checking every {interval}s)")
        
        self.running = True
        check_count = 0
        
        while self.running:
            try:
                check_count += 1
                logger.info(f"[Check #{check_count}] Scanning for market gap emails...")
                
                processed = self.check_mailbox_once()
                
                if processed > 0:
                    logger.info(f"✅ Processed {processed} market gap reports")
                
                # Wait for next check
                time.sleep(interval)
            
            except KeyboardInterrupt:
                logger.info("Listener interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in listener loop: {e}")
                time.sleep(interval)  # Wait before retrying
        
        logger.info("Email trigger listener stopped")
    
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ""
        
        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                decoded_parts.append(part.decode(encoding or 'utf-8', errors='ignore'))
            else:
                decoded_parts.append(str(part))
        
        return ''.join(decoded_parts)
    
    def _extract_body(self, msg) -> str:
        """Extract text body from email"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors='ignore')
                    break
                elif part.get_content_type() == "text/html":
                    body = part.get_payload(decode=True).decode(errors='ignore')
        else:
            body = msg.get_payload(decode=True).decode(errors='ignore')
        
        return body[:5000]  # Limit to first 5000 chars
    
    def _parse_email_for_gap(self, subject: str, body: str) -> Optional[Dict]:
        """Parse email for market gap information"""
        for parser in self.parsers:
            if parser.can_parse(subject):
                gap = parser.parse(subject, body)
                if gap:
                    return gap
        return None
    
    def _create_approval_from_gap(self, gap: Dict) -> bool:
        """Create approval request from parsed gap"""
        try:
            # Load existing workflow state
            workflow_file = Path("data/approval_workflow_state.json")
            
            if workflow_file.exists():
                with open(workflow_file, 'r') as f:
                    workflow_state = json.load(f)
            else:
                workflow_state = {"requests": {}}
            
            # Create new approval request
            request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            approval_request = {
                "request_id": request_id,
                "gaps": [gap],
                "created_at": datetime.utcnow().isoformat(),
                "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "status": "waiting",
                "sent_to_emails": self._get_approver_emails(),
                "high_risk_count": 1 if gap.get("security_risk_level") == "HIGH" else 0,
                "medium_risk_count": 1 if gap.get("security_risk_level") == "MEDIUM" else 0,
                "low_risk_count": 1 if gap.get("security_risk_level") == "LOW" else 0,
            }
            
            # Add to workflow state
            workflow_state["requests"][request_id] = approval_request
            
            # Save updated state
            with open(workflow_file, 'w') as f:
                json.dump(workflow_state, f, indent=2)
            
            logger.info(f"Created approval request {request_id}")
            
            # Trigger email notification to approvers
            self._send_approval_notification(approval_request)
            
            return True
        
        except Exception as e:
            logger.error(f"Error creating approval request: {e}")
            return False
    
    def _get_approver_emails(self) -> List[str]:
        """Get list of approver emails"""
        # Check environment variables for approver emails
        approver_emails = []
        
        if os.getenv("APPROVER_EMAILS"):
            approver_emails = os.getenv("APPROVER_EMAILS").split(",")
        elif os.getenv("USER_EMAIL"):
            approver_emails = [os.getenv("USER_EMAIL")]
        else:
            approver_emails = [self.config.get("email", "")]
        
        return [email.strip() for email in approver_emails if email.strip()]
    
    def _send_approval_notification(self, request: Dict) -> bool:
        """Send notification about new approval request"""
        try:
            # This would integrate with src/market_gap_reporter.py email sending
            logger.info(f"Would send approval notification to {request.get('sent_to_emails')}")
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    def stop(self):
        """Stop the listener daemon"""
        logger.info("Stopping email trigger listener...")
        self.running = False


def main():
    parser = argparse.ArgumentParser(
        description="📧 Email Trigger Listener - Automatic approval workflow from emails"
    )
    
    parser.add_argument("--start", action="store_true",
                       help="Start listener daemon (run in background)")
    parser.add_argument("--check-mailbox", action="store_true",
                       help="Check mailbox once and process emails")
    parser.add_argument("--interval", type=int, default=300,
                       help="Check interval in seconds (default: 300)")
    parser.add_argument("--test-email", action="store_true",
                       help="Send test market gap email (requires configured email)")
    
    args = parser.parse_args()
    
    listener = EmailTriggerListener()
    
    if args.check_mailbox:
        listener.check_mailbox_once()
    elif args.start:
        try:
            def signal_handler(sig, frame):
                listener.stop()
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            listener.start_daemon(interval=args.interval)
        except KeyboardInterrupt:
            listener.stop()
    elif args.test_email:
        print("Test email feature not yet implemented")
        print("To test: send an email with 'market gap' in subject to your configured email")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
