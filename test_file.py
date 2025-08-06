
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


def arr_of_str_to_2darr(list: list, reverse: bool): # reverse function for if you want 2darr to str instead of str to 2darr 
    out = []
    if reverse:
        for line in list:
            out.append("".join(line))
    else:
        for i in range(len(list)): 
            out.append([])
            for chr in list[i]:
                out[i].append(chr)

    return out


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


def initialize_game(game_map, fog, player):
    # initialize map
    game_map = load_map("level1.txt", game_map)
    
    # TODO: initialize fog
    for i in range(MAP_HEIGHT):
        fog.append([])
        for j in range(MAP_WIDTH):
            fog[i].append("0")

    
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
    player['turns'] = 0
    player['save_name'] = 'new'
    player['portal_position'] = "no portal placed right now."
    player['pickaxe_lvl'] = 0
    player['current_load'] = 0

    return game_map, fog, player


def initialize_game(game_map, fog, player):
    # initialize map
    game_map = load_map("level1.txt", game_map)
    
    # TODO: initialize fog
    for i in range(MAP_HEIGHT):
        fog.append([])
        for j in range(MAP_WIDTH):
            fog[i].append('0')

    
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
    player['turns'] = 0
    player['save_name'] = 'new'
    player['portal_position'] = "no portal placed right now."
    player['pickaxe_lvl'] = 0
    player['current_load'] = 0

    return game_map, fog, player


def save_game(game_map, fog, player):

    # checks if a save folder exists. if not, creates folder
    save_folder = "saves"
    if not os.path.exists(save_folder):
        os.mkdir('saves')

    # get the current saves available 
    saves_list = os.listdir(save_folder)

    
    if player['save_name'] not in saves_list:
        save_no = "save_#" + str(len(saves_list)+1)
        player['save_name'] = save_no
        particular_save_file = os.path.join(save_folder, save_no + '.json')
    else:
        particular_save_file = os.path.join(save_folder, player['save_name'] + '.json')

    # add fog and map to dictnary written to save file
    player['fog'] = arr_of_str_to_2darr(fog, True)
    player['map'] = arr_of_str_to_2darr(game_map, True)

    # open file and write to save file
    save_file = open(particular_save_file, 'w')
    player_info_json = json.dumps(player, indent=1)
    save_file.write(player_info_json)

    save_file.close()
    
    return


def load_game(game_map, fog, player):   
    save_folder = 'saves'
    if not os.path.exists(save_folder) or (os.listdir(save_folder) == []):
        print("There are no available saves for you to load!")
        if input("Do you want to start a new game? [y/n] ") == 'y':
            return initialize_game(game_map, fog, player)

    else:
        # show available saves and ask usr for which save to load
        saves_list = os.listdir(save_folder)
        print("----- Saves List -----")
        for save_idx in range(len(saves_list)):
            print(f" {save_idx+1}. {saves_list[save_idx][:-5]}")


        save_to_load = input("\nWhich save do you want to load, plaese enter the corresponding number? ")

        try: # to ensure that input can be read as an integer
            save_to_load = int(save_to_load) - 1
        except:
            print("\nPlease enter the save number.")
            save_to_load = int(input("\nWhich save do you want to load, plaese enter the corresponding number? ")) - 1


        while (-1 >= save_to_load) and (save_to_load >= len(saves_list)): # since this gets a number, outside of the use case of the above valid_usr_input function
            print("\nThats not a valid option! Please try again...")
            save_to_load = int(input("\nWhich save do you want to load, plaese enter the corresponding number? ")) - 1
        
        # load save info
        save_path = os.path.join(save_folder, saves_list[save_to_load])
        save_file = open(save_path, 'r')
        data_raw = json.load(save_file)
        
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
    

game_map, fog, player = load_game(game_map, fog, player)
print(player)