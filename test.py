x=1
y=-2
strings="hello"
multi="line1\nline2\nline3"
if x>0:
    print("X is positive")
elif x<0:
    print("X is negative")
else :
    print("X is zero")
while x<11:
    print(x)
    x=x+1
for i in range(1, 2 + 1):
    print(i)
def add(x,y=2):
    return x+y
z=add(1)
lst=[0,1,2,3]
first=lst[0]
slc=lst[0:2+1]
print(first,slc)
dct={0:1,1:2,2:3}
