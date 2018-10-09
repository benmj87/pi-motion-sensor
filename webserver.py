import os
import os.path
from pathlib import Path
from http.server import BaseHTTPRequestHandler,HTTPServer

class myHandler(BaseHTTPRequestHandler):
  def do_GET(self):

    f = Path('email-flag')
    if f.is_file():
      exists = True
    else:
      exists = False

    if exists:
      radios = """<input type="radio" name="option" value="1" checked="checked" /> <label for="1">Enable</label><br>
                  <input type="radio" name="option" value="0" /><label for="0">Disable</label><br /><br />"""
    else:
      radios = """<input type="radio" name="option" value="1" /> <label for="1">Enable</label><br>
                  <input type="radio" name="option" value="0" checked="checked" /><label for="0">Disable</label><br /><br />"""

    html = """<!DOCTYPE html>
    <html>
      <body>

      <h2>Enable/Disable email notifications</h2>

      <form method="POST">""" 

    html += radios  

    html +=  """<input type="submit" value="Save" />  
      </form> 

      </body>
    </html>"""

    self.send_response(200)
    self.send_header('Content-Type', 'text/html')
    self.end_headers()
    self.wfile.write(html.encode('utf-8'))

    return

  def do_POST(self):
    len = self.headers.get('content-length', 0)
    body = self.rfile.read(int(len)).decode('utf-8')
    print(body)
   
    if body == 'option=0':
      if (os.path.exists('email-flag')):
        os.remove('email-flag')
    else:
      with open('email-flag', 'w') as f:
        f.write('nul')
   
    self.send_response(301)
    self.send_header('Location','/')
    self.end_headers()
    return

try:
  server = HTTPServer(('', 8080), myHandler)
  server.serve_forever()
except KeyboardInterrupt:
  server.socket.close()
