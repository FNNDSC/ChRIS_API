# ChRIS_API

## The API specification of ChRIS

This repository contains simulates a ChRIS instance that is REST conformant. It serves primarily as a test bed for the interacting with and developing the ChRIS REST API. The main entry point to the simulated machine is the python script, <tt>ChRIS_SM</tt> (where the <tt>SM</tt> denotes "Simulated Machine").

A simple web-facing server is also available: <tt>ChRIS_WS.py</tt> (where the <tt>WS</tt> denotes "Web Server"). This module is suitable for http handling using any client. When http traffic is sent to <tt>ChRIS_WS.py</tt>,  spawns a new <tt>ChRIS_SM.py</tt> instance. A new instance is spawned each time a new API call is made. The state of a user's data is preserved between calls by a simple file-based database.

## Getting up and running quickly

### Setup a server to run the simulated machine.

To setup a server you will need either a Linux or Mac machine. The backend will not run on Windows. See here for more [information](../../wiki/0.-Getting-Set-Up).

### Starting the server

Once setup, simply start up the <tt>ChRIS_WS.py<tt> server from the command line. In the simplest case, it is sufficient to run

```
./ChRIS_WS.py -i 192.168.1.3 -p 5555--API REST
```

Assuming of course that your machine has IP <tt>192.168.1.3</tt>  - see here for more [information](../../1.-Starting-the-Server).

### First things first: logging in (and logging out)

Before you can do anything, you need to "log in". Of course, this is all simulated, and the login state is recorded by writing a lock file to the filesystem. Login never times out, and only changes once you actually "log out".

But no API calls will be serviced until you login.

To log in, on a client, do

```
curl  -s  "http://192.168.1.3:5555/v1/login?auth=user=chris,passwd=chris1234"
```

The <tt>passwd</tt> is actually important. Any other string and the login will fail.

To log out, do

```
curl  -s  "http://192.168.1.3:5555/v1/logout?auth=user=chris,hash=ABCDEF1234"
```

Note that this call sends a <tt>hash</tt> and not the user's password. For more information, see here.

## Interacting with the API service

## Call anatomy

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

### <tt>API</tt>

The <tt>API</tt> field echoes back to the client the received API call.

## <tt>return</tt>

The <tt>return</tt> field contains information that the server has processed based on the client call. It contains the following sub-fields:

### <tt>status</tt>

The boolean return status of the call.

### <tt>payload</tt>

The call-specific information returned.

### <tt>URL_GET</tt>

A list of valid GET URLs from this context.

### <tt>URL_PUT</tt>

A list of valid PUT URLs from this context.

## <tt>auth</tt>

A module containing authorization information used to create per-call hashes between client and server.

## <tt>server</tt>

Information about the server, used in conjunction with <tt>URL_GET</tt> and <tt>URL_PUT</tt> to create REST API calls from this context.

## REST

The default manner of interaction is via a REST paradigm. 

### Login

To log into the system via REST, use the following call

```
http://10.17.24.111:5555/v1/login?auth=user=chris,passwd=chris1234
```

which returns

```json
{
    "API": {
        "APIcall": "/v1/login?auth=user=chris,passwd=chris1234"
    },
    "return": {
        "exec": {
            "status": true,
            "payload": {
                "message": "login credentials parsed",
                "loginDetail": {
                    "loginTimeStamp": "2015-09-10_16:07:33.319970",
                    "loginMessage": "Successful login for user chris at 2015-09-10 16:07:33.320026.",
                    "logoutMessage": "",
                    "sessionToken": "ABCDEF",
                    "APIcanCall": false,
                    "loginStatus": true,
                    "sessionSeed": "1",
                    "sessionStatus": true
                }
            }
        }
    },
    "auth": {
        "status": true,
        "authInfo": {
            "sessionSeed": "1",
            "user": "chris",
            "sessionStatus": true
        },
        "message": "Authorization info for user 'chris'."
    },
    "server": {
        "URI": "http://10.17.24.111:5555",
        "APIversion": "v1"
    }
}
```

## RPC

As an alternate to the <tt>REST</tt> interface, a Remote Procedure Call (RPC) type paradigm is also available. In this paradigm you effectively call the internal python API directly over the <tt>http</tt> scheme.

## Start the Web Service in RPC mode

The web service can be started in RPC mode as follows:

```
./ChRIS_WS.py --host 10.17.24.111 --port 5555 --API RPC 
```

As opposed to REST, the RPC approach is stateful, and each call is recorded (and played back again) in the a state file specified in *each* API call. This session file *must* be consistent across all API calls for this session. The RPC paradigm more complex, but arguably more expressive way to interact with the service since one can call the internal python API directly.

### Login

For completeness sake, the login using RPC:

````
http://10.17.24.111:5555?returnstore=d&object=chris&method=login&parameters=user='chris',passwd='chris1234'&clearSessionFile=1&sessionFile=session.py
````
which returns

```json
{
    "cmd": {
        "pycode": "d=chris.login(user='chris',passwd='chris1234')"
    },
    "API": {
        "APIcall": "/?returnstore=d&object=chris&method=login&parameters=user=%27chris%27,passwd=%27chris1234%27&clearSessionFile=1&sessionFile=session.py"
    },
    "return": {
        "exec": {
            "status": true,
            "payload": {
                "message": "login credentials parsed",
                "loginDetail": {
                    "loginTimeStamp": "2015-09-10_16:28:08.586338",
                    "loginMessage": "Successful login for user chris at 2015-09-10 16:28:08.586375.",
                    "logoutMessage": "",
                    "sessionToken": "ABCDEF",
                    "APIcanCall": false,
                    "loginStatus": true,
                    "sessionSeed": "1",
                    "sessionStatus": true
                }
            }
        }
    },
    "auth": {
        "status": true,
        "authInfo": {
            "sessionSeed": "1",
            "user": "chris",
            "sessionStatus": true
        },
        "message": "Authorization info for user 'chris'."
    }
}
```

This is identical to the REST call, with the added return field <tt>cmd/pycode</tt> for the actual internal python API call made.

#### Behind the scenes

The <tt>sessionFile</tt> acts as a persistent store between calls of the ChRIS Simulated Machine. The above API call is in fact parsed and assembled into a python class/method construct directly:

```
# 2015-06-01 16:13:04.502564 ?returnstore=d&object=chris&method=login&parameters=user=%27chris%27,passwd=%27chris1234%27&sessionFile=session.py
d=auth(lambda: chris.login(user='chris',passwd='chris1234'))
```

where we can clearly see how the URL args map to a function call in ChRIS.
