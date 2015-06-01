# ChRIS_API

## The API specification of ChRIS

This repository contains a set of mostly python code that creates a simulated ChRIS machine that serves as a test bed for the interacting with and developing the ChRIS REST API.

### Quick-n-Dirty Test

The simplest way to interact with the service, is to fire up the ChRIS Web Service, <tt>ChRIS_WS.py</tt> and connect to the server port (default '5555', specify alternate port with <tt>--port \<port\></tt>:

```
./ChRIS_WS.py
```

Perhaps the quickest way to test an interaction with the web service is to use Google Chrome with the Advanced Rest Client extension. In the Query parameters you can add "key, value" pairs.

| key             | Value    |
|-----------------|----------|
| returnstore     | d        |
| object          | chris    |
| method          | login    |
| parameters      | user='chris',passwd='chris1234' |
| sessionFile     | session.py |

On hitting "Send", you should see:

```
{
 "sessionSeed": "1", 
 "APIcanCall": false, 
 "loginStatus": true, 
 "loginTimeStamp": "2015-06-01_16:13:04.503956", 
 "loginMessage": "Successful login at 2015-06-01 16:13:04.503992.", 
 "logoutMessage": "", 
 "sessionStatus": true, 
 "sessionToken": "ABCDEF"
}
```

#### Behind the scenes

The <tt>sessionFile</tt> acts as a persistent store between calls of the ChRIS Simulated Machine. The above API call is in fact parsed and assembled into a python class/method contruct directly:

```
# 2015-06-01 16:13:04.502564 ?returnstore=d&object=chris&method=login&parameters=user=%27chris%27,passwd=%27chris1234%27&sessionFile=session.py
d=auth(lambda: chris.login(user='chris',passwd='chris1234'))
```

where we can clearly see how the URL args map to a function call in ChRIS.
