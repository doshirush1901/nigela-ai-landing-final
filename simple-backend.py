#!/usr/bin/env python3
"""
Simple backend to save Nigela AI signups directly to local files
"""

import os
import csv
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading

class NigelaSignupHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/save-signup':
            try:
                # Read POST data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                email = data.get('email', '').strip()
                
                if email and '@' in email:
                    # Save to files in Nigela folder
                    self.save_signup_to_nigela_folder(email)
                    
                    # Send success response
                    self.send_cors_response(200, {'success': True, 'message': 'Saved to Nigela folder'})
                    print(f"✅ Saved email to Nigela folder: {email}")
                else:
                    self.send_cors_response(400, {'error': 'Invalid email'})
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                self.send_cors_response(500, {'error': str(e)})
        else:
            self.send_cors_response(404, {'error': 'Not found'})
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_cors_response(200, {})
    
    def send_cors_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def save_signup_to_nigela_folder(self, email):
        # Save to the main Nigela folder (go up one level)
        nigela_folder = os.path.join(os.path.dirname(os.getcwd()), 'Nigela')
        signup_file = os.path.join(nigela_folder, 'client_signups.csv')
        json_file = os.path.join(nigela_folder, 'client_signups.json')
        
        # Create signup data
        signup_data = {
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'source': 'superchefnigela_website',
            'location': 'Mumbai',
            'ip': self.client_address[0] if self.client_address else 'unknown'
        }
        
        # Save to CSV
        file_exists = os.path.exists(signup_file)
        with open(signup_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Email', 'Timestamp', 'Source', 'Location', 'IP'])
            writer.writerow([
                signup_data['email'],
                signup_data['timestamp'], 
                signup_data['source'],
                signup_data['location'],
                signup_data['ip']
            ])
        
        # Save to JSON
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                signups = json.load(f)
        else:
            signups = []
        
        # Add if not duplicate
        if not any(s['email'] == email for s in signups):
            signups.append(signup_data)
            with open(json_file, 'w') as f:
                json.dump(signups, f, indent=2)
        
        print(f"📁 Saved to Nigela folder: {signup_file}")
        print(f"📊 Total signups: {len(signups)}")

def start_server():
    server_address = ('localhost', 3001)
    httpd = HTTPServer(server_address, NigelaSignupHandler)
    
    print("🚀 Nigela Signup Server Started!")
    print("📡 URL: http://localhost:3001/save-signup")
    print("📁 Saving to: ../Nigela/ folder")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    start_server()
