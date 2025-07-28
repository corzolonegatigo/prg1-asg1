# testing like the asap rocky album

h = 10
w = 10

player = {"x": 0, "y": 0}
fog = []
map_struct = []
map_file = open('level1.txt', 'r')
map_raw = map_file.readlines()
for i in range(len(map_raw)):
    map_struct.append(map_raw[i].strip("\n"))


for i in range(h):
        fog.append([])
        for j in range(w):
            fog[i].append(0)
def arr_of_str_to_2darr(list: list): 
    out = []
    for i in range(len(list)): 
        out.append([])
        for j in list[i]:
            out[i].append(j)

    return out
def clear_fog(map, fog, player):
    x = player['x']
    y = player['y']

    
    
    x_range = (x-1, x+2)
    y_range = (y-1, y+2)
    if x == 0:
        x_range = (x, x+2)
    elif x == (MAP_WIDTH-1):
        x_range = (x-1, x+1)

    if y == 0:
        y_range = (y, y+2)
    elif y == (MAP_HEIGHT-1):
        y_range = (y-1, y+1)

    #there must be a faster way
    width_surrounding = x_range[1] - x_range[1] + 1
    for yc in range(y_range[0], y_range[1]):
        for xc in range(x_range[0], x_range[1]):
            fog[yc][xc] = 1
        
    
    return fog
    
    return fog
def wrap_map(map: list): # takes a 1d/2d array as input. if 1d, each element is a str of fixed length. 2d, each list in the main list is of fixed length, with each element in each inner list being a string of each length
    width = len(map[0])*2 + 2 # width of shape outputted
    sides_vertical = "+" + "-" * width + "+"
    
    need_to_join = (type(map[0]) == list)
    print(sides_vertical)
    for line in map:
        if need_to_join:
            print("| " + " ".join(line) + " |") 
        else:
            print("| ", end='')
            for s in line:
                print(s, end=" ")
            print(" |")

    print(sides_vertical)

def draw_map(game_map, fog, player):

    map_with_fog = [''] * h
    for h1 in range(h):
        for w1 in range(w):
            if fog[h1][w1] == "1":
                map_with_fog[h1] = map_with_fog[h1] + game_map[h1][w1]
                #print(game_map[h][w], end="")
            else:
                map_with_fog[h1] = map_with_fog[h1] + "?"
                #print("?", end="")
    wrap_map(map_with_fog)


#draw_map(map_struct, fog, 1)
print(clear_fog(map_struct,fog,player))