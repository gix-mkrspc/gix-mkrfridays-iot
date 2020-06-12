from pathlib import Path
import os
import sys
import fileinput
from shutil import copyfile

ESP8266_PACKAGE_PATH = Path("packages/esp8266/hardware/esp8266/")

# TODO: this is a work in progress and needs to be implemented!
def update_line_file(file_path, str_line_to_update, str_replacement, comment_only=False, comment_str=None):
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
    :param comment_str: Str to use for a comment if commenting
    :type comment_only str:
    :raises: :class:`FileNotFound`: File couldn't be opened

    :returns: whether the string was replaced in the file or it was commented out
    :rtype: boolean
    '''
    file_modified = False
    for line in fileinput.input(file_path, inplace=True):
        # TODO: determine if file already modified before changing file_modified
        if line.startswith(str_line_to_update):
            file_modified = True
            if comment_only:
                line = f"{comment_str} {line}"
            else:
                line = str_replacement
        sys.stdout.write(line)
        
    # ! Important; this updates an entire line! If the substring matches
    #  the line should be obliterated and replaced with str_replacement
    
    return file_modified


def main():
    if sys.platform == "darwin":
        ARDUINO_PACKAGES_PATH = Path(Path.home() / "Library/Arduino15")
    elif sys.platform == "linux":
        # TODO: add path here!
        ARDUINO_PACKAGES_PATH = Path(Path.home() / ".arduino15/packages/")
    elif sys.platform == "win32":
        # TODO: add path here!
        ARDUINO_PACKAGES_PATH = Path(Path.home() / "AppData/Local/Arduino15")

    # check if board path is set
    try:
        print(f"Arduino board path for platform {sys.platform} is: {str(ARDUINO_PACKAGES_PATH)}")
    except NameError:
        print(
            f"Error: no valid board path condition for platform: {sys.platform}")

    # Check for and change other versions if they exist
    versions = []
    with os.scandir(str(ARDUINO_PACKAGES_PATH / ESP8266_PACKAGE_PATH)) as entries:
        for version in entries:
            # avoid files and hidden files
            if version.is_dir and not version.name.startswith('.'):
                versions.append(Path(ARDUINO_PACKAGES_PATH / ESP8266_PACKAGE_PATH / version))

    for path in versions:
        arduino_header_file = Path(path / "cores/esp8266/Arduino.h")
        if arduino_header_file.exists():
            print(f"Updating: {str(arduino_header_file)}")
            # TODO: add logic to detect if backup file exists then skip
            copyfile(arduino_header_file, str(Path(path / "cores/esp8266/Arduino.h.orig")))
            print(f"Backup created: {str(Path(path / 'cores/esp8266/Arduino.h.orig'))}")
            get_update = update_line_file(str(arduino_header_file), "#define round(x)", str_replacement = None, comment_only = True, comment_str="//")
            print(f"Updated: {get_update} for  {arduino_header_file}")
        platform_txt_file = Path(path / "platform.txt")
        if platform_txt_file.exists():
            print(f"Updating: {str(platform_txt_file)}")
            copyfile(platform_txt_file, str(Path(path / "platform.txt.orig")))
            print(f"Backup created: {str(Path(path / 'platform.txt.orig'))}")
            get_update = update_line_file(str(platform_txt_file), "build.extra_flags=", str_replacement = "build.extra_flags=-DESP8266 -DDONT_USE_UPLOADTOBLOB -DUSE_BALTIMORE_CERT")
            print(f"Updated: {get_update} for  {platform_txt_file}")

main()


