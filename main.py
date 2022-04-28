#!/usr/bin/python3

import os, sys, pyaes, random, base64, hashlib, json, argparse, loguru, getpass

HOME = os.environ["HOME"]

if not os.path.exists(HOME + "/.pk"):
    os.mkdir(HOME + "/.pk")

if not os.path.exists(HOME + "/.pk/vaults"):
    os.mkdir(HOME + "/.pk/vaults")

logger = loguru.logger

def encrypt(key, data): # returns base64 of encrypted data
    return pyaes.AESModeOfOperationCTR(key).encrypt(data)

def decrypt(key, data): # returns bytes of decrypted data
    return pyaes.AESModeOfOperationCTR(key).decrypt(data)

def do_config(args):
    pass

def do_list(args):
    pass

def do_add(args):
    pass

def do_get(args):
    pass

def do_import(args):
    pass

def do_create(args):
    pass

def do_delete(args):
    pass

def do_delete_vault(args):
    pass

def do_default_vault(args):
    pass

def do_change_password(args):
    pass

actions = {
        "config": do_config,
        "list": do_list,
        "add": do_add,
        "get": do_get,
        "import": do_import,
        "create": do_create,
        "delete": do_delete,
        "delete_vault": do_delete_vault,
        "default_vault": do_default_vault,
        "change_password": do_change_password
}

# @logger.catch
def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-v", "--verbose", action="store_true", help="Turns on logging")

    subparser = parser.add_subparsers(dest = "command")

    config = subparser.add_parser("config", help="Get/set configuration")
    list_ = subparser.add_parser("list", help="List contents from a vault")
    add = subparser.add_parser("add", help="Add content to a vault")
    get = subparser.add_parser("get", help="Get content from a vault")
    delete = subparser.add_parser("delete", help="Deletes content from a vault")
    import_ = subparser.add_parser("import", help="Pours contents from a CSV into a vault")
    create = subparser.add_parser("create", help="Creates new vault")
    delete_vault = subparser.add_parser("delete_vault", help="Deletes vault")

    list_.add_argument("--vault", type=str, required=False, help="Vault to list")
    list_.add_argument("--type", type=str, required=False, help="Filter contents by type")

    add.add_argument("--vault", type=str, required=False, help="Vault to add content to")

    get.add_argument("name", type=str, help="Name of content to get")
    get.add_argument("--vault", type=str, required=False, help="Vault to get content from")

    delete.add_argument("name", type=str, help="Name of content to delete")
    delete.add_argument("--vault", type=str, help="Vault to delete content from")

    import_.add_argument("file name", type=str, help="CSV file name")
    import_.add_argument("--make-new-vault", action="store_true", help="Make a new vault if doesn't exist")
    import_.add_argument("vault", type=str, help="Vault to pour CSV content into")

    create.add_argument("name", type=str, help="Vault name to create")
    create.add_argument("--encrypted", action="store_true", help="Makes vault encrypted (requires password)")

    delete_vault.add_argument("name", type=str, help="Vault name to delete")

    conf_subparser = config.add_subparsers(dest = "command")
    default_vault = conf_subparser.add_parser("default_vault", help="Gets/sets the default vault")
    change_password = conf_subparser.add_parser("change_password", help="Changes the password for all or one vault(s)")

    default_vault.add_argument("--vault", type=str, required=False, help="Vault to set as the default")

    args = parser.parse_args()

    if not args.command:
        parser.parse_args(["--help"])

    if not args.verbose:
        logger.remove()

    actions[args.command](args)

    print(args)

if __name__ == "__main__":
    main()
