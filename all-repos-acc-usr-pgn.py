import requests
import logging
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import os

def add_collaborator(owner_username, collaborator_username, token):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    # Get all repositories for the owner
    repositories = get_repos(owner_username, token)
    # Iterate through repositories and add collaborator
    for repo in repositories["repos"]:
        repo_name = repo['name']
        repo_full_name = repo['full_name']
        collaborator_url = f'https://api.github.com/repos/{repo_full_name}/collaborators/{collaborator_username}'
        # Check if the user is already a collaborator
        check_collaborator_response = requests.get(collaborator_url, headers=headers)
        if check_collaborator_response.status_code == 404:
            # User is not a collaborator, add them
            add_collaborator_response = requests.put(collaborator_url, headers=headers)
            if add_collaborator_response.status_code == 201:
                logging.info(f'Successfully added {collaborator_username} as a collaborator to {repo_full_name}')
            else:
                logging.error(f'Failed to add {collaborator_username} as a collaborator to {repo_full_name}')
        elif check_collaborator_response.status_code == 204:
            # User is already a collaborator
            logging.warning(f'{collaborator_username} is already a collaborator on {repo_full_name}')
        else:
            logging.error(f'Error checking collaborator status for {collaborator_username} on {repo_full_name}')


def get_repos(username, token=None, per_page=100):
    # https://docs.github.com/en/rest/reference/repos#releases
    repos, page_number, running = {"repos": []}, 1, True
    while running:
        if token is not None:
            r = requests.get(
                "https://api.github.com/user/repos?per_page=%d&page=%d" % (per_page, page_number),
                headers={"Accept": "application/vnd.github.v3+json", "Authorization": "token %s" % token}
            )
        else:
            print((username, per_page, page_number))
            logging.info(f' {username} : {per_page} : {page_number}')
            r = requests.get(
                "https://api.github.com/users/%s/repos?per_page=%d&page=%d" % (username, per_page, page_number),
                headers={"Accept": "application/vnd.github.v3+json"}
            )
        if type(r.json()) == dict:
            if "message" in r.json().keys():
                logging.info(r.json()['message'])
                running = False
        else:
            for repo in r.json():
                repos["repos"].append(repo)
            if len(r.json()) < per_page:
                running = False
            page_number += 1
    repo_count=len(repos['repos'])
    logging.info(f'Detected {repo_count} repositories for {username}')
    return repos


# Configure logging to write to a file
logging.basicConfig(filename='collaborator_addition.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
# Load the encryption key from an environment variable
encryption_key = os.getenv("ENCRYPTION_KEY")
# Decrypt the .env file
cipher_suite = Fernet(encryption_key.encode())
decrypted_env = cipher_suite.decrypt(open(".env.encrypted", "rb").read()).decode()
# Parse the decrypted_env string into a dictionary
env_dict = {}
for line in decrypted_env.splitlines():
    if '=' in line:
        key, value = line.split('=', 1)
        env_dict[key.strip()] = value.strip()

github_token =  env_dict.get("TKN_API_KEY")
github_token = github_token.replace('\'', '')
github_token = github_token.replace('=', '')
# Configure logging to write to a file

if __name__ == "__main__":
    # Replace these values with your own
    owner_username = '<<owner_username>>'
    collaborator_username_to_add = '<<collaborator_username>>'
    add_collaborator(owner_username, collaborator_username_to_add, github_token)
