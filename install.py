#!/usr/bin/env python3

"""Dotfiles installation script

Must be run from the dotfiles main directory.
"""

import argparse
import io
import os
from pathlib import Path
import string
import subprocess
import tarfile

"""Templates to substitute in files. Installation script will ask the user to 
fill in this information and will substitute the placeholders in the given file
by the information provided.
Missing placeholders will be ignored with a warning.

Dictionary keys are the templated files located in the dotfiles. Dictionary
items are the placeholders, which will be replaced by user input. Placeholders
cannot have spaces!
"""
TEMPLATES = {
    # example:
    # "./template_file": ["full_name", "email", "user"]
}

"""Files for which a symlink will be created. Key is source file and value is 
the location where symlink to source will be saved.
"""
SYMLINK_FILES = {
    "./bash/bashrc": "~/.bashrc",
    "./fish/config.fish": "~/.config/fish/config.fish",
    "./gdb/gdbinit": "~/.config/gdb/gdbinit",
    "./git/gitconfig": "~/.gitconfig",
    "./htop/htoprc": "~/.config/htop/htoprc",
    "./python/ipython_config.py": "~/.ipython/profile_default/ipython_config.py",
    "./ssh/ssh_config": "~/.ssh/config",
    "./tmux/tmux.conf": "~/.tmux.conf",
    "./vscode/settings.json": "~/.config/Code/User/settings.json",
}

"""Set permissions for files.
"""
FILE_PERMISSIONS = {
    "./ssh/ssh_config": 0o600,
}

"""Archive files which are extracted during installation and packed to save 
changes. Key is the archive name and value is the folder saved in the archive.
"""
ARCHIVE_FILES = {
}


def query_yes_no(question):

    VALID_INPUT = {
        True: ["yes", "y"],
        False: ["no", "n"]}

    while True:
        user_in = input(question + " (y/n): ").lower()

        if user_in in VALID_INPUT[True]:
            return True
        elif user_in in VALID_INPUT[False]:
            return False
        else:
            print("Please answer with 'y' or 'n'")


def process_templates():
    """Substitutes placeholders in templated files with information provided by
    the user.
    """

    print("Processing templates")

    for file, placeholders in TEMPLATES.items():

        file = Path(os.path.abspath(Path(file).expanduser()))

        if not file.exists():
            raise RuntimeError(
                "Could not find path for the file '{}'".format(file))

        # create dict to store user input
        placeholders = dict.fromkeys(placeholders)
        for placeholder in placeholders:
            placeholders[placeholder] = input(
                "Enter information for {}: ".format(placeholder))

        file_data = file.read_text()
        template = string.Template(file_data)
        file_data = template.substitute(placeholders)
        file.write_text(file_data)


def pack_files():
    """Packs files into an AES encrypted tar archive

    Based on commands:
    tar -cvpf archive.tar ./
    openssl aes256 -e -salt -pbkdf2 -in archive.tar -out archive.tar.aes
    """

    print("Packing files")

    for encrypted_tar_file, folder in ARCHIVE_FILES.items():

        # create archive file
        encrypted_tar_file = Path(
            os.path.abspath(Path(encrypted_tar_file).expanduser()))

        if encrypted_tar_file.exists():
            print("Archive file '{}' already exists.".format(encrypted_tar_file))

            if query_yes_no("Overwrite file?"):
                print("Deleting '{}'".format(encrypted_tar_file))
                encrypted_tar_file.unlink()

            else:
                print("Skipping packing of '{}'".format(encrypted_tar_file))
                continue

        # get files to be included in the archive
        folder = Path(os.path.abspath(Path(folder).expanduser()))

        # create .tar file in memory
        tar_data = io.BytesIO()
        tar_file = tarfile.open(fileobj=tar_data, mode='w')
        # add files in the specified folder
        # relative to parent of archive to avoid getting wrong path
        # when extracting archive
        tar_file.add(folder.relative_to(encrypted_tar_file.parent))
        tar_file.close()

        # needed otherwise read returns emptys
        tar_data.seek(0)

        # generate encrypted data
        encrypted_tar_data, _ = subprocess.Popen(
            ["openssl", "aes256", "-e", "-salt", "-pbkdf2"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE).communicate(input=tar_data.read())

        # write encrypted data
        encrypted_tar_file.write_bytes(encrypted_tar_data)
        tar_data.close()

        assert tar_file.closed and tar_data.closed

    return


def unpack_files():
    """Unpacks files of an AES encrypted tar archive

    Based on commands:
    tar -cvpf archive.tar ./
    openssl aes256 -e -salt -pbkdf2 -in archive.tar -out archive.tar.aes
    """

    print("Unpacking files")

    for encrypted_tar_file, folder in ARCHIVE_FILES.items():

        # create archive file
        encrypted_tar_file = Path(
            os.path.abspath(Path(encrypted_tar_file).expanduser()))

        if not encrypted_tar_file.exists():
            print("Archive file '{}' does not exist.".format(encrypted_tar_file))
            print("Skipping unpacking of '{}'".format(encrypted_tar_file))
            continue

        decrypted_tar_data, _ = subprocess.Popen(
            ["openssl", "aes256", "-d", "-salt", "-pbkdf2"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE).communicate(input=encrypted_tar_file.read_bytes())

        # create .tar file in memory
        tar_data = io.BytesIO(decrypted_tar_data)
        tar_file = tarfile.open(fileobj=tar_data, mode='r')

        # check if unpacking will overwrite any files
        tar_key_files = [
            file_info.name for file_info in tar_file.getmembers()]

        key_files = [
            file_path.name for file_path in sorted(encrypted_tar_file.parent.glob("./*"))]

        if len(set(key_files) & set(tar_key_files)):
            print("Unpacking the archive '{}' will cause (a) file(s) to be overwritten.".format(
                encrypted_tar_file))

            if not query_yes_no("Overwrite file(s)?"):
                print("Skipping unpacking of '{}'".format(encrypted_tar_file))
                continue

        tar_file.extractall(path=encrypted_tar_file.parent)

        tar_file.close()
        tar_data.close()

        assert tar_file.closed and tar_data.closed

    return


def fix_permissions():

    print("Fixing file permissions")

    for dotfile, permission in FILE_PERMISSIONS.items():

        dotfile = Path(os.path.abspath(Path(dotfile).expanduser()))

        if not dotfile.exists():
            print(
                "Could not find path for the file '{}'".format(dotfile))
            continue

        dotfile.chmod(permission)


def create_symlinks():

    print("Creating symlinks for configuration files")

    # Overwrite system files with dotfile files
    for dotfile, sysfile in SYMLINK_FILES.items():

        # Dotfile config file
        dotfile = Path(os.path.abspath(Path(dotfile).expanduser()))

        if not dotfile.exists():
            raise RuntimeError(
                "Could not find path for the file '{}'".format(dotfile))

        if not query_yes_no("Create symlink for dotfile '{}'?".format(dotfile)):
            print("Skipping installation of '{}'".format(dotfile))
            continue

        # System config file
        sysfile = Path(os.path.abspath(Path(sysfile).expanduser()))

        if sysfile.exists() or sysfile.is_symlink():
            print("System config file '{}' already exists.".format(sysfile))

            if query_yes_no("Overwrite file?"):
                print("Deleting '{}'".format(sysfile))
                sysfile.unlink()
            else:
                print("Skipping installation of '{}'".format(dotfile))
                continue

        else:
            # if file does not exist, maybe its parent directories also don't exist
            sysfile.parent.mkdir(parents=True, exist_ok=True)

        # Creating symlink
        print("Creating symlink for dotfile config file '{}' to system config file '{}'"
              .format(dotfile, sysfile))

        sysfile.symlink_to(dotfile)


def main():

    parser = argparse.ArgumentParser(
        description="Dotfiles installation utility")
    parser.add_argument(
        # action="store_const",
        "command", choices=["install", "pack", "unpack", "permissions"], nargs=1,
        help="desired command")
    args = parser.parse_args()

    print("Dotfiles installation utility")

    if "unpack" in args.command:
        unpack_files()
        fix_permissions()

    elif "install" in args.command:
        fix_permissions()
        create_symlinks()

    elif "pack" in args.command:
        fix_permissions()
        pack_files()

    elif "permissions" in args.command:
        fix_permissions()

    else:
        raise RuntimeError("Unexpected condition.")


if __name__ == "__main__":
    main()
