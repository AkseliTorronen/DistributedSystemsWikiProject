import xmlrpc.client, sys, time
proxy = xmlrpc.client.ServerProxy('http://localhost:1234', allow_none=True)

while True:
    print("\nWhat would you like to do?")
    print("1) Find the shortest path between two Wikipedia articles.")
    print("0) exit")
    choice = input("Choose an option: ")
    
    try:
        choice = int(choice)

        if choice == 0:
            sys.exit()

        elif choice == 1:
            article1 = input("\nGive the first article's title: ")
            article2 = input("Give the second article's title: ")
            try:
                start = time.time()
                print(str(proxy.searchForPath(article1, article2)))
                end = time.time()
                print(f"Time taken: {end-start}")
            except xmlrpc.client.Fault as err:
                print("A fault occurred")
                print("Fault code: %d" % err.faultCode)
                print("Fault string: %s" % err.faultString)

        else:
            print("Unknown command.")
    
    except ValueError:
        print("\nPlease insert a number (0-2)")
