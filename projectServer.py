from textwrap import indent
from xmlrpc.server import SimpleXMLRPCServer
from collections import deque
import wikipediaapi
from multiprocessing import Manager
import json
import concurrent.futures


wikiSearch = wikipediaapi.Wikipedia('en')

def retrieveLinks(article):
    page = wikiSearch.page(article)
    links = page.links
    linksToPages = list(links.keys())
    finalList = []
    for l in linksToPages: #filter out unwanted links
        if l.startswith("Wikipedia:") or l.startswith("Template:") or l.startswith("Template talk:") or l.startswith("Help:") or l.startswith("Category:") or l.startswith("Portal:") or l.startswith("Talk:"):
            continue
        else:
            finalList.append(l)
            pass

    return finalList

def breadFirst(linkList, goal, path, page): #TODO typo, meant to be breadthFirst...
    for link in linkList:
        if link.lower() == goal.lower():
            return True
        if (link not in path) and (link != page):
            path[link] = path[page] + [link]
    return False

def pathFinder(article1, goal):
    
    path = Manager().dict()
    path[article1] = [article1]
    que = deque([article1]) #create a double ended queue for the links
    
    while len(que) != 0:
        visited = []
        page = str(que.popleft()) #take the leftmost article from the queue
        if page.startswith("["):
            page = page.lstrip("['").rstrip("']")
        print(f"Queue: {len(que)}") #helps keep track of the length of the queue

        if page:
            links = retrieveLinks(page) #get links from current page
            if len(links) == 0:
                continue
            else:
                #take the length of the current list of links and devide it evenly among the workers
                length = int(len(links)/10)
                executor = concurrent.futures.ProcessPoolExecutor(max_workers=10)
                for i in range(10):
                    j = i*length
                    if i == 9:
                        r = executor.submit(breadFirst, links[j:], goal, path, page)
                        if r.result():
                            return True
                        for l in links[j:]:
                            if l not in visited:
                                que.append(l)
                    else:
                        k = ((i+1)*length)
                        r = executor.submit(breadFirst, links[j:k], goal, path, page)
                        if r.result():
                            return True
                        for l in links[j:k]:
                            if l not in visited:
                                que.append(l)
            visited.append(page)
    return False

def assembleResponse(path, start, goal):
    if path == False:
        res = "No path."
    else:
        res = "Yes path."
    res = {"start":start, "goal":goal, "path":res}
    return json.dumps(res, indent=4, ensure_ascii=False).encode('utf-8') #encode the json manually to preserve letters like Å, Ä and Ö

def searchForPath(article1, article2):
    #search for pages and check if they exist
    page = wikiSearch.page(article1)
    page2 = wikiSearch.page(article2)
    
    if page.exists() and page2.exists():
        links = page.links
        linksToPages = list(links.keys())
    else:
        if page2.exists():
            return "1st article's name is invalid"
        elif page.exists():
            return "2nd article's name is invalid"
        return "Both article names are invalid"
    if article1.lower() == article2.lower():
        return "Input 2 different article names."

    for link in linksToPages:
        if link.lower() == article2.lower():
            return f"That was easy! Path: {article1} -> {article2}"

    path = pathFinder(article1, article2)
    finalResponse = assembleResponse(path, article1, article2).decode()
    print(finalResponse)
    return finalResponse

    
if __name__ == "__main__":
    print("Hello world!")
    server = SimpleXMLRPCServer(('localhost', 1234), logRequests=True, allow_none=True)
    server.register_function(searchForPath)
    print("[SERVER RUNNING]")
    server.serve_forever()