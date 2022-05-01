#!/usr/bin/python3

import os, sys, pyaes, random, base64, hashlib, json, argparse, loguru, getpass, uuid, time

HOME = os.environ["HOME"]
pk_dir = HOME + "/.pk"
pk_vaults = pk_dir + "/vaults"
logger = loguru.logger

if not os.path.exists(pk_dir):
    logger.debug("pk directory not found, created new")
    os.mkdir(pk_dir)

if not os.path.exists(pk_dir + "/vaults"):
    os.mkdir(pk_dir + "/vaults")

default_config = {
        "default_vault": None,
        "auto_sync": False,
        "server_ip": "0.0.0.0",
        "server_port": 10900
        }

try:
    with open(pk_dir + "/config.json", "r") as f:
        config = json.loads(f.read())
except FileNotFoundError:
    logger.debug("config file not found, created new")
    config = default_config
    with open(pk_dir + "/config.json", "w") as f:
        f.write(json.dumps(config))

def write_config():
    with open(pk_dir + "/config.json", "w") as f:
        f.write(json.dumps(config))

def vault_exists(name):
    return os.path.exists(pk_vaults + "/" + stringify(name) + ".json")

# this script relys on md5 hashing for passwords, sue me
# mainly did because it fit in the aes key size
# wouldve used sha1 or sha256 but oh well, livin on the edge

# salts come later

# wtf
# i just realized
# i cant use the same hash i keep in the db for the encryption key
# why am i so dumb
# ooh
# what if i keep a sha256 hash in the db and use md5 for the key?
# whatever, its literally midnight and it sounds like a good idea

def encrypt(key, data): # returns base64 of encrypted data
    return base64.b64encode(pyaes.AESModeOfOperationCTR(key).encrypt(data))

def decrypt(key, data): # returns bytes of decrypted data
    return pyaes.AESModeOfOperationCTR(key).decrypt(base64.b64decode(data))

def stringify(name):
    output = ""
    for i in name:
        i = i.lower()
        if ord(i) in list(range(97, 123)) or ord(i) in list(range(48, 58)) or ord(i) in list(range(65, 91)):
            output += i
        else:
            output += "-"
    return output

class Vault():
    def __init__(self, name=None, uuid=None, content=None, key=None, encrypted=False):
        self.name = name
        self.uuid = uuid
        self.content = content
        self.key = key
        self.encrypted = encrypted
        self.created = int(time.time())
        self.last_updated = int(time.time())

    def loadFromFile(self, filename):
        with open(filename, "r") as f:
            data = json.loads(f.read())
            self.name = data["name"]
            self.uuid = data["uuid"]
            self.content = data["content"]
            self.encrypted = data["encrypted"]
            self.key = data["key"]
            self.created = data["created"]
            self.last_updated = data["last_updated"]

        if self.encrypted:
            self.decrypt()

    def writeToFile(self, filename):
        with open(filename, "w") as f:
            f.write(json.dumps({
                "name": self.name,
                "uuid": self.uuid,
                "content": self.content,
                "key": self.key,
                "encrypted": self.encrypted,
                "created": self.created,
                "last_updated": int(time.time())
                }))

    def __repr__(self):
        return f"Vault(name='{self.name}', uuid='{self.uuid}')"

class VaultManager():
    def __init__(self):
        self.vaults = []

    def loadVault(self, name):
        vault = None
        for i in self.vaults:
            if name == i.name:
                vault = i
        if not vault:
            for i in self.vaults:
                if name == i.uuid:
                    vault = i
        return vault

    def addVault(self, filename):
        vault = Vault()
        vault.loadFromFile(filename)
        self.vaults.append(vault)

    def removeVault(self, name):
        self.vaults.remove(self.loadVault(name))

    def __repr__(self):
        return f"VaultManager(vaults={len(self.vaults)})"

def get_default_vault():
    default_vault = config["default_vault"]
    if not default_vault:
        return None
    
    vault = Vault()
    vault.loadFromFile(pk_home + "/vaults/" + stringify(default_vault) + ".json")

    return vault

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

def do_create_vault(args):
    if vault_exists(args.name):
        print("vault already exists")
        exit(1)
    if len(args.name) > 33:
        print("vault name must be 32 characters or lower")
        exit(1)

    vault = Vault(name=args.name, uuid=str(uuid.uuid4()), encrypted=args.encrypted)
    if vault.encrypted:
        pass1 = ""
        while True:
            pass1 = getpass.getpass(prompt="enter vault password:    ")
            pass2 = getpass.getpass(prompt="re-enter vault password: ")
            if pass1 != pass2:
                print("passwords do not match")
                continue
            else:
                break
        vault.key = hashlib.sha256(pass1.encode("utf-8")).hexdigest()
        vault.content = encrypt(hashlib.md5(pass1.encode("utf-8")).hexdigest().encode("utf-8"), b"{}").decode("utf-8")
    else:
        vault.key = None
        vault.content = dict()
    vault.writeToFile(pk_vaults + "/" + stringify(args.name) + ".json")
    print(f"created new vault '{args.name}'")

def do_delete(args):
    pass

def do_delete_vault(args):
    pass

def do_default_vault(args):
    if get_default_vault() and not args.vault:
        print(get_default_vault())
    elif not get_default_vault() and not args.vault:
        print("no default vault")
    elif args.vault:
        if not vault_exists(args.vault):
            print("vault doesn't exist")
            exit(1)
        else:
            config["default_vault"] = args.vault
            write_config()

def do_change_password(args):
    pass

def do_cloud(args):
    pass

def do_sync(args):
    pass

actions = {
        "config": do_config,
        "list": do_list,
        "add": do_add,
        "get": do_get,
        "import": do_import,
        "create_vault": do_create_vault,
        "delete": do_delete,
        "delete_vault": do_delete_vault,
        "default_vault": do_default_vault,
        "change_password": do_change_password,
        "cloud": do_cloud,
        "sync": do_sync
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
    create_vault = subparser.add_parser("create_vault", help="Creates new vault")
    delete_vault = subparser.add_parser("delete_vault", help="Deletes vault")
    sync = subparser.add_parser("sync", help="Uploads/downloads vault information to/from the cloud")

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

    create_vault.add_argument("name", type=str, help="Vault name to create")
    create_vault.add_argument("--encrypted", action="store_true", help="Makes vault encrypted (requires password)")

    delete_vault.add_argument("name", type=str, help="Vault name to delete")

    conf_subparser = config.add_subparsers(dest = "command")
    default_vault = conf_subparser.add_parser("default_vault", help="Gets/sets the default vault")
    change_password = conf_subparser.add_parser("change_password", help="Changes the password for all or one vault(s)")
    cloud = conf_subparser.add_parser("cloud", help="Gets/sets the cloud IP/port address")

    default_vault.add_argument("--vault", type=str, required=False, help="Vault to set as the default")

    cloud.add_argument("--ip", type=str, required=False, help="IP for the cloud server")
    cloud.add_argument("--port", type=int, required=False, help="Port for the cloud server")

    args = parser.parse_args()

    if not args.command:
        parser.parse_args(["--help"])

    if not args.verbose:
        logger.remove()
    else:
        logger.debug(args)

    actions[args.command](args)

if __name__ == "__main__":
    main()
