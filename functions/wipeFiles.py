import os
def wipe_files(file_path):
     for file in os.listdir(file_path):
          print(f"Removed File: {file}")
          os.remove(f"{file_path}/{file}")