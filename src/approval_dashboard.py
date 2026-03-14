"""
Piddy Approval Dashboard - Web UI for market gap review

Allows users to:
1. View pending market gaps
2. Review security concerns
3. Approve or disapprove gaps
4. Set rejection reasons for high-risk agents

Runs on http://localhost:8000 by default
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("⚠️  FastAPI not installed. Dashboard will run in demo mode.")
    FastAPI = None


class ApprovalDashboard:
    """
    Web dashboard for reviewing and approving market gaps
    
    Serves both UI and API endpoints
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.approval_decisions: Dict[str, Dict] = {}
        self.approval_data_path = Path("data/approval_decisions.json")
        self.approval_data_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_decisions()
        
        if FastAPI:
            self.app = self._create_app()
        else:
            self.app = None
    
    def _load_decisions(self):
        """Load previous approval decisions from file"""
        if self.approval_data_path.exists():
            try:
                with open(self.approval_data_path, 'r') as f:
                    self.approval_decisions = json.load(f)
            except:
                self.approval_decisions = {}
    
    def _save_decisions(self):
        """Save approval decisions to file"""
        with open(self.approval_data_path, 'w') as f:
            json.dump(self.approval_decisions, f, indent=2)
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application with routes"""
        app = FastAPI(title="Piddy Approval Dashboard")
        
        # Enable CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            """Serve main dashboard UI"""
            return self._render_dashboard_html()
        
        @app.get("/approvals/{request_id}", response_class=HTMLResponse)
        async def view_approval(request_id: str):
            """View specific approval request"""
            return self._render_approval_html(request_id)
        
        @app.get("/api/approvals/{request_id}")
        async def get_approval_status(request_id: str):
            """Get approval request status via API"""
            # This would connect to the reporter
            return {
                "request_id": request_id,
                "status": "pending",
                "message": "Connect to market_gap_reporter for live data"
            }
        
        @app.post("/api/approvals/{request_id}/gaps/{gap_id}/approve")
        async def approve_gap(request_id: str, gap_id: str):
            """Approve a gap for building"""
            self.approval_decisions[f"{request_id}_{gap_id}"] = {
                "approved": True,
                "timestamp": datetime.now().isoformat(),
            }
            self._save_decisions()
            return {
                "status": "approved",
                "request_id": request_id,
                "gap_id": gap_id,
            }
        
        @app.post("/api/approvals/{request_id}/gaps/{gap_id}/reject")
        async def reject_gap(request_id: str, gap_id: str, reason: str = ""):
            """Reject a gap from building"""
            self.approval_decisions[f"{request_id}_{gap_id}"] = {
                "approved": False,
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
            }
            self._save_decisions()
            return {
                "status": "rejected",
                "request_id": request_id,
                "gap_id": gap_id,
                "reason": reason,
            }
        
        @app.get("/api/decisions")
        async def get_all_decisions():
            """Get all approval decisions made"""
            return self.approval_decisions
        
        return app
    
    def _render_dashboard_html(self) -> str:
        """Render main dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Piddy Approval Dashboard</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #f5f5f5;
                    padding: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                header {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #1a73e8;
                    margin-bottom: 10px;
                }
                .subtitle {
                    color: #666;
                    font-size: 16px;
                }
                .status-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }
                .status-card {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .status-card h3 {
                    color: #666;
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 10px;
                }
                .status-number {
                    font-size: 32px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .pending { color: #f57c00; }
                .approved { color: #4caf50; }
                .rejected { color: #d32f2f; }
                
                .section {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .section h2 {
                    color: #333;
                    margin-bottom: 20px;
                    font-size: 20px;
                    border-bottom: 2px solid #f5f5f5;
                    padding-bottom: 10px;
                }
                .request-link {
                    display: block;
                    padding: 15px;
                    margin-bottom: 10px;
                    background: #f9f9f9;
                    border-left: 4px solid #1a73e8;
                    border-radius: 4px;
                    text-decoration: none;
                    color: #1a73e8;
                    transition: all 0.2s;
                }
                .request-link:hover {
                    background: #f0f0f0;
                    transform: translateX(5px);
                }
                .info-box {
                    background: #e3f2fd;
                    border-left: 4px solid #1a73e8;
                    padding: 15px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .button {
                    display: inline-block;
                    padding: 10px 20px;
                    background: #1a73e8;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-top: 10px;
                    transition: all 0.2s;
                }
                .button:hover {
                    background: #0d47a1;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🤖 Piddy Approval Dashboard</h1>
                    <p class="subtitle">Review and approve autonomous agent builds</p>
                </header>
                
                <div class="section">
                    <h2>Overview</h2>
                    <div class="status-grid">
                        <div class="status-card">
                            <h3>Pending Approvals</h3>
                            <div class="status-number pending" id="pending-count">0</div>
                        </div>
                        <div class="status-card">
                            <h3>Approved</h3>
                            <div class="status-number approved" id="approved-count">0</div>
                        </div>
                        <div class="status-card">
                            <h3>Rejected</h3>
                            <div class="status-number rejected" id="rejected-count">0</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Pending Market Gap Requests</h2>
                    <div class="info-box">
                        <strong>ℹ️ How it works:</strong>
                        <p>When market gaps are identified, they're sent to your email with a unique approval link. 
                        Click a request below to review security concerns and approve or disapprove the agents.</p>
                    </div>
                    <div id="requests-container">
                        <p style="color: #999;">No pending approvals</p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Instructions</h2>
                    <ol style="line-height: 1.8; color: #555;">
                        <li>Check your email for new market gap reports</li>
                        <li>Click the approval link in the email</li>
                        <li>Review each gap's security concerns</li>
                        <li>
                            <strong>For HIGH RISK gaps:</strong> Provide a reason if you're disapproving
                        </li>
                        <li>Click "Approve" to authorize building, or "Reject" to skip</li>
                        <li>Approved gaps will be autonomously built within 1 hour</li>
                    </ol>
                </div>
            </div>
            
            <script>
                async function loadDecisions() {
                    try {
                        const response = await fetch('/api/decisions');
                        const decisions = await response.json();
                        
                        let pending = 0, approved = 0, rejected = 0;
                        
                        for (const key in decisions) {
                            if (decisions[key].approved) approved++;
                            else rejected++;
                        }
                        
                        document.getElementById('pending-count').textContent = pending;
                        document.getElementById('approved-count').textContent = approved;
                        document.getElementById('rejected-count').textContent = rejected;
                    } catch(e) {
                        console.log('Dashboard demo mode - decisions not yet available');
                    }
                }
                
                loadDecisions();
                setInterval(loadDecisions, 5000);
            </script>
        </body>
        </html>
        """
    
    def _render_approval_html(self, request_id: str) -> str:
        """Render approval UI for specific request"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Approve Market Gaps - Piddy</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #f5f5f5;
                    padding: 20px;
                }}
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                }}
                header {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{ color: #1a73e8; margin-bottom: 10px; }}
                .gap-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-left: 4px solid #ddd;
                }}
                .gap-card.high-risk {{ border-left-color: #d32f2f; }}
                .gap-card.medium-risk {{ border-left-color: #ff9800; }}
                .gap-card.low-risk {{ border-left-color: #4caf50; }}
                .risk-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    color: white;
                    font-size: 12px;
                    margin-bottom: 10px;
                }}
                .risk-high {{ background: #d32f2f; }}
                .risk-medium {{ background: #ff9800; }}
                .risk-low {{ background: #4caf50; }}
                .gap-title {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 8px; }}
                .gap-description {{ color: #666; margin-bottom: 15px; }}
                .security-concerns {{
                    background: #fff3cd;
                    border-left: 3px solid #ff9800;
                    padding: 12px;
                    margin: 15px 0;
                    border-radius: 4px;
                }}
                .security-concerns ul {{ margin-left: 20px; color: #555; }}
                .security-concerns li {{ margin-bottom: 5px; }}
                .action-buttons {{
                    display: flex;
                    gap: 10px;
                    margin-top: 15px;
                }}
                .btn {{
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: bold;
                    transition: all 0.2s;
                }}
                .btn-approve {{
                    background: #4caf50;
                    color: white;
                }}
                .btn-approve:hover {{
                    background: #388e3c;
                }}
                .btn-reject {{
                    background: #f44336;
                    color: white;
                }}
                .btn-reject:hover {{
                    background: #d32f2f;
                }}
                .info-box {{
                    background: #e3f2fd;
                    border-left: 4px solid #1a73e8;
                    padding: 15px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }}
                .rejection-form {{
                    display: none;
                    margin-top: 10px;
                    padding: 10px;
                    background: #fff3cd;
                    border-radius: 4px;
                }}
                textarea {{
                    width: 100%;
                    min-height: 80px;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-family: inherit;
                }}
                .request-id {{
                    color: #999;
                    font-size: 12px;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🔍 Market Gap Review</h1>
                    <p>Approve or reject autonomously proposed agents</p>
                    <p class="request-id">Request ID: {request_id}</p>
                </header>
                
                <div class="info-box">
                    <strong>⚠️  Important:</strong>
                    <ul>
                        <li>Review security concerns carefully, especially for HIGH RISK agents</li>
                        <li>HIGH RISK agents require explicit approval despite risk level</li>
                        <li>Approved gaps will be built within 1 hour</li>
                        <li>Disapproved gaps will not be built</li>
                    </ul>
                </div>
                
                <div id="gaps-container">
                    <p style="text-align: center; color: #999;">Loading gaps...</p>
                </div>
            </div>
            
            <script>
                const requestId = "{request_id}";
                
                // In real implementation, this would fetch from /api/approvals/{{request_id}}
                // For demo, show instructions
                document.getElementById('gaps-container').innerHTML = `
                    <div style="background: white; padding: 30px; border-radius: 8px; text-align: center;">
                        <h3 style="color: #333; margin-bottom: 15px;">Approval Dashboard</h3>
                        <p style="color: #666; margin-bottom: 20px;">
                            This dashboard will display specific gaps from request: <br/>
                            <code style="background: #f0f0f0; padding: 5px 10px; border-radius: 4px; display: inline-block; margin-top: 10px;">{{requestId}}</code>
                        </p>
                        <p style="color: #999;">
                            Connect to market_gap_reporter instance to load live approval data
                        </p>
                        <a href="/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #1a73e8; color: white; text-decoration: none; border-radius: 4px;">
                            Back to Dashboard
                        </a>
                    </div>
                `;
            </script>
        </body>
        </html>
        """
    
    async def run(self):
        """Run the dashboard server"""
        if not self.app:
            print("⚠️  FastAPI not installed. Installing...")
            import subprocess
            subprocess.run(["pip", "install", "fastapi", "uvicorn"], check=True)
            self.app = self._create_app()
        
        print(f"\n🖥️  APPROVAL DASHBOARD STARTED")
        print(f"   URL: http://{self.host}:{self.port}")
        print(f"   Email approvals will link here")
        print(f"   Dashboard will wait for user approvals")
        
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


async def main():
    """Run dashboard in demo mode"""
    dashboard = ApprovalDashboard()
    await dashboard.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✋ Dashboard stopped")
