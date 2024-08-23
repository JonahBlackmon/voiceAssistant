from configparser import ConfigParser
def get_default():
    config = ConfigParser()
    config.read('config.ini')
    file_path = config['DEFAULT']['FILE_PATH']
    return file_path