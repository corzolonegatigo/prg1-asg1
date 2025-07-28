# small testing
import os
import json 

save_folder = "saves"
if not os.path.exists(save_folder):
    os.mkdir('saves')

saves_list = os.listdir(save_folder)

print(saves_list)

player = {'x':1, 'y':2, 'z':[1,23,4,5,6,], 'a': 'hello'}
json_obj = json.dumps(player)
outfile = open("jsontest.json", 'w')
outfile.write(json_obj)


outfile.close()

readfile = open('jsontest.json', 'r')
json_obj = json.load(readfile)

print(json_obj)
