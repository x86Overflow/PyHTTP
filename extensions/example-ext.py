if MGR_ExtState == "ExtDoc":
    document = "Extension Testing".encode()
if MGR_ExtState == "ExtHead":
    headers = headers + "Hello: World\r\n"