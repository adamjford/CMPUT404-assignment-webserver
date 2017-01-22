#  coding: utf-8 
import SocketServer, os.path, time, datetime


# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(SocketServer.BaseRequestHandler):
    def get(self, path):
        if path[-1] == '/':
            path += 'index.html'

        file_path = './www' + path

        if self.content_dir not in os.path.abspath(file_path):
            # 404
            pass
        else:
            response = ''

            # Written by rslite (http://stackoverflow.com/users/15682/rslite) on StackOverflow
            # http://stackoverflow.com/a/82852 (CC-BY-SA 3.0)
            if os.path.isfile(file_path):
                # There's a file at that path, so let's serve it

                # Source: https://docs.python.org/2/tutorial/inputoutput.html
                with open(file_path) as f:
                    contents = f.read()

                headers = [
                    # Source: Example GET from class slides
                    # https://eclass.srv.ualberta.ca/pluginfile.php/3259365/mod_resource/content/2/04-HTTP.pdf
                    'HTTP/1.1 200 OK',
                    'Server: MyWebServer/0.1 Python/2.7',
                    'Content-type: text/html',
                    # From https://docs.python.org/2/library/os.path.html#os.path.getsize
                    'Content-Length: %d' % os.path.getsize(file_path),
                    'Date: %s' % format_date_now(),
                    # From https://docs.python.org/2/library/os.path.html#os.path.getmtime
                    'Last-Modified: %s' % format_date(time.gmtime(os.path.getmtime(file_path)))
                ]

                response = '\r\n'.join(headers) + '\r\n\r\n'
                response += contents
            elif os.path.isdir(file_path):
                # Means we ended up here by /foo
                # so redirect to /foo/ via 301 Moved Permanently
                # Based on behaviour/output of SimpleHTTPServer in same case

                now = format_date_now()

                headers = [
                    'HTTP/1.1 301 Moved Permanently',
                    'Server: MyWebServer/0.1 Python/2.7',
                    'Date: %s' % now,
                    'Location: %s' % (path + '/')
                ]

                response = '\r\n'.join(headers)

                print response

            return response

    def handle(self):
        self.content_dir = os.path.abspath('./www/')
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: \n%s\n" % self.data)

        response = ''

        first_line = self.data.split('\r\n')[0]

        split_line = first_line.split(' ')

        method = split_line[0]

        if method == 'GET':
            response = self.get(split_line[1])
            self.request.sendall(response)
        else:
            self.request.sendall("501 Not Implemented\r\n")


def format_date(time_to_format):
    # from https://docs.python.org/2/library/time.html
    format_string = '%a, %d %b %Y %H:%M:%S GMT'

    if time_to_format is None:
        return time.strftime(format_string, time.gmtime())

    return time.strftime(format_string, time_to_format)


def format_date_now():
    # From https://docs.python.org/2/library/datetime.html#datetime.datetime.now
    return format_date(None)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
