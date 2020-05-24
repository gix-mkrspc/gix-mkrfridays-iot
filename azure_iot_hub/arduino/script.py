from pathlib import Path
import os
import sys
import fileinput
from shutil import copyfile

ESP8266_PACKAGE_PATH = Path("packages/esp8266/hardware/esp8266/")

# TODO: this is a work in progress and needs to be implemented!
def update_line_file(file_path, str_line_to_update, str_replacement, comment_only):
    '''
    Updates a line on a file with a replacement line or comments it out

    :param file_path: The path to the file 
    :type file_path: str
    :param str_to_update: The string which will be replaced
    :type str_to_update str:
    :param str_replacement: The string which replace the line of str_to_update
    :type str_replacement str:
    :param comment_only: Determines whether to replace or only comment out a line
    :type comment_only boolean:
    :raises: :class:`FileNotFound`: File couldn't be opened

    :returns: whether the string was replaced in the file or it was commented out
    :rtype: boolean
    '''
    file_modified = False
    for line in fileinput.input(file_path, inplace=True):
        if line.startswith(str_line_to_update):
            if comment_only:
                line = "// " + line
            else:
                line = line.replace(str_line_to_update, str_replacement)
            file_modified = True
        print (line)
        
    # ! Important; this updates an entire line! If the substring matches
    #  the line should be obliterated and replaced with str_replacement
    
    return file_modified


def main():
    # NOTE: You should use forward slashes with pathlib functions.
    # The Path() object will convert forward slashes into the correct k
    # ind of slash for the current operating system. Nice!

    # If you want to add on to the path, you can use the / operator directly in your code.
    # Say goodbye to typing out os.path.join(a, b) over and over.
    # See: https://bit.ly/3gfS7D8 for more info
    if sys.platform == "darwin":
        ARDUINO_PACKAGES_PATH = Path(Path.home() / "Library/Arduino15")
    elif sys.platform == "linux":
        # TODO: add path here!
        ARDUINO_PACKAGES_PATH = Path(Path.home() / ".arduino15/packages/")
        print("it's linux i broke it")
    elif sys.platform == "win32":
        # TODO: add path here!
        ARDUINO_PACKAGES_PATH = Path(Path.home() / "AppData/Local/Arduino15")
        print("it's Windows")

    # check if board path is set
    try:
        print(f"Your Arduino board path for platform {sys.platform} is: {str(ARDUINO_PACKAGES_PATH)}")
    except NameError:
        print(
            f"Error: no valid board path condition for platform: {sys.platform}")

    versions = []
    with os.scandir(str(ARDUINO_PACKAGES_PATH / ESP8266_PACKAGE_PATH)) as entries:
        for version in entries:
            # avoid files and hidden files
            if version.is_dir and not version.name.startswith('.'):
                versions.append(Path(ARDUINO_PACKAGES_PATH / ESP8266_PACKAGE_PATH / version))

    for path in range(len(versions)):
        versions[path] = Path(versions[path] / "cores/esp8266/")

    for path in versions:
        arduino_header_file = Path(path / "Arduino.h")
        if arduino_header_file.exists():
            copyfile(arduino_header_file, str(Path(path / "Arduino.h.orig")))
            print(f"Updating {str(arduino_header_file)}")
            # TODO: implement change to comment code{}
            get_update = update_line_file(str(arduino_header_file), "#define round(x)", str_replacement = None, comment_only = True)
            print(get_update)
main()


