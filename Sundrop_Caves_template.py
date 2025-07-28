from random import randint
import os
import time
import json
from copy import deepcopy

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
    player['save_name'] = 'new'
    player['portal_position'] = "no portal placed right now."
    player['pickaxe_lvl'] = 1
    player['current_load'] = 0

    return game_map, fog, player
    
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
    print()

    print("----- Player Information -----")
    print("Name:", player['name'])
    print("Portal position:", player['portal_position'])
    print(f"Pickaxe level: {player['pickaxe_lvl']} ({minerals[player['pickaxe_lvl']]})") # using the mineral ranking as the pickaxe material ranking for now
    print("Gold:", player['gold'])
    print("Silver:", player['silver'])
    print("Bronze:", player['bronze'])
    print("------------------------------")

    print(f"Load: {player['current_load']} / {player['bp_size']}")
    print("------------------------------")

    print("GP:", player['GP'])
    print("Steps taken:", player['steps'])
    print("------------------------------")


# This function saves the game
def save_game(game_map, fog, player):

    # checks if a save folder exists. if not, creates folder
    save_folder = "saves"
    if not os.path.exists(save_folder):
        os.mkdir('saves')

    # get the current saves available 
    saves_list = os.listdir(save_folder)

    
    if player['save_name'] not in saves_list:
        save_no = "save_#" + str(len(saves_list+1))
        player['save_name'] = save_no
        particular_save_file = os.path.join(save_folder, save_no + '.json')
    else:
        particular_save_file = os.path.join(save_folder, player['save_name'] + '.json')

    # add fog and map to dictnary written to save file
    player['fog'] = fog
    player['map'] = game_map

    # open file and write to save file
    save_file = open(particular_save_file, 'w')
    player_info_json = json.dumps(player)
    save_file.write(player_info_json)

    save_file.close()
    
    return
        
# This function loads the game
def load_game():   
    save_folder = 'saves'
    if not os.path.exists(save_folder) or (os.listdir(save_folder) == []):
        print("There are no available saves for you to load!")
        if input("Do you want to start a new game? [y/n] ") == 'y':
            return initialize_game()

    else:
        # show available saves and ask usr for which save to load
        saves_list = os.listdir(save_folder)
        print("----- Saves List -----")
        for save_idx in range(len(saves_list)):
            print(f" {save_idx+1}. {saves_list[save_idx][:5]}")

        save_to_load = int(input("\nWhich save do you want to load, plaese enter the corresponding number? ")) - 1
        while -1 < save_to_load < len(save_folder):
            print("\nThats not a valid option! Please try again...")
            save_to_load = int(input("\nWhich save do you want to load, plaese enter the corresponding number? ")) - 1
        
        # load save info
        save_path = os.path.join(save_folder, saves_list[save_to_load] + '.json')
        save_file = open(save_path, 'r')
        data_raw = json.loads(save_file)
        
        # write the map and fog from save to the respective vars
        game_map = data_raw['map']
        fog = data_raw['fog']

        # gets map width + map height
        global MAP_WIDTH
        global MAP_HEIGHT

        MAP_WIDTH = len(game_map[0])
        MAP_HEIGHT = len(game_map)
       
        # creates a deepcopy of the dictionary read from the .json file
        player = deepcopy(data_raw)

        # remove map and fog from player
        del player['map']
        del player['fog']

        return game_map, fog, player
    


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
    elif choice == 'L':
        return load_game()
    
    else:
        print("buh bye")
        return None
    
    
def show_town_menu(player):
    print(f"Day {player['day']}")
    # TODO: Show Day    
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------")
    
    options = ["B", "I", "M", "E", "V", "Q"]
    choice = input("Your choice? ")
    if choice not in options:
        print("\nThats not a valid option! Please try again...")
        choice = input("Your choice? ")



            

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




    
