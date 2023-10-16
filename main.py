import httpx
import base64
import time
import colorama
from json import loads
from colorama import Fore, init
from time import strftime
import os
from art import *
from colorama import Fore, init

init(autoreset=True)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

texto_personalizado = f"{Fore.RED}"
texto_personalizado += """

#    ▄▄▄▄    ██▀███   ▒█████   ██ ▄█▀▓█████  ███▄    █ 
#   ▓█████▄ ▓██ ▒ ██▒▒██▒  ██▒ ██▄█▒ ▓█   ▀  ██ ▀█   █ 
#   ▒██▒ ▄██▓██ ░▄█ ▒▒██░  ██▒▓███▄░ ▒███   ▓██  ▀█ ██▒
#   ▒██░█▀  ▒██▀▀█▄  ▒██   ██░▓██ █▄ ▒▓█  ▄ ▓██▒  ▐▌██▒
#   ░▓█  ▀█▓░██▓ ▒██▒░ ████▓▒░▒██▒ █▄░▒████▒▒██░   ▓██░
#   ░▒▓███▀▒░ ▒▓ ░▒▓░░ ▒░▒░▒░ ▒ ▒▒ ▓▒░░ ▒░ ░░ ▒░   ▒ ▒ 
#   ▒░▒   ░   ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░▒ ▒░ ░ ░  ░░ ░░   ░ ▒░
#    ░    ░   ░░   ░ ░ ░ ░ ▒  ░ ░░ ░    ░      ░   ░ ░ 
#    ░         ░         ░ ░  ░  ░      ░  ░         ░ 
#         ░                                            

"""
clear_terminal()

print(texto_personalizado)

init(autoreset=True)

def print_message(text: str) -> None:
    """
    Print a formatted message with a timestamp.
    """
    formatted_text = (
        f"{Fore.LIGHTWHITE_EX}[{Fore.CYAN}{strftime('%H:%M:%S')}{Fore.LIGHTWHITE_EX}] {text}"
        .replace('[+]', f'[{Fore.LIGHTGREEN_EX}+{Fore.LIGHTWHITE_EX}]')
        .replace('[*]', f'[{Fore.LIGHTYELLOW_EX}*{Fore.LIGHTWHITE_EX}]')
        .replace('[>]', f'[{Fore.CYAN}>{Fore.LIGHTWHITE_EX}]')
        .replace('[-]', f'[{Fore.RED}-{Fore.LIGHTWHITE_EX}]')
    )
    print(formatted_text)

class DiscordAPI:
    def __init__(self, token: str, server_id: str) -> None:
        self.token = token
        self.server_id = server_id
        self.base_url = f"https://discord.com/api/v9/guilds/{self.server_id}"
        self.session = httpx.Client()
        self.headers = {"Authorization": self.token}

    def make_request(self, url) -> dict:
        """
        Make a GET request to the Discord API.
        """
        response = self.session.get(url=url, headers=self.headers)
        return response.json()

    def get_channels(self) -> dict:
        """
        Get a list of channels in the server.
        """
        return self.make_request(f"{self.base_url}/channels")

    def get_server_info(self) -> dict:
        """
        Get information about the server.
        """
        return self.make_request(self.base_url)

    def get_server_data(self) -> dict:
        """
        Get data about the server, including channels, roles, and emojis.
        """
        server_info = self.get_server_info()
        return {
            "info": server_info,
            "channels": self.get_channels(),
            "roles": server_info["roles"],
            "emojis": server_info["emojis"],
        }

class ServerCreator:
    def __init__(self, token: str, server_data: dict, server_id: str) -> None:
        self.token = token
        self.base_url = "https://discord.com/api/v9"
        self.session = httpx.Client()
        self.server_data = server_data
        self.server_id = server_id  
        self.headers = {"Authorization": self.token}
        self.delay = 0.5  


    def create_server(self):
        """
        Create a new server.
        """
        print_message("[>] Creating server")
        img_url = f"https://cdn.discordapp.com/icons/{self.server_data['info']['id']}/{self.server_data['info']['icon']}.webp?size=96"
        img = f"data:image/png;base64,{base64.b64encode(self.session.get(img_url).content).decode('utf-8')}"
        data = {
            "name": self.server_data["info"]["name"],
            "icon": img,
            "channels": [],
            "system_channel_id": None,
            "guild_template_code": "8ewECn5UKpDY",
        }

        response = self.session.post(
            url=f"{self.base_url}/guilds",
            headers=self.headers,
            json=data,
        ).json()

        self.server_id = response["id"]
        self.everyone_role_id = response["roles"][0]["id"]
        role_url = f"{self.base_url}/guilds/{self.server_id}/roles/{self.everyone_role_id}"
        role_data = {
            "name": "@everyone",
            "permissions": "1071698529857",
            "color": 0,
            "hoist": False,
            "mentionable": False,
            "icon": None,
            "unicode_emoji": None,
        }
        self.session.patch(
            url=role_url,
            headers=self.headers,
            json=role_data,
        )

        server_url = f"{self.base_url}/guilds/{self.server_id}"
        server_data = {
            "features": ["APPLICATION_COMMAND_PERMISSIONS_V2", "COMMUNITY"],
            "verification_level": 1,
            "default_message_notifications": 1,
            "explicit_content_filter": 2,
            "rules_channel_id": "1",
            "public_updates_channel_id": "1",
        }
        self.session.patch(
            url=server_url,
            headers=self.headers,
            json=server_data,
        )

        print_message(f"[+] Created server {self.server_data['info']['name']} -> {response['id']}")

    def delete_channels(self):
        """
        Delete existing channels in the server.
        """
        channels = self.session.get(
            url=f"{self.base_url}/guilds/{self.server_id}/channels",
            headers=self.headers,
        ).json()

        for channel in channels:
            status_code = self.session.delete(
                url=f"{self.base_url}/channels/{channel['id']}",
                headers=self.headers,
            ).status_code

            if status_code == 200:
                print_message(f"[+] Deleted channel {channel['name']} -> {status_code}")
            else:
                print_message(f"[-] Failed to delete channel {channel['name']} -> {status_code}")

    def create_channels(self):
        """
        Create channels in the server.
        """
        parent_channels = sorted([channel for channel in self.server_data["channels"] if channel["type"] == 4], key=lambda x: x["position"])
        parent_channel_ids = {}

        print_message(f"[>] Creating {len(parent_channels)} parent channels")

        for channel in parent_channels:
            data = {
                "name": channel["name"],
                "type": channel["type"],
                "permission_overwrites": channel["permission_overwrites"],
            }

            response = self.session.post(
                url=f"{self.base_url}/guilds/{self.server_id}/channels",
                headers=self.headers,
                json=data,
            )

            if response.status_code == 201:
                print_message(f"[+] Created channel {channel['name']} -> {response.status_code}")
                parent_channel_ids[channel["id"]] = response.json()["id"]
                time.sleep(self.delay)
            else:
                print_message(f"[-] Failed to create channel {channel['name']} -> {response.status_code}")

        print_message(f"[>] Creating {len(self.server_data['channels']) - len(parent_channels)} channels")

        for channel in self.server_data["channels"]:
            if channel["type"] == 4:
                continue

            data = {
                "name": channel["name"],
                "type": channel["type"],
                "permission_overwrites": channel["permission_overwrites"],
            }

            if channel["parent_id"]:
                data["parent_id"] = parent_channel_ids[channel["parent_id"]]

            response = self.session.post(
                url=f"{self.base_url}/guilds/{self.server_id}/channels",
                headers=self.headers,
                json=data,
            )

            if response.status_code == 201:
                print_message(f"[+] Created channel {channel['name']} -> {response.status_code}")
                time.sleep(self.delay)
            else:
                print_message(f"[-] Failed to create channel {channel['name']} -> {response.status_code}")

    def create_roles(self):
        """
        Create roles in the server.
        """
        roles = self.server_data["roles"]
        roles = sorted(roles, key=lambda x: x["position"], reverse=True)

        print_message(f"[>] Creating {len(roles)} roles")

        for role in roles:
            if role["name"] == "@everyone":
                for channel in self.server_data["channels"]:
                    for permission in channel["permission_overwrites"]:
                        if permission["id"] == role["id"]:
                            permission["id"] = self.everyone_role_id
                continue
            data = {
                "name": role["name"],
                "permissions": role["permissions"],
                "color": role["color"],
                "hoist": role["hoist"],
                "mentionable": role["mentionable"],
                "icon": None,
                "unicode_emoji": None,
            }

            response = self.session.post(
                url=f"{self.base_url}/guilds/{self.server_id}/roles",
                headers=self.headers,
                json=data,
            )

            if response.status_code == 200:
                print_message(f"[+] Created role {role['name']} -> {response.status_code}")
                for channel in self.server_data["channels"]:
                    if channel["type"] == 4:
                        continue

                    for permission in channel["permission_overwrites"]:
                        if permission["id"] == role["id"]:
                            permission["id"] = response.json()["id"]
                time.sleep(self.delay)
            else:
                print_message(f"[-] Failed to create role {role['name']} -> {response.status_code}")

    def create_emojis(self):
        """
        Create emojis in the server.
        """
        emojis = self.server_data["emojis"]
        print_message(f"[>] Creating {len(emojis)} emojis" if emojis else "[!] No emojis to create")

        for emoji in emojis:
            img_url = f"https://cdn.discordapp.com/emojis/{emoji['id']}.png"
            img = f"data:image/png;base64,{base64.b64encode(self.session.get(img_url).content).decode('utf-8')}"
            data = {
                "name": emoji["name"],
                "image": img,
                "roles": emoji["roles"]
            }
            status_code = self.session.post(
                url=f"{self.base_url}/guilds/{self.server_id}/emojis",
                headers=self.headers,
                json=data,
            ).status_code

            if status_code == 201:
                print_message(f"[+] Created emoji {emoji['name']} -> {status_code}")
                time.sleep(self.delay)
            else:
                print_message(f"[-] Failed to create emoji {emoji['name']} -> {status_code}")

    def all(self):
        """
        Execute all tasks to create the server.
        """
        tasks = [
            self.create_server,
            self.delete_channels,
            self.create_channels,
            self.create_roles,
            self.create_emojis,
        ]
        for task in tasks:
            try:
                task()
            except Exception as e:
                print_message(f"[*] {e}")
                pass

if __name__ == "__main__":
    config = loads(open("config.json", "r").read())
    token = config["token"]
    
    source_server_id = input(f"{Fore.RED}[?] ID do Servidor Que voce que copiar: {Fore.RESET}")
    destination_server_id = input(f"{Fore.RED}[?] ID do Seu Servidor Original: {Fore.RESET}")

    
    source_server_data = DiscordAPI(token, source_server_id).get_server_data()
    server_creator = ServerCreator(token, source_server_data, destination_server_id)
    server_creator.all()
