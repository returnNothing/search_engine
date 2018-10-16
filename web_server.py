from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import search_engine
from indexer import Position_structure
import requests

# Web_Server is used to send search results on the server with the use of html-form. 
class Web_Server(BaseHTTPRequestHandler):

    # do_GET sends html-form with a query and limit (offset) fields. 
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(bytes("<html><body><form method=\"post\" action=\"web_server.py\">" \
                               "<p>Query: <input type=\"text\" name=\"query\"></p>" \
                               #"<p>Offset: <input type=\"number\" name=\"offset\"></p>" \
                               "<input type=\"hidden\" name=\"offset\">"
                               "<p>Limit: <input type=\"number\" name=\"limit\"></p>" \
                               "<p><input type=\"submit\" name=\"search\" value=\"Search\"></p></form></body></html>" \
                               , encoding='utf-8'))

    # do_POST enables server to get new information from put by a user and post responses.     
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html;charset=utf-8')
        self.end_headers()
        
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type']}, encoding='utf-8')

        if form.getvalue('search'):
            offset = 0
            limit = 1

        # Get a value of a query-field. 
        if form.getvalue('query'):
            query = str(form.getvalue('query'))

        # Otherwise say that nothing was printed. 
        else:
            raise ValueError('Query is empty.')
            

        # Get a value of a limit-field.
        # Limit is how many items will be given. 
        if form.getvalue('limit'):
            limit = int(form.getvalue('limit'))

        # Value by default. 
        else:
            limit = 1

        # Get a value of a offset-field.
        # Offset is the number of the first item from which all the rest will be given.     
        if form.getvalue('offset'):
            offset = int(form.getvalue('offset'))

        # Value by default.
        else:
            offset = 0

        # Value by default.
        window_size = 1

        # A list for names of limit-fields is created. 
        forms = []

        # A list for names of offset-fields is created. 
        forms2 = []

        # They are given different names. 
        for i in range(limit):
            forms.append('offset_for_citations_' + str(i))
            forms2.append('limit_for_citations_' + str(i))

        # Get offset for citations for each document. 
        offset_for_citations = []                  
        for f in forms:
            if form.getvalue(f):
                offset_for_citations.append(int(form.getvalue(f)))

            # Value by default.
            else:
                offset_for_citations.append(0)

        # Get limit for citations for each document. 
        limit_for_citations = []
        for f2 in forms2:
            if form.getvalue(f2):
                limit_for_citations.append(int(form.getvalue(f2)) + 1)

            # Value by default.
            else:
                limit_for_citations.append(11)

        # Do back for documents.
        if form.getvalue('back') and offset >= limit: 
            offset -= limit

        # Do next for documents.
        if form.getvalue('next'):
            offset += limit

        # Do start for documents.
        if form.getvalue('start'):
            offset = 0

        # A list for names of Next-buttons for citations is created.
        next_buttons = []

        # A list for names of Back-buttons for citations is created.
        back_buttons = []

        # A list for names of Start-buttons for citations is created.
        start_buttons = []

        # All the buttons are named. 
        for i in range(limit):
            next_buttons.append('next_' + str(i))
            back_buttons.append('back_' + str(i))
            start_buttons.append('start_' + str(i))

            # Do next for citations of a certain document.
            if form.getvalue(next_buttons[i]): 
                offset_for_citations[i] += limit_for_citations[i] - 1

            # Do back for citations of a certain document.
            elif form.getvalue(back_buttons[i]) and offset_for_citations[i] >= limit_for_citations[i] - 1: 
                offset_for_citations[i] -= limit_for_citations[i] - 1

            # Do start for citations of a certain document.
            elif form.getvalue(start_buttons[i]): 
                offset_for_citations[i] = 0

        # A list of pairs offset-limit for citations of each document is created. 
        limit_and_offset = list(zip(offset_for_citations, limit_for_citations))

        # Request more than was asked for to check if it's the last page. 
        limit_plus = limit + 1

        # Call the main function.
        request = self.server.engine.emphasize_3(query, window_size, limit_plus, offset, limit_and_offset)

        # Print the same form as in do_GET.
        self.wfile.write(bytes("<html><body><form method=\"post\" action=\"web_server.py\">" \
                               "<p>Query: <input type=\"text\" name=\"query\" value=\"%s\"></p>" \
                               #"<p>Offset: <input type=\"number\" name=\"offset\" value=\"%s\"></p>" \
                               "<input type=\"hidden\" name=\"offset\" value=\"%s\">" \
                               "<p>Limit: <input type=\"number\" name=\"limit\" value=\"%s\"></p>" \
                               "<p><input type=\"submit\" name=\"search\" value=\"Search\"></p><ol>" \
                               %(query, offset, limit), encoding='utf-8'))

        # Count how many documents were already printed. 
        i = 0

        # Each document is a given a counting number and set number (limit) citations from it is printed. 
        for key in sorted(request):

            # The last citation is not given to a user. 
            if i <= limit - 1:
                self.wfile.write(bytes("<li><p><b>File Name: %s </b></p>" % key, encoding='utf-8'))

                # By a document number (i) we know the name of the form and offset from their lists.
                #self.wfile.write(bytes("<p>Offset for citations: <input type=\"number\"" \
                                        #"name=\"%s\" value=\"%s\"></p>" % (forms[i], offset_for_citations[i]), encoding='utf-8'))
                self.wfile.write(bytes("<input type=\"hidden\" name=\"%s\" value=\"%s\">" % (forms[i], offset_for_citations[i]), encoding='utf-8'))

                # The same is done for limit.  
                self.wfile.write(bytes("<p>Limit for citations: <input type=\"number\"" \
                                        "name=\"%s\" value=\"%s\"></p><ul>" % (forms2[i], limit_for_citations[i] - 1), encoding='utf-8'))

                # Then citations are printed.
                for value in request[key][:-1]:
                    self.wfile.write(bytes("<li>%s</li>" % value, encoding='utf-8'))
        
                # If it's the first page, then only Next-button is created. 
                if offset_for_citations[i] == 0 and len(request[key]) > limit_for_citations[i] - 1:
                    self.wfile.write(bytes("</ul></li><p><input type=\"submit\" name =\"%s\" value =\"Next\"></p>" % next_buttons[i], encoding='utf-8'))

                # If it's not the first page and we can go further, then all buttons are created. 
                elif offset_for_citations[i] != 0 and len(request[key]) > limit_for_citations[i] - 1:
                    self.wfile.write(bytes("</ul></li><p><input type=\"submit\" name =\"%s\" value =\"Back\"> " \
                                           "<input type=\"submit\" name =\"%s\" value =\"Next\"> " \
                                       "<input type=\"submit\" name =\"%s\" value =\"At the start\"></p>" % (back_buttons[i], next_buttons[i], start_buttons[i]), encoding='utf-8'))

                # If it's the only page, don't print any buttons.
                elif offset_for_citations[i] == 0 and len(request[key]) < limit_for_citations[i] - 1:
                    pass

                # If it's the last page, print only 'back' and 'start'.
                else:
                    self.wfile.write(bytes("</ul></li><p><input type=\"submit\" name =\"%s\" value =\"Back\"> " \
                                           "<input type=\"submit\" name =\"%s\" value =\"At the start\"></p>" % (back_buttons[i], start_buttons[i]), encoding='utf-8'))

                # Counter for documents. 
                i = i + 1

            else:
                pass

        # The same thing with buttons for citations. 
        if offset == 0 and len(request.keys()) > limit:
            self.wfile.write(bytes("</ol><p><input type=\"submit\" name =\"next\" value =\"Next\"></p></form></body></html>", encoding='utf-8'))
            
        elif offset != 0 and len(request.keys()) > limit:
            self.wfile.write(bytes("</ol><p><input type=\"submit\" name =\"back\" value =\"Back\"> <input type=\"submit\" name =\"next\" value =\"Next\"> " \
                           "<input type=\"submit\" name =\"start\" value =\"At the start\"></p></form></body></html>", encoding='utf-8'))

        elif offset == 0 and len(request.keys()) <= limit:
            pass

        else:
            self.wfile.write(bytes("</ul></li><p><input type=\"submit\" name =\"back\" value =\"Back\"> " \
                                   "<input type=\"submit\" name =\"start\" value =\"At the start\"></p>", encoding='utf-8'))

# Run the server.  
def run(server_class=HTTPServer, handler_class=Web_Server):
        server_address = ('', 8000)
        httpd = server_class(server_address, handler_class)
        httpd.engine = search_engine.Search_Engine('war_and_peace')
        httpd.serve_forever()
        
run()
