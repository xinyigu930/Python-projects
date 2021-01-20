# this imports the SimpleServer library
import SimpleServer
# This imports the functions you defined in searchengine.py
from searchengine import create_index, search, textfiles_in_dir
# has the json.dumps function. So useful
import json

"""
File: extension_server.py
---------------------
This program starts a server and searches words in the designated directory. 
It's implemented on http://localhost:8000 !
"""

# the directory of files to search over
DIRECTORY = 'bbcnews'
# perhaps you want to limit to only 10 responses per search..
MAX_RESPONSES_PER_REQUEST = 10


class SearchServer:
    def __init__(self):
        """
        load the data that we need to run the search engine. This happens
        once when the server is first created.
        """
        self.html = open('extension_client.html').read()
        self.files = textfiles_in_dir(DIRECTORY)
        self.index = {}
        self.file_titles = {}
        create_index(self.files, self.index, self.file_titles)

    # this is the server request callback function. You can't change its name or params!!!
    def handle_request(self, request):
        """
        This function gets called every time someone makes a request to our
        server. To handle a search, look for the query parameter with key "query"
        """
        # it is helpful to print out each request you receive!
        print(request)

        # if the command is empty, return the html for the search page
        if request.command == '':
            return self.html
        # if the command is search, the client wants you to perform a search!
        if request.command == 'search':
            query = request.get_params()['query']
            filename_lst = search(self.index, query)
            result = []
            if len(filename_lst) > 10:
                responses = MAX_RESPONSES_PER_REQUEST
            else:
                responses = len(filename_lst)
            for i in range(responses):
                title = self.file_titles[filename_lst[i]]
                dic = {'title': title}
                result.append(dic)
            # this return the string version of a list of dicts.
            print(json.dumps(result, indent=2))
            return json.dumps(result, indent=2)


def main():
    # make an instance of your Server
    handler = SearchServer()
    # start the server to handle internet requests!
    SimpleServer.run_server(handler, 8000) # make the server


if __name__ == '__main__':
    main()