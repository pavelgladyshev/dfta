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
def make_graph():
    G = []
    for i in range(0,len(S)):
        s = S[i]
        for j in range(0,len(s)):
            if s[j] != "empty":
                # can release an occupied space
                s1 = s[0:j]+("empty",)+s[j+1:]
                pos = S.index(s1)
#                print(i,j,s,s1)
#                print("(",i,",",pos,",",1,",",True,"),")
                G.append((i,pos,1,True))      
            else:
                # empty parking slot, consider all ways of filling it
                for o in O:
                    if not(o in s):
                        # o can occupy j-th space
                        s1 = s[0:j]+(o,)+s[j+1:]
                        pos = S.index(s1)
#                        print(i,j,s,s1)
#                        print("(",i,",",pos,",",1,",",True,"),")
                        G.append((i,pos,1,True))
    return G

                
#  Chinese Postman Trip calculated for graph G (list of visited states)

CPT =   [1, 61, 169, 174, 173, 148, 150, 12, 79, 77, 73, 86, 34, 37, 163, 161, 162, 35, 42, 14, 13, 14, 1, 61, 135, 140, 71, 70, 139, 134, 107, 109, 136, 63, 3, 11, 69, 63, 66, 64, 65, 6, 146, 172, 171, 168, 170, 62, 170, 143, 141, 144, 156, 158, 157, 25, 27, 158, 150, 144, 150, 158, 157, 148, 149, 10, 55, 48, 1, 14, 186, 201, 42, 35, 162, 161, 164, 145, 171, 168, 141, 161, 164, 165, 40, 37, 88, 86, 87, 75, 73, 83, 91, 92, 46, 36, 197, 178, 181, 179, 181, 199, 39, 36, 197, 195, 175, 0, 9, 10, 55, 48, 128, 133, 118, 117, 125, 31, 17, 44, 17, 117, 119, 126, 33, 23, 26, 23, 33, 126, 121, 109, 119, 20, 46, 44, 34, 44, 166, 151, 159, 160, 32, 31, 125, 126, 125, 120, 122, 120, 21, 188, 193, 185, 200, 185, 175, 177, 189, 194, 187, 177, 175, 188, 189, 22, 21, 28, 193, 188, 190, 188, 191, 192, 184, 182, 207, 208, 183, 182, 191, 25, 26, 25, 27, 24, 122, 110, 107, 108, 1, 18, 152, 142, 141, 145, 164, 165, 40, 38, 34, 36, 34, 195, 196, 35, 45, 167, 152, 167, 162, 167, 45, 44, 46, 20, 17, 19, 59, 57, 59, 99, 98, 93, 95, 50, 129, 110, 113, 8, 147, 144, 163, 144, 147, 145, 5, 0, 1, 176, 175, 182, 175, 202, 203, 208, 183, 10, 68, 67, 103, 104, 69, 11, 184, 192, 26, 11, 78, 11, 9, 25, 9, 67, 103, 100, 101, 106, 105, 100, 60, 61, 60, 134, 139, 70, 13, 114, 116, 16, 30, 28, 30, 124, 116, 124, 123, 120, 121, 120, 107, 114, 115, 14, 42, 201, 200, 195, 34, 161, 163, 165, 147, 165, 163, 37, 43, 16, 30, 124, 123, 114, 115, 140, 71, 61, 68, 10, 9, 11, 3, 178, 190, 23, 121, 126, 119, 117, 17, 83, 98, 93, 73, 86, 89, 90, 82, 16, 4, 0, 141, 148, 149, 142, 169, 61, 68, 174, 149, 174, 173, 168, 173, 148, 9, 182, 9, 67, 69, 104, 102, 63, 136, 134, 137, 111, 112, 138, 66, 63, 60, 67, 173, 67, 69, 63, 60, 62, 72, 15, 72, 70, 105, 100, 73, 0, 3, 36, 3, 23, 3, 0, 1, 48, 203, 176, 196, 201, 186, 185, 187, 15, 2, 49, 2, 62, 65, 172, 65, 62, 101, 106, 81, 106, 72, 106, 105, 80, 82, 76, 79, 97, 95, 76, 73, 93, 47, 51, 130, 111, 130, 131, 130, 127, 47, 51, 205, 179, 198, 179, 5, 7, 3, 109, 3, 63, 102, 104, 103, 77, 78, 75, 3, 75, 102, 100, 101, 62, 2, 22, 32, 160, 155, 160, 159, 31, 159, 154, 141, 143, 153, 151, 141, 161, 166, 151, 152, 142, 162, 142, 149, 10, 183, 176, 196, 35, 45, 44, 91, 83, 85, 20, 33, 31, 21, 120, 125, 117, 132, 127, 107, 0, 34, 161, 166, 167, 166, 44, 91, 86, 88, 76, 88, 90, 88, 37, 40, 8, 113, 110, 4, 8, 4, 144, 141, 142, 1, 176, 175, 188, 191, 182, 207, 54, 96, 93, 95, 97, 96, 97, 79, 76, 95, 50, 53, 50, 56, 97, 56, 12, 56, 54, 96, 77, 9, 54, 9, 77, 73, 75, 102, 100, 60, 64, 5, 38, 39, 7, 112, 109, 136, 138, 136, 134, 135, 140, 115, 108, 128, 48, 58, 18, 152, 151, 17, 19, 2, 6, 52, 6, 180, 6, 5, 111, 107, 109, 119, 20, 17, 0, 60, 168, 141, 154, 156, 24, 30, 24, 4, 76, 82, 16, 43, 90, 82, 80, 13, 28, 123, 120, 107, 117, 118, 133, 58, 133, 132, 117, 107, 114, 116, 110, 116, 16, 4, 37, 4, 12, 9, 0, 2, 6, 65, 64, 60, 134, 135, 61, 71, 14, 71, 70, 60, 70, 105, 80, 13, 185, 186, 176, 203, 202, 175, 178, 184, 182, 183, 176, 186, 14, 115, 108, 107, 0, 60, 62, 72, 70, 13, 16, 13, 114, 139, 140, 139, 114, 123, 28, 193, 185, 175, 179, 205, 202, 207, 202, 205, 51, 5, 179, 180, 206, 52, 49, 47, 202, 204, 177, 180, 179, 175, 178, 190, 192, 26, 11, 184, 178, 3, 7, 39, 36, 87, 75, 85, 75, 78, 104, 78, 77, 103, 100, 73, 80, 73, 83, 85, 20, 3, 20, 33, 31, 21, 154, 157, 148, 141, 0, 4, 50, 56, 54, 55, 208, 203, 48, 58, 18, 1, 10, 1, 108, 135, 108, 118, 18, 45, 18, 17, 83, 98, 99, 84, 99, 59, 49, 204, 206, 52, 51, 5, 7, 181, 178, 197, 199, 197, 195, 200, 41, 200, 201, 196, 195, 198, 195, 175, 0, 47, 0, 5, 8, 147, 145, 141, 151, 159, 154, 157, 25, 21, 154, 155, 22, 29, 15, 13, 41, 89, 80, 89, 90, 43, 41, 42, 41, 13, 185, 187, 15, 81, 80, 81, 74, 73, 0, 13, 15, 81, 74, 2, 74, 94, 93, 94, 74, 84, 19, 84, 83, 84, 74, 101, 74, 73, 76, 4, 110, 107, 111, 113, 131, 129, 127, 128, 133, 132, 57, 47, 57, 17, 151, 153, 143, 146, 143, 2, 19, 32, 31, 17, 18, 118, 108, 128, 127, 130, 51, 53, 51, 52, 49, 94, 99, 94, 49, 47, 48, 47, 50, 4, 144, 156, 158, 27, 12, 4, 24, 156, 154, 155, 22, 21, 0, 34, 86, 87, 92, 85, 92, 46, 36, 87, 92, 91, 86, 89, 41, 43, 37, 34, 35, 1, 35, 34, 41, 34, 38, 164, 38, 40, 8, 53, 8, 5, 38, 39, 199, 198, 38, 198, 199, 181, 7, 66, 64, 171, 145, 5, 6, 146, 145, 146, 172, 170, 172, 171, 64, 137, 138, 66, 7, 112, 111, 137, 64, 5, 111, 113, 131, 53, 131, 129, 50, 47, 54, 207, 208, 55, 54, 47, 202, 204, 206, 205, 206, 180, 177, 2, 15, 29, 22, 32, 19, 153, 160, 153, 19, 59, 49, 204, 177, 2, 22, 189, 194, 193, 194, 187, 177, 189, 188, 21, 23, 190, 192, 191, 25, 21, 24, 27, 12, 9, 148, 150, 12, 79, 77, 96, 93, 47, 127, 107, 134, 137, 138, 112, 109, 121, 23, 21, 28, 29, 194, 29, 28, 13, 0, 17, 57, 98, 57, 58, 57, 132, 127, 129, 110, 122, 124, 122, 24, 21, 0, 2, 143, 155, 143, 170, 168, 60, 67, 68, 174, 169, 168, 169, 142, 1]