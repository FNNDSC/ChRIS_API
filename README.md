# ChRIS_API

## The API specification of ChRIS

This repository contains simulates a ChRIS instance that is REST conformant. It serves primarily as a test bed for the interacting with and developing the ChRIS REST API. The main entry point to the simulated machine is the python script, <tt>ChRIS_SM</tt> (where the <tt>SM</tt> denotes "Simulated Machine").

A simple web-facing server is also available: <tt>ChRIS_WS.py</tt> (where the <tt>WS</tt> denotes "Web Server"). This module is suitable for http handling using any client. When http traffic is sent to <tt>ChRIS_WS.py</tt>,  spawns a new <tt>ChRIS_SM.py</tt> instance. A new instance is spawned each time a new API call is made. The state of a user's data is preserved between calls by a simple file-based database.

## Getting up and running quickly

### Setup a server to run the simulated machine.

To setup a server you will need either a Linux or Mac machine. The backend will not run on Windows. See here for more [information](../../wiki/0.-Getting-Set-Up).

### Starting the server

Once setup, start up the <tt>ChRIS_WS.py</tt> server from the command line. In the simplest case, it is sufficient to run

```
./ChRIS_WS.py -i 192.168.1.3 -p 5555 --API REST
```

Assuming of course that your machine has IP <tt>192.168.1.3</tt>  - see here for more [information](../../1.-Starting-the-Server).

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

Note that this call sends a <tt>hash</tt> and not the user's password. For more information, see [here](../../wiki/.3.-Login-out-and-Session-Authentication).

## Interacting with the API service

### Call anatomy

The client sends an http request to the server. The server services the call and returns a JSON formatted stream of data with the following fields:

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

More information in the wiki [here](../../wiki/4.-Call-anatomy).

