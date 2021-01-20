"""
File: extension.py
------------------
As an extension to searchengine.py, this program adds the extra feature
of removing stop words from the index and user query.

"""

import os
import string
import sys
import math

STOP_WORDS = 'stop_words.txt'
TOTAL_NUM_DOCUMENTS = 347


def create_index(filenames, index, file_titles):
    """
    This function is passed:
        filenames:      a list of file names (strings)

        index:          a dictionary mapping from terms to file names (i.e., inverted index)
                        (term -> list of file names that contain that term)

        file_titles:    a dictionary mapping from a file names to the title of the article
                        in a given file
                        (file name -> title of article in that file)

    The function will update the index passed in to include the terms in the files
    in the list filenames.  Also, the file_titles dictionary will be updated to
    include files in the list of filenames.

    >>> index = {}
    >>> file_titles = {}
    >>> create_index(['test1.txt'], index, file_titles)
    >>> index
    {'file': ['test1.txt'], '1': ['test1.txt'], 'title': ['test1.txt'], 'apple': ['test1.txt'], 'ball': ['test1.txt'], 'carrot': ['test1.txt']}
    >>> file_titles
    {'test1.txt': 'File 1 Title'}
    >>> index = {}
    >>> file_titles = {}
    >>> create_index(['test2.txt'], index, file_titles)
    >>> index
    {'file': ['test2.txt'], '2': ['test2.txt'], 'title': ['test2.txt'], 'ball': ['test2.txt'], 'carrot': ['test2.txt'], 'dog': ['test2.txt']}
    >>> file_titles
    {'test2.txt': 'File 2 Title'}
    >>> index = {}
    >>> file_titles = {}
    >>> create_index(['test1.txt', 'test2.txt'], index, file_titles)
    >>> index
    {'file': ['test1.txt', 'test2.txt'], '1': ['test1.txt'], 'title': ['test1.txt', 'test2.txt'], 'apple': ['test1.txt'], 'ball': ['test1.txt', 'test2.txt'], 'carrot': ['test1.txt', 'test2.txt'], '2': ['test2.txt'], 'dog': ['test2.txt']}
    >>> index = {}
    >>> file_titles = {}
    >>> create_index(['test1.txt', 'test2.txt', 'test2.txt'], index, file_titles)
    >>> index
    {'file': ['test1.txt', 'test2.txt'], '1': ['test1.txt'], 'title': ['test1.txt', 'test2.txt'], 'apple': ['test1.txt'], 'ball': ['test1.txt', 'test2.txt'], 'carrot': ['test1.txt', 'test2.txt'], '2': ['test2.txt'], 'dog': ['test2.txt']}
    >>> file_titles
    {'test1.txt': 'File 1 Title', 'test2.txt': 'File 2 Title'}
    >>> index = {'file': ['test1.txt'], '1': ['test1.txt'], 'title': ['test1.txt'], 'apple': ['test1.txt'], 'ball': ['test1.txt'], 'carrot': ['test1.txt']}
    >>> file_titles = {'test1.txt': 'File 1 Title'}
    >>> create_index([], index, file_titles)
    >>> index
    {'file': ['test1.txt'], '1': ['test1.txt'], 'title': ['test1.txt'], 'apple': ['test1.txt'], 'ball': ['test1.txt'], 'carrot': ['test1.txt']}
    >>> file_titles
    {'test1.txt': 'File 1 Title'}
    """
    for name in filenames:
        file = open(name)
        file_titles[name] = file.readline().strip()
        for line in open(name):
            line = line.strip()
            term_lst = line.split(' ')
            make_index(index, name, term_lst)
    stop_words = file_to_lst(STOP_WORDS)
    for word in stop_words:
        if word in index:
            del index[word]


def make_index(index, name, term_lst):
    for term in term_lst:
        term = term.strip()
        term = term.strip(string.punctuation)
        term = term.lower()
        if term != '':
            if term not in index:
                index[term] = []
            if name not in index[term]:
                index[term].append(name)


# this function turns a text file, each of whose line only contains one word, to a word list.
def file_to_lst(file):
    lst = []
    for line in open(file):
        line = line.strip()
        line = line.split(' ')
        lst.append(line[0])
    return lst


def search(index, query):
    """
    This function is passed:
        index:      a dictionary mapping from terms to file names (inverted index)
                    (term -> list of file names that contain that term)

        query  :    a query (string), where any letters will be lowercase

    The function returns a list of the names of all the files that contain *all* of the
    terms in the query (using the index passed in).

    >>> index = {}
    >>> create_index(['test1.txt', 'test2.txt'], index, {})
    >>> search(index, 'apple')
    ['test1.txt']
    >>> search(index, 'ball')
    ['test1.txt', 'test2.txt']
    >>> search(index, 'file')
    ['test1.txt', 'test2.txt']
    >>> search(index, '2')
    ['test2.txt']
    >>> search(index, 'carrot')
    ['test1.txt', 'test2.txt']
    >>> search(index, 'dog')
    ['test2.txt']
    >>> search(index, 'nope')
    []
    >>> search(index, 'apple carrot')
    ['test1.txt']
    >>> search(index, 'apple ball file')
    ['test1.txt']
    >>> search(index, 'apple ball nope')
    []
    """
    word_lst = query.split()
    pre_lst = []
    stop_words = file_to_lst(STOP_WORDS)
    for word in word_lst:
        if word in index:
            cur_lst = index[word]
            if pre_lst:
                cur_lst = common(cur_lst, pre_lst)
            pre_lst = cur_lst
        # ignore the stop words
        elif word in stop_words:
            cur_lst = pre_lst
        else:
            cur_lst = []
    print(cur_lst)
    return cur_lst


def rank(index, query):
    query_lst = query.split()
    filename = search(index, query)
    cosine_lst = []
    for file in filename:
        TF = 1
        vector = []
        for word in query_lst:
            num_doc = len(index[word])
            IDF = math.log(TOTAL_NUM_DOCUMENTS / num_doc) + 1
            for line in open(file):
                line = line.strip()
                term_lst = line.split(' ')
                for term in term_lst:
                    term = term.strip(string.punctuation)
                    term = term.lower()
                    if word == term:
                        TF += 1
            TFIDF = IDF * TF
            vector.append(TFIDF)
        normalized_doc = normalize(vector)
        normalized_query = normalize_query(query)
        cosine = 0
        for i in range(len(query_lst)):
            cosine += normalized_doc[i] * normalized_query[i]
        cosine_lst.append(cosine)
    similarity = []
    for i in range(len(cosine_lst)):
        similarity.append((filename[i], cosine_lst[i]))
    similarity = sorted(similarity, key=lambda x: x[1], reverse=True)
    return similarity


def normalize_query(query):
    query_lst = query.split()
    vector = []
    for i in range(len(query_lst)):
        TF = 1
        j = i + 1
        while j < len(query_lst):
            if query_lst[i] == query_lst[j]:
                TF += 1
            j += 1
        n = i - 1
        while n > - 1:
            if query_lst[i] == query_lst [n]:
                TF += 1
            n -= 1
        vector.append(TF)
    return normalize(vector)


def normalize(vector):
    sum = 0
    for elem in vector:
        sum += float(elem) ** 2
    magnitude = math.sqrt(sum)
    for i in range(len(vector)):
        vector[i] = vector[i] / magnitude
    return vector



def common(list1, list2):
    result = []
    if len(list1) >= len(list2):
        check_common(list1, list2, result)
    else:
        check_common(list2, list1, result)
    return result


def check_common(list1, list2, result):
    for i in range(len(list1)):
        if list1[i] in list2 and list1[i] not in result:
            result.append(list1[i])


##### YOU SHOULD NOT NEED TO MODIFY ANY CODE BELOW THIS LINE (UNLESS YOU'RE ADDING EXTENSIONS) #####


def do_searches(index, file_titles):
    """
    This function is given an inverted index and a dictionary mapping from
    file names to the titles of articles in those files.  It allows the user
    to run searches against the data in that index.
    """
    while True:
        query = input("Query (empty query to stop): ")
        query = query.lower()  # convert query to lowercase
        if query == '':
            break
        #results = search(index, query)
        results = rank(index, query)

        # display query results
        print("Results for query '" + query + "':")
        if results:  # check for non-empty results list
            for i in range(len(results)):
                title = file_titles[results[i]]
                print(str(i + 1) + ".  Title: " + title + ",  File: " + results[i])
        else:
            print("No results match that query.")


def textfiles_in_dir(directory):
    """
    DO NOT MODIFY
    Given the name of a valid directory, returns a list of the .txt
    file names within it.

    Input:
        directory (string): name of directory
    Returns:
        list of (string) names of .txt files in directory
    """
    filenames = []

    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filenames.append(os.path.join(directory, filename))

    return filenames


def main():
    """
    Usage: searchengine.py <file directory> -s
    The first argument specified should be the directory of text files that
    will be indexed/searched.  If the parameter -s is provided, then the
    user can interactively search (using the index).  Otherwise (if -s is
    not included), the index and the dictionary mapping file names to article
    titles are just printed on the console.
    """
    # Get command line arguments
    args = sys.argv[1:]
    num_args = len(args)
    if num_args < 1 or num_args > 2:
        print('Please specify directory of files to index as first argument.')
        print('Add -s to also search (otherwise, index and file titles will just be printed).')
    else:
        # args[0] should be the folder containing all the files to index/search.
        directory = args[0]
        if os.path.exists(directory):
            # Build index from files in the given directory
            files = textfiles_in_dir(directory)
            index = {}  # index is empty to start
            file_titles = {}  # mapping of file names to article titles is empty to start
            create_index(files, index, file_titles)

            # Either allow the user to search using the index, or just print the index
            if num_args == 2 and args[1] == '-s':
                do_searches(index, file_titles)
            else:
                print('Index:')
                print(index)
                print('File names -> document titles:')
                print(file_titles)
        else:
            print('Directory "' + directory + '" does not exist.')


if __name__ == '__main__':
    main()
