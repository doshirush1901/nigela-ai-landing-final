#!/usr/bin/env python3
"""
Local server to save Nigela AI signups directly to the Nigela cursor folder
Run this alongside your website to capture all signups locally
"""

import os
import csv
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import threading

class NigelaLocalHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/save-email':
            try:
                # Read form data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                # Parse form data (either JSON or form-encoded)
                try:
                    data = json.loads(post_data)
                    email = data.get('email', '')
                except:
                    # Try form-encoded data
                    form_data = parse_qs(post_data)
                    email = form_data.get('email', [''])[0]
                
                if email and '@' in email:
                    # Save to Nigela cursor folder
                    self.save_to_nigela_folder(email)
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {'success': True, 'message': f'Email {email} saved to Nigela folder'}
                    self.wfile.write(json.dumps(response).encode())
                    
                    print(f"✅ SAVED: {email} → Nigela folder")
                else:
                    self.send_error(400, "Invalid email")
                    
            except Exception as e:
                print(f"❌ Error saving email: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_OPTIONS(self):
        # Handle CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def save_to_nigela_folder(self, email):
        # Save directly to the main Nigela cursor folder
        nigela_path = "/Users/rushabhdoshi/Desktop/Nigela"
        
        # Create signup data
        signup_data = {
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'source': 'snazzy_kleicha_website',
            'location': 'Mumbai',
            'ip': self.client_address[0] if self.client_address else 'localhost'
        }
        
        # Save to CSV in Nigela folder
        csv_file = os.path.join(nigela_path, 'nigela_beta_signups.csv')
        
        # Create CSV with header if doesn't exist
        file_exists = os.path.exists(csv_file)
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
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
        
        # Also save as JSON backup in Nigela folder
        json_file = os.path.join(nigela_path, 'nigela_beta_signups.json')
        
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                signups = json.load(f)
        else:
            signups = []
        
        # Add new signup if not duplicate
        if not any(s['email'] == email for s in signups):
            signups.append(signup_data)
            with open(json_file, 'w') as f:
                json.dump(signups, f, indent=2)
        
        print(f"📁 Files saved to: {nigela_path}")
        print(f"📊 CSV: {csv_file}")
        print(f"📋 JSON: {json_file}")
        print(f"📈 Total signups: {len(signups)}")
        print("-" * 50)

def start_server():
    server_address = ('localhost', 3001)
    httpd = HTTPServer(server_address, NigelaLocalHandler)
    
    print("🚀 Nigela Local File Server Started!")
    print("=" * 50)
    print("📡 Listening on: http://localhost:3001/save-email")
    print("📁 Saving files to: /Users/rushabhdoshi/Desktop/Nigela/")
    print("📄 CSV file: nigela_beta_signups.csv")
    print("📋 JSON backup: nigela_beta_signups.json")
    print("⏹️  Press Ctrl+C to stop server")
    print("=" * 50)
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Local file server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    start_server()
