# ChRIS_API

## The API specification of ChRIS

This repository contains python set of example code to create, interact with, and manipulate ChRIS feeds.

### <tt>api.php</tt>

The main entry point for interacting with the ChRIS web service. Calls to <tt>api.php</tt> return JSON objects.

For example

````
php api.php 'object=Feed&method=new'
````

returns

````
 {"note": {"meta": {"_depth": 1}}, "comment": {"meta": {"_depth": 1}, "contents": "Hello, world!"}, "meta": {"_depth": 0}, "data": {"meta": {"_depth": 1}, "visualView": {"meta": {"_depth": 2}}, "fileView": {"meta": {"_depth": 2}}}, "title": {"meta": {"_depth": 1}}}
````

