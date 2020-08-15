import itertools

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
L = { "stephens", "synge", "westland", "kildare" }
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


