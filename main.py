import http.server
import json
import traceback
from cv_api import generate_html, generate_pdf
from linkedin_api import scrape_linkedin_jobs

class UnifiedHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b""
        
        try:
            payload = json.loads(post_data.decode('utf-8')) if post_data else {}
            
            if self.path == '/api/cv':
                if not payload.get("name") or not isinstance(payload.get("name"), str):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Validation failed: 'name' is required and must be a string."}).encode('utf-8'))
                    return

                html_content = generate_html(payload)
                with open('resume.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)

                pdf_data = generate_pdf(payload)

                custom_filename = payload.get("filename")
                if custom_filename and isinstance(custom_filename, str) and custom_filename.strip():
                    pdf_filename = custom_filename.strip()
                    if not pdf_filename.lower().endswith('.pdf'):
                        pdf_filename += '.pdf'
                else:
                    safe_name = ''.join(c if c.isalnum() or c in (' ', '_', '-') else '' for c in payload.get('name', 'CV'))
                    safe_name = safe_name.replace(' ', '_').strip('_') or 'CV'
                    pdf_filename = f"CV_{safe_name}.pdf"

                self.send_response(200)
                self.send_header('Content-type', 'application/pdf')
                self.send_header('Content-Disposition', f'attachment; filename="{pdf_filename}"')
                self.end_headers()
                self.wfile.write(pdf_data)
                
            elif self.path == '/api/scrape':
                query = payload.get("query", "")
                location = payload.get("location", "")
                max_rows = payload.get("maxRows", 25)
                radius = payload.get("radius", "25")
                
                if not query or not location:
                    raise ValueError("Please provide at least 'query' and 'location' in your JSON.")
                
                results = scrape_linkedin_jobs(query, location, max_rows, radius, payload)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(results, indent=2).encode('utf-8'))
                
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e), "trace": traceback.format_exc()}).encode('utf-8'))

if __name__ == '__main__':
    port = 8080
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, UnifiedHandler)
    print(f"Unified API Server listening on port {port}...")
    print(f"Routes available: POST /api/cv, POST /api/scrape")
    httpd.serve_forever()
