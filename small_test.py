# small testing
import os

save_folder = "saves"
if not os.path.exists(save_folder):
    os.mkdir('saves')

saves_list = os.listdir(save_folder)

print(saves_list)