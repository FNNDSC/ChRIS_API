# ChRIS_API

## The API specification of ChRIS

This repository contains a set of mostly python code that creates a simulated ChRIS machine that serves as a test bed for the interacting with and developing the ChRIS REST API.

### Quick HOWOTO

The simplest way to interact with the service, is to fire up the ChRIS Web Service, <tt>ChRIS_WS.py</tt> and connect to the server port (default '5555', specify alternate port with <tt>--port \<port\></tt>). In order to connect to the service from a non-localhost browser, specify the host address of the service explicitly:

```
./ChRIS_WS.py --host 10.17.24.111 --port 5555 --API REST
```

This starts the service on <tt>10.17.24.111:5555</tt> and informs the listener to use the REST paradigm (the default). A Remote Procedure Call (RPC) paradigm is also available. You can now connect to this service from any <tt>http</tt> protocol scheme. Perhaps the quickest way to test an interaction with the web service is to use Google Chrome with the Advanced Rest Client extension. 

## Call anatomy

The client sends an http request to the server. The server services the call and returns a JSON formatted stream of data with the following fields:

````
o
 \
  +--- API
  |    |
  |    +--- APIcall: <APIcall>
  |
  +--- return
  |       |
  |       +--- status: True|False
  |       |
  |       +--- payload: {call specific results}
  |       |         
  |       +--- URL_PUT: [list]
  |       |
  |       +--- URL_GET: [list]
  |
  +--- auth
  |       |
  |       +--- status: True|False
  |       |
  |       +--- authInfo: {authorization information}
  |       |
  |       +--- message: "text message"
  |
  +--- server
          |
          +--- URI: "text URI of server"
          |
          +--- APIversion: "text"
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
