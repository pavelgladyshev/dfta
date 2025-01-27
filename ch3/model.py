import itertools
import networkx as nx 
from networkx.algorithms.euler import is_eulerian, eulerian_circuit

# Defining model of the system

def valid(v):
    noemp = [ x for x in list(v) if x != "empty"]
    return len(set(noemp)) == len(noemp)

def get(l,v):
    if(l in L):
        i = { "stephens" : 0, "synge" : 1, "westland" : 2, "kildare" : 3}.get(l)
        return v[i]
    else:
        return None

def dlen(l):
    return { "gladyshev" : 4, "johnson" : 2, "hyde" : -1, "empty" : 0, "lowry" : 0 }.get(l)

def lpark(s):
    if (s in S):
        return 1052+dlen(get("stephens",s))+dlen(get("synge",s))+dlen(get("westland",s))+dlen(get("kildare",s))
    else:
        return None

O = { "gladyshev", "johnson", "hyde", "lowry", "empty" }
L = [ "stephens", "synge", "westland", "kildare" ]
V = itertools.product(O,O,O,O)
S = [v for v in list(V) if valid(v)]

# Analysis of the model

# x is the length of output
# y is the name being present
# calculate numbers of states that produce parkinfo output of x bytes with y (l1)
# and without y (l2)
def hyp(x,y):
    l1=0
    l2=0
    for s in S:
        if (lpark(s) == x):
            if (y in s):
                l1 = l1+1
            else:
                l2 = l2+1
    return (l1,l2)

# output all states that produce parkinfo output of x bytes
def prst(x):
    for s in S:
        if (lpark(s)==x):
            print(s)


# calculate numbers of states that contain user y and produce parkinfo output of x bytes (l1) 
# or produce output of different size (l2)
def y_present(x,y):
    l1=0
    l2=0
    for s in S:
        if (y in s):
            if (lpark(s) == x):
                l1 = l1+1
            else:
                l2 = l2+1
    return (l1,l2)

# calculate numbers of states that DO NOT contain user y and produce parkinfo output of x bytes (l1) 
# or produce output of different size (l2)
def y_absent(x,y):
    l1=0
    l2=0
    for s in S:
        if not(y in s):
            if (lpark(s) == x):
                l1 = l1+1
            else:
                l2 = l2+1
    return (l1,l2)

# generate transition graph suitable for the chinese postman algorithm
def get_edges():
    E = []
    for i in range(0,len(S)):
        s = S[i]
        for j in range(0,len(s)):
            if s[j] != "empty":
                # can release an occupied space
                s1 = s[0:j]+("empty",)+s[j+1:]
                pos = S.index(s1)
#                print(i,j,s,s1)
#                print("(",i,",",pos,",",1,",",True,"),")
                E.append((i,pos,1))      
            else:
                # empty parking slot, consider all ways of filling it
                for o in O:
                    if not(o in s):
                        # o can occupy j-th space
                        s1 = s[0:j]+(o,)+s[j+1:]
                        pos = S.index(s1)
#                        print(i,j,s,s1)
#                        print("(",i,",",pos,",",1,",",True,"),")
                        E.append((i,pos,1))
    return E

E = get_edges()

# use networkx to create directed graph
def make_graph():
    DG = nx.DiGraph()
    DG.add_nodes_from(list(range(0,len(S))))
    DG.add_weighted_edges_from(E) 
    return DG

# stub for Chinese Postman Trip algorithm
def cpt(G):
    if is_eulerian(G):
        return list(eulerian_circuit(G))

#  Chinese Postman Trip calculated for graph G (list of visited states)
CPT = cpt(make_graph())

# HTTP methods
import requests as rq 
username = "gladyshev" # Need a default username &
password = "g123"      # password for requests to parkinfo 

def verify_success(status_code):
    if(status_code == 200):
        return f"HTTP request success : {status_code}"
    else:   
        return f"HTTP request failure : {status_code}"

def parkinfo():
    url = "http://127.0.0.1/parkinfo.php"
    response = rq.get(url, auth=(username,password)) 
    if(response.status_code == 200):
        return response.text
    else:
        return f"HTTP request failure : {response.status_code}"

def parkinfo_len():
    url = "http://127.0.0.1/parkinfo.php"
    response = rq.get(url, auth=(username, password))
    if(response.status_code == 200):
        return len(response.text)
    else:
        return f"HTTP request failure : {response.status_code}"

def reserve(loc, username, password):
    url = "http://127.0.0.1/reserve.php"
    form_data = { 
                 "loc": loc 
    }
    response = rq.post(url, data=form_data, auth=(username, password))
    return verify_success(response.status_code)

def release(loc, username, password):      
    url = "http://127.0.0.1/release.php"
    form_data = {
        "loc": loc
    }
    response = rq.post(url, data=form_data, auth=(username, password))
    return verify_success(response.status_code)

# get current state of parkinfo from Redis
import redis
r = redis.Redis(
        host = 'localhost',
        port = 6379,
        decode_responses = True
)

def parkinfo_state():
    state = tuple()
    for loc in L:
        state += (r.get(loc),)
    return state

# walk through CPT

def get_password(username):
    return f"{username[0]}123"

def step(cpt_edge):
    initial, final = S[cpt_edge[0]], S[cpt_edge[1]]
    for i in range(0, len(initial)):
        if(initial[i] != final[i]):
            loc = L[i]
            if(final[i] != "empty"):
                reserve(loc, final[i], get_password(final[i]))
            else:
                release(loc, initial[i], get_password(initial[i]))

def teleport(state_index):
    empty = S.index(("empty","empty","empty","empty"))
    current = S.index(parkinfo_state())
    step((current, empty)) 
    step((empty, state_index))

def walk():
    traversal = list()
    unexpected_lengths = list()
    #move to initial state
    teleport(CPT[0][0])
    for cpt_edge in CPT: 
        # check length of parkinfo for state 
        expected_length = lpark(S[cpt_edge[0]])
        actual_length = parkinfo_len()
        if(expected_length != actual_length):
            unexpected_lengths.append((cpt_edge[0],expected_length, actual_length)) 
        # record actual state traversal with Redis 
        initial = S.index(parkinfo_state())
        step(cpt_edge)
        final = S.index(parkinfo_state())
        traversal.append((initial,final))
    if(CPT == traversal):
        ret = f"Walk successfully completed with {len(CPT)} edges traversed and {len(unexpected_lengths)} occurences of unexpected size of parkinfo.php output."
        for item in unexpected_lengths:
            ret += f"\nAt state {item[0]}, expected {item[1]} bytes, actual {item[2]} bytes."
    else:
        ret = f"Walk failed."
    return ret
