import os
import sys
import subprocess
import requests
import json

def run_command(command, cwd=None):
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False, result.stderr
    return True, result.stdout

def create_github_repo(token, repo_name):
    print(f"Creating GitHub repository: {repo_name}")
    if "/" in repo_name:
        owner, name = repo_name.split("/", 1)
        url = f"https://api.github.com/orgs/{owner}/repos"
    else:
        owner = "user"
        name = repo_name
        url = "https://api.github.com/user/repos"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": name,
        "private": False,
        "auto_init": False
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        return True, response.json()["clone_url"]
    elif response.status_code == 422 and "name already exists" in response.text:
        print("Repository already exists. Obtaining existing URL...")
        if "/" in repo_name:
            repo_info_url = f"https://api.github.com/repos/{repo_name}"
        else:
            user_response = requests.get("https://api.github.com/user", headers=headers)
            user_login = user_response.json()["login"]
            repo_info_url = f"https://api.github.com/repos/{user_login}/{repo_name}"
            
        repo_response = requests.get(repo_info_url, headers=headers)
        if repo_response.status_code == 200:
            return True, repo_response.json()["clone_url"]
        else:
            return False, f"Repo exists but couldn't get info: {repo_response.text}"
    else:
        return False, response.text

def enable_github_pages(token, repo_full_name):
    print(f"Enabling GitHub Pages for: {repo_full_name}")
    url = f"https://api.github.com/repos/{repo_full_name}/pages"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    check_response = requests.get(url, headers=headers)
    if check_response.status_code == 200:
        print("GitHub Pages is already enabled.")
        return True, check_response.json()["html_url"]

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return True, response.json()["html_url"]
    else:
        data["source"]["branch"] = "master"
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return True, response.json()["html_url"]
        return False, response.text

def push_to_github(directory, repo_url, token, repo_full_name):
    print(f"Pushing files from {directory} to {repo_url}")
    run_command(["git", "init"], cwd=directory)
    run_command(["git", "add", "."], cwd=directory)
    run_command(["git", "commit", "-m", "Initial static site export"], cwd=directory)
    
    auth_url = repo_url.replace("https://", f"https://{token}@")
    run_command(["git", "remote", "add", "origin", auth_url], cwd=directory)
    
    success, output = run_command(["git", "push", "-f", "-u", "origin", "main"], cwd=directory)
    if not success and "error: src refspec main does not match" in output:
        success, output = run_command(["git", "push", "-f", "-u", "origin", "master"], cwd=directory)
    
    if success:
        print("Successfully pushed code. Now enabling GitHub Pages...")
        pages_success, pages_url = enable_github_pages(token, repo_full_name)
        if pages_success:
            print(f"GitHub Pages enabled! Live at: {pages_url}")
        else:
            print(f"Failed to enable GitHub Pages automatically: {pages_url}")
    return success, output

def get_token_from_git_credentials():
    creds_path = os.path.expanduser("~/.git-credentials")
    if os.path.exists(creds_path):
        with open(creds_path, "r") as f:
            for line in f:
                if "github.com" in line:
                    try:
                        token = line.split(":", 2)[2].split("@")[0]
                        if token: return token
                    except IndexError: continue
    return None

def get_token():
    token = os.environ.get("GITHUB_TOKEN")
    if token: return token
    return get_token_from_git_credentials()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python github_push.py <directory> <repo_name> [token]")
        sys.exit(1)

    directory = sys.argv[1]
    repo_name = sys.argv[2]
    token = sys.argv[3] if len(sys.argv) > 3 else get_token()

    if not token:
        print("Error: No GitHub token provided.")
        sys.exit(1)

    success, repo_url = create_github_repo(token, repo_name)
    if not success:
        print(f"Failed to create repo: {repo_url}")
        sys.exit(1)

    success, output = push_to_github(directory, repo_url, token, repo_name)
    if success:
        print("Successfully pushed to GitHub!")
    else:
        print(f"Failed to push: {output}")
        sys.exit(1)
