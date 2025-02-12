# Small signal probe station S2P to ADS compatible file

import os
import glob

def process_s2p(input):
    with open(input, 'r') as file:
        lines = file.readlines()
    
    # Delete 3rd 4th 5th lines, delete last 2 lines
    remove = {2, 3, 4, 6}  
    modified_lines = [line for i, line in enumerate(lines) if i not in remove]
    modified_lines = modified_lines[:-1]

    output = os.path.join(os.path.join(os.path.dirname(input), f"ads_{os.path.basename(input)}"))
    with open(output, 'w') as file:
        file.writelines(modified_lines)

    print("Exported to " + output)

def import_folder(folder_path):
    s2p_files = glob.glob(os.path.join(folder_path, '*.s2p'))
    for file_path in s2p_files:
        process_s2p(file_path)

folder_path = input("Enter folder path: ")
import_folder(folder_path)

