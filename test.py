block_x=1
block_y=-2
block_strings="hello"
block_multi="line1\nline2\nline3"
if block_x>0:
    print("X is positive")
elif block_x<0:
    print("X is negative")
else:
    print("X is zero")
while block_x<11:
    print(block_x)
    block_x=block_x+1
for block_i in range(1, 2 + 1):
    print(block_i)
def block_add(block_x,block_y=2):
    return block_x+block_y
block_z=block_add(1)
block_lst=[0,1,2,3]
block_first=block_lst[0]
block_slc=block_lst[0:2+1]
print(block_first,block_slc)
set_dct={"[0:1]",{1:2}}
block_dct={0:1,1:2,2:3}