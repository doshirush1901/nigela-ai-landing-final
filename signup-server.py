#!/usr/bin/env python3
"""
Simple server to save email signups to local files
Run this alongside your website to capture signups
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import csv
import os
from datetime import datetime
from urllib.parse import parse_qs
import threading

class SignupHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/signup':
            try:
                # Get content length
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                # Parse form data
                form_data = parse_qs(post_data)
                email = form_data.get('email', [''])[0]
                
                if email and '@' in email:
                    # Save to CSV file
                    self.save_signup(email)
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {'success': True, 'message': 'Email saved successfully'}
                    self.wfile.write(json.dumps(response).encode())
                    
                    print(f"✅ Saved email: {email}")
                else:
                    self.send_error(400, "Invalid email")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not found")
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def save_signup(self, email):
        # Create signups directory if it doesn't exist
        signup_dir = "client registration data"
        os.makedirs(signup_dir, exist_ok=True)
        
        # Prepare signup data
        signup_data = {
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'source': 'superchefnigela_website',
            'location': 'Mumbai'
        }
        
        # Save to CSV file
        csv_file = os.path.join(signup_dir, 'nigela_beta_signups.csv')
        
        # Check if file exists and has header
        file_exists = os.path.exists(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header if new file
            if not file_exists:
                writer.writerow(['Email', 'Timestamp', 'Source', 'Location'])
            
            # Write signup data
            writer.writerow([
                signup_data['email'],
                signup_data['timestamp'],
                signup_data['source'],
                signup_data['location']
            ])
        
        # Also save as JSON for backup
        json_file = os.path.join(signup_dir, 'signups.json')
        
        # Load existing signups
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                signups = json.load(f)
        else:
            signups = []
        
        # Add new signup if not duplicate
        if not any(s['email'] == email for s in signups):
            signups.append(signup_data)
            
            # Save updated JSON
            with open(json_file, 'w') as f:
                json.dump(signups, f, indent=2)
        
        print(f"📁 Saved to: {csv_file}")
        print(f"📊 Total signups: {len(signups)}")

def start_server():
    server_address = ('localhost', 3001)
    httpd = HTTPServer(server_address, SignupHandler)
    
    print("🚀 Nigela Signup Server Started!")
    print("📡 Listening on: http://localhost:3001")
    print("📁 Saving signups to: client registration data/")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    start_server()
