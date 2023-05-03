import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import molsql
import MolDisplay
import cgi
import ctypes


# Initialize the database and insert elements
db = molsql.Database(reset=True)
db.create_tables()
db['Elements'] = (1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25)
db['Elements'] = (6, 'C', 'Carbon', '808080', '010101', '000000', 40)
db['Elements'] = (7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40)
db['Elements'] = (8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40)

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            try:
                with open("index.html", "r") as file:
                    content = file.read()

                self.send_response(200)  # OK
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(content))
                self.end_headers()
                try:
                    self.wfile.write(bytes(content, "utf-8"))
                except BrokenPipeError:
                    print("Client closed the connection prematurely")


            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(bytes("404: index.html not found", "utf-8"))
        elif self.path == "/get_molecules":
            molecule_names = db.get_molecule_names()
            self.send_response(200)  # OK
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("\n".join(molecule_names).encode("utf-8"))

        elif self.path.startswith("/select_molecule"):
            query = urlparse(self.path).query
            query_components = parse_qs(query)
            molecule_name = query_components["name"][0]
            print(f"Selected molecule: {molecule_name}")
            MolDisplay.radius = db.radius();
            MolDisplay.element_name = db.element_name();
            MolDisplay.header += db.radial_gradients();
            for molecule in [ molecule_name]:
                mol = db.load_mol( molecule );
                mol.sort();
                with open( molecule + ".svg", "w" ) as fp:
                    fp.write( mol.svg() )

                with open(molecule + ".svg", "r") as fp:
                    content = fp.read()

                self.send_response(200)  # OK
                self.send_header("Content-type", "image/svg+xml")
                self.send_header("Content-length", len(content))
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))


        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))

    def do_POST(self):
        if self.path == "/upload":
            content_length = int(self.headers.get('Content-Length'))
            content_type, params = cgi.parse_header(self.headers.get('Content-Type'))

            if content_type == 'multipart/form-data':
                form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': content_type, 'CONTENT_LENGTH': content_length})

                sdf_file = form['file'].file.read().decode('utf-8')
                molecule_name = form.getvalue('name')
                
                # Save the SDF file to the database
                sdf_lines = sdf_file.splitlines()
                # sdf_lines = sdf_lines[4:]  # skipping first 4 lines
                # print(sdf_lines)
                db.add_molecule(molecule_name, sdf_lines)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Molecule uploaded and saved successfully')

            else:
                self.send_error(400)
                self.end_headers()
                self.wfile.write(bytes("400: Bad Request", "utf-8"))
    
        else:
            self.send_error(404)
            self.end_headers()
            self.wfile.write(bytes("404: Not found", "utf-8"))


# # Add the is_valid_sdf function here
# def is_valid_sdf(sdf_file):
#     # Validate the SDF file content
#     return True






if __name__ == "__main__":
    PORT = 56488
    httpd = HTTPServer(('localhost', PORT), MyHandler)
    print(f"Serving on port {PORT}")
    httpd.serve_forever()