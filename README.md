# ChRIS_API

## The API specification of ChRIS

This repository contains a set of python scripts that simulates a REST conformant ChRIS instance. It serves primarily as a test bed for the interacting with and developing the ChRIS REST API. The main entry point to the simulated machine is the python script, <tt>ChRIS\_SM.py</tt> (where the <tt>SM</tt> denotes "Simulated Machine").

A simple web-facing server is also available: <tt>ChRIS\_WS.py</tt> (where the <tt>WS</tt> denotes "Web Server"). This module is suitable for handling <tt>http</tt> traffic originating from any client. When <tt>http</tt> traffic is sent to <tt>ChRIS\_WS.py</tt>, it spawns a new <tt>ChRIS\_SM.py</tt> instance to service the traffic --- in other words a new simulated machine is created for **each** call to the web service. The state of a user's data is preserved between calls by a simple file-based database.

## Getting up and running quickly

### Setup a server to run the simulated machine.

To setup a server you will need either a Linux or Mac machine. The backend will not run on Windows. See [here](../../wiki/0.-Getting-Set-Up) for more information.

### Starting the API service

Once setup, start up the <tt>ChRIS\_WS.py</tt> server from the command line. In the simplest case, it is sufficient to run

```
./ChRIS_WS.py -i 192.168.1.3 -p 5555 --API REST
```

(Assuming of course that your machine has IP <tt>192.168.1.3</tt>)

See [here](../../wiki/1.-Starting-the-Server) for more information.

### Start a web server to access the service

The easiest way to interact with the API service is using the bundled <tt>index.html</tt>. To use this, you need to start a web server in the checkout directory. 

```
python -m SimpleHTTPServer 8001
```

This will start a server on port 8001. Now, point your browser at

```
http://localhost:8001
```

to access the tester. Consult the page's "help" button for more information.

### First things first: logging in (and logging out)

Before you can do anything, you need to "log in". Of course, this is all simulated, and the login state is recorded by writing a lock file to the filesystem. Login never times out, and only changes once you actually "log out".

Importantly, _no API calls will be serviced until you login_.

To log in, on a client, do

```
curl  -s  "http://192.168.1.3:5555/v1/login?auth=user=chris,passwd=chris1234"
```

The <tt>passwd</tt> is actually important. Any other string and the login will fail.

To log out, do

```
curl  -s  "http://192.168.1.3:5555/v1/logout?auth=user=chris,hash=ABCDEF1234"
```

Note that this call sends a <tt>hash</tt> and not the user's password. See [here](../../wiki/2.-Login,-logout,-and-Session-Authentication) for more information.

## Interacting with the API service

### Call anatomy

The client sends an http request to the server. A typical call, for example getting a list of available feeds for the logged in user, is:

```
curl  -s  "http://192.168.1.3:5555/v1/Feeds/NAME_*?auth=user=chris,hash=ABCDEF123456789"
```

The server services the call and returns a JSON formatted stream of data with the following fields:

````
o
 \
  +--- API
  |       |
  |       +--- APIcall: "text string: API call as seen by client"
  |
  +--- return
  |       |
  |       +--- status: True|False (boolean)
  |       |
  |       +--- payload: {dictionary of call specific results}
  |       |         
  |       +--- URL_PUT: [list of PUT URLs from this context]
  |       |
  |       +--- URL_GET: [list of GET URLs from this context]
  |
  +--- auth
  |       |
  |       +--- status: True|False (boolean)
  |       |
  |       +--- authInfo: {dictionary of authorization information}
  |       |
  |       +--- message: "text message"
  |
  +--- server
          |
          +--- URI: "text URI of server -- can be combined with URL_GET/URL_PUT and {auth} to create valid calls"
          |
          +--- APIversion: "text of called API version"
````

More information about [the call anatomy](../../wiki/3.-Call-anatomy) and [the feed logical structure](../../wiki/4.-Feed-Logical-Structure) available in the wiki.

