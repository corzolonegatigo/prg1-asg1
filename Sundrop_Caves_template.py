from random import randint
import os
import time

player = {}
game_map = []
fog = []

# const
MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 500

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_price = [50, 150]

prices = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)

# This function loads a map structure (a nested list) from a file
# It also updates MAP_WIDTH and MAP_HEIGHT

def arr_of_str_to_2darr(list: list): 
    out = []
    for i in range(len(list)): 
        out.append([])
        for chr in list[i]:
            out[i].append(chr)

    return out


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


def load_map(filename, map_struct):
    map_file = open(filename, 'r')
    global MAP_WIDTH
    global MAP_HEIGHT
    
    map_struct.clear()
    
    # TODO: Add your map loading code here
    map_raw = map_file.readlines()
    for i in range(len(map_raw)):
        map_struct.append(map_raw[i].strip("\n"))



    MAP_WIDTH = len(map_struct[0])
    MAP_HEIGHT = len(map_struct)

    map_file.close()

    return map_struct

def get_surrounding(x: int, y: int): # takes position, gets the bounds of the 3x3 area around it
    
    three_by_three = [['','',''],['','',''],['','','']]

    for yv in range(y-1, y+2):
        for xv in range(x-1, x+2):
            if ((0 <= xv) and (xv < MAP_WIDTH)) or ((0 <= yv) and (yv < MAP_HEIGHT)):
                three_by_three[yv][xv] = "#"
            else:
                three_by_three[yv][xv] = (xv, yv)
                

    return three_by_three

# This function clears the fog of war at the 3x3 square around the player
def clear_fog(map, fog, player):
   
    area_to_clear = get_surrounding(player['x'], player['y'])
    #there must be a faster way
    for row in area_to_clear:
        for item in row:
            if item != '#':
                fog[item[1]][item[0]] = 1
    
    return fog

def initialize_game(game_map, fog, player):
    # initialize map
    game_map = load_map("level1.txt", game_map)
    
    # TODO: initialize fog
    for i in range(MAP_HEIGHT):
        fog.append([])
        for j in range(MAP_WIDTH):
            fog[i].append(0)

    
    # TODO: initialize player
    #   You will probably add other entries into the player dictionary
    player['name'] = input("Greetings, miner! What is your name? ")
    player['bp_size'] = 10
    player['x'] = 0
    player['y'] = 0
    player['copper'] = 0
    player['silver'] = 0
    player['gold'] = 0
    player['GP'] = 0
    player['day'] = 0
    player['steps'] = 0
    player['turns'] = TURNS_PER_DAY

    clear_fog(fog, player)
    
# This function draws the entire map, covered by the fog
def draw_map(game_map, fog, player):

    map_with_fog = []
    for h in range(MAP_HEIGHT):
        map_with_fog.append([])

        for w in range(MAP_WIDTH):

            if fog[h][w]:
                map_with_fog[h].append(game_map[h][w])
            else:
                map_with_fog[h].append("?")

    wrap_map(map_with_fog)

    return None

# This function draws the 3x3 viewport
def draw_view(game_map, fog, player):

    viewarea = get_surrounding(player['x'], player['y'])
    view = [[],[],[]]
    for row in viewarea:
        for item in row:
            if item != "#":
                view.append(game_map[item[1]][item[0]])
            else:
                view.append('#')
            
    view[1][1] = 'M'
    wrap_map(view)

    return

# This function shows the information for the player

def show_information(player):
    return

# This function saves the game
def save_game(game_map, fog, player):

    save_folder = "saves"
    if not os.path.exists(save_folder):
        os.mkdir('saves')

    saves_list = os.listdir(save_folder)
    # save map
    # save fog
    # save player
    return
        
# This function loads the game
def load_game(game_map, fog, player):
    # load map
    # load fog
    # load player
    return


def show_main_menu():
    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
#    print("(H)igh scores")
    print("(Q)uit")
    print("------------------")
    potential_options = ['N','L','Q']

    choice = ''
    while choice not in potential_options:
        choice = input("Your choice?").upper()
    if choice == 'N':
        return initialize_game()
def show_town_menu():
    print()
    # TODO: Show Day
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------")
            

#--------------------------- MAIN GAME ---------------------------
game_state = 'main'
print("---------------- Welcome to Sundrop Caves! ----------------")
print("You spent all your money to get the deed to a mine, a small")
print("  backpack, a simple pickaxe and a magical portal stone.")
print()
print("How quickly can you get the 1000 GP you need to retire")
print("  and live happily ever after?")
print("-----------------------------------------------------------")

# TODO: The game!



#testing loop
initialize_game(game_map, fog, player)
    
    
