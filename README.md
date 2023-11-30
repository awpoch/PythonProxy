# Python Proxy

I created 3 python scripts, a client, a proxy, and a server. The client sends a request to the proxy, 
which parses the request (sperating/organizing the host, file path, and headers) and sends it to the server. 
The server then replies to the proxy with the requested file and the proxy forwards it back to the client. 
In this example the server is just a simple reflection server. However, any server can be used. The client
just has to enter the address of the server it's trying to reach om initialization.

### More Information:
* Uses Python's Socket library
* Creates a buffer to recieve all data
* Parses HTTP headers

### Here's a Preview:
![PythonProxy](https://github.com/awpoch/PythonProxy/assets/143761409/5d862ac3-e830-45cf-a6cb-ccd38e5c9dc3)
