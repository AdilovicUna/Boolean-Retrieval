from collections import defaultdict
from curses.ascii import isalnum
import os

inverted_index = defaultdict(set)

def remove_delim(word):
    """

    removes delimeters from beginning and end of a word

    """
    while len(word) > 0 and not isalnum(word[0]) and not word[0].lower() in "áčďéěíňóřšťúůýž":
        word = word[1:]
    while len(word) > 0 and not isalnum(word[-1]) and not word[-1].lower() in "áčďéěíňóřšťúůýž":
        word = word[:- 1]
    return word

def tokenize_one_line(line):
    """

    eg. "Lorem ipsum dolor sit amet, consectetur adipiscing elit." -> 
        ["Lorem", "ipsum, "dolor", "sit", "amet", "consectetur", "adipiscing", "elit"]

    """
    return [remove_delim(word) for word in line.split()]

def open_tag(name):
    """

    eg. "TEXT" -> "<TEXT>"

    """
    return '<' + name + '>'

def closed_tag(name):
    """

    eg. "TEXT" -> "</TEXT>"

    """
    return '</' + name + '>'

def strip_tag(name,line):
    """

    eg. "<TEXT>Lorem ipsum</TEXT>" -> "Lorem ipsum"

    """
    return line[len(open_tag(name)): - len(closed_tag(name))]

def index_one_file(filepath):
    """

    goes through one file on filepath and updates the inverted index
    from the documents in that file

    """
    with open(filepath,'r',encoding='utf8') as file:
        all_lines = file.readlines()   

    doc_id = -1
    is_open_tag = False

    for line in all_lines:
        line = line.strip()

        if "DOCID" in line:
            doc_id = strip_tag("DOCID",line)

        elif line == open_tag("TITLE") or line == open_tag("TEXT") or line == open_tag("HEADING"):
            is_open_tag = True
        elif line == closed_tag("TITLE") or line == closed_tag("TEXT") or line == closed_tag("HEADING"):
            is_open_tag = False
        
        elif is_open_tag:
            result = tokenize_one_line(line)
            for word in result:
                inverted_index[word].add(doc_id)

    file.close()

def loop_files(directory):
    """

    loops through all files in directory and calls index_one_file() on each of them

    """
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        if os.path.isfile(f):
            index_one_file(f)

def split_query(query):
    """

    eg. "a AND b OR c AND NOT d" -> ["a", "AND", "b", "OR", "c", "AND NOT", "d"]

    """
    temp = query.split()
    result = []
    i = 0
    while i < len(temp) - 1:
        if temp[i] == "AND" and temp[i+1] == "NOT":
            result.append("AND NOT")
            i += 2
        else:
            result.append(temp[i])
            i += 1
    result.append(temp[-1])
    return result

def _or(a,b):
    """

    implementation of the boolean operator OR

    """
    result = set([])
    for elem in a:
        result.add(elem)
    for elem in b:
        result.add(elem)
    return result

def _and(a,b):
    """

    implementation of the boolean operator AND

    """
    result = set([])
    (a,b) = (b,a) if len(a) > len(b) else (a,b)

    for elem in a:
        if elem in b:
            result.add(elem)
    return result

def _and_not(a,b):
    """

    implementation of the boolean operator AND NOT

    """
    result = set([])
    for elem in a:
        if not elem in b:
            result.add(elem)
    return result

def eval_atomic_query(a, op, b):
    """

    evaluates atomic query

    """
    if type(a) is str:
        a = inverted_index[a]
    if type(b) is str:
        b = inverted_index[b]

    if op == "AND":
        return _and(a,b)
    if op == "OR":
        return _or(a,b)
    if op == "AND NOT":
        return _and_not(a,b)

def eval_query(query):
    """

    evaluate the query from left to right

    """
    if len(query) == 3:
        return eval_atomic_query(query[0], query[1], query[2])
    return eval_atomic_query(eval_query(query[:-2]), query[-2], query[-1])
     
def loop_query_file(filepath):
    """

    process all queries from file on filepath and creates output files for each - num - tag

    """
    with open(filepath,'r',encoding='utf8') as file:
        all_lines = file.readlines()   
    file.close()

    directory = "10.2452"
    if not os.path.exists(directory):
        os.mkdir(directory)

    filename = ""

    for line in all_lines:
        line = line.strip()
        if "num" in line:
            path = strip_tag("num", line)
            filename = path.split('/')[1]
        elif "query" in line:
            query = strip_tag("query", line)
            doc_ids = eval_query(split_query(query))
            s = ""
            for id in doc_ids:
                s += id + '\n'

            with open(os.path.join(directory, filename), "w") as file:
                file.write(s)
            file.close()

def main():
    # loop through all the files and build inverted index
    loop_files("A2\documents_cs")

    # process each query and create output
    loop_query_file("A2\queries_cs.xml")

if __name__ == "__main__":
    main()
