import base64
from os import environ
import requests
import webbrowser

# Authentication headers for GitHub API
HEADERS = {
    'Accept': 'application/json',
    'User-Agent': "Teb's Lab Github Exercise bot",
    'Authorization': f'Bearer {environ["GITHUB_ACCESS_TOKEN"]}'
}

def main():
    # Step 1: Authenticate and get user
    response = requests.get('https://api.github.com/user', headers=HEADERS)
    user_name = response.json()['login']

    # Step 2: Get repo name input
    repo_name = input("Type the name of the repo. No spaces allowed.\n")
    repo_description = 'I made this repo using a Python script. That script is even in this repo!! Neat.'

    # Step 3: Create the repo
    create_repo_response = create_repo(repo_name, repo_description)
    print("create_repo_response status code:", create_repo_response.status_code)
    print("create_repo_response JSON:", create_repo_response.json())

    if create_repo_response.status_code != 201:
        print("❌ Failed to create repo. Exiting.")
        return

    # Step 4: Add README file
    f1_response = add_file_to_repo(user_name, repo_name, 'readme.md', '# Auto Generated\n\n Isn\'t this sweet?')

    # Step 5: Read this script's code
    with open(__file__, 'r') as this_file:
        this_file_as_str = this_file.read()

    # Step 6: Add this script to the repo
    f2_response = add_file_to_repo(user_name, repo_name, 'repo_creator.py', this_file_as_str)
    print("f2_response status code:", f2_response.status_code)
    print("f2_response JSON response:", f2_response.json())

    if f2_response.status_code != 201:
        print("❌ Failed to add repo_creator.py")
        return

    # Step 7: Create branch, issue, modify file, and open PR
    hash_for_new_branch = f2_response.json()['commit']['sha']
    create_issue_response = create_issue(user_name, repo_name, "This repo is actually whack.", "It's my view that you should fix it.")

    new_branch_name = 'a_branch'
    create_branch_response = create_branch(user_name, repo_name, hash_for_new_branch, new_branch_name)

    f1_contents = f1_response.json()
    modify_file_response = modify_existing_file(
        user_name, 
        repo_name, 
        f1_contents['content']['path'], 
        f1_contents['content']['sha'], 
        '# Auto Generated\n\n Isn\'t this sweet?\n\n It\'s way sweet.', 
        new_branch_name
    )

    open_pr_response = open_merge_pr(
        user_name, 
        repo_name, 
        new_branch_name,
        'main',
        'We need to merge!',
        'This new branch is way better, you need to merge it.'
    )

    webbrowser.open(create_repo_response.json()['html_url'], new=0, autoraise=True)

# Helper: Create a GitHub repo
def create_repo(repo_name, repo_description):
    response = requests.post(
        'https://api.github.com/user/repos',
        headers=HEADERS,
        json={
            'name': repo_name,
            'description': repo_description
        })
    return response

# Helper: Add a file to the repo
def add_file_to_repo(owner_name, repo_name, file_name, file_contents):
    file_contents_encoded = base64.b64encode(file_contents.encode('utf-8'))
    encoded_file_as_str = file_contents_encoded.decode('utf-8')
    response = requests.put(
        f'https://api.github.com/repos/{owner_name}/{repo_name}/contents/{file_name}',
        headers=HEADERS,
        json={
            'message': f'Created {file_name}.',
            'content': encoded_file_as_str
        })
    return response

# Helper: Create an issue
def create_issue(owner_name, repo_name, issue_name, issue_description):
    response = requests.post(
        f'https://api.github.com/repos/{owner_name}/{repo_name}/issues',
        headers=HEADERS,
        json={
            'title': issue_name,
            'body': issue_description
        })
    return response

# Helper: Create a branch
def create_branch(owner_name, repo_name, source_branch_hash, new_branch_name):
    response = requests.post(
        f'https://api.github.com/repos/{owner_name}/{repo_name}/git/refs',
        headers=HEADERS,
        json={
            'ref': f'refs/heads/{new_branch_name}',
            'sha': source_branch_hash
        })
    return response

# Helper: Modify an existing file
def modify_existing_file(owner_name, repo_name, file_path, file_sha, new_file_content, branch_name):
    file_contents_encoded = base64.b64encode(new_file_content.encode('utf-8'))
    encoded_file_as_str = file_contents_encoded.decode('utf-8')
    response = requests.put(
        f'https://api.github.com/repos/{owner_name}/{repo_name}/contents/{file_path}',
        headers=HEADERS,
        json={
            'message': f'Modified {file_path}.',
            'content': encoded_file_as_str,
            'branch': branch_name,
            'sha': file_sha
        })
    return response

# Helper: Open a pull request
def open_merge_pr(owner_name, repo_name, branch_to_merge, merge_into_branch, title, description):
    response = requests.post(
        f'https://api.github.com/repos/{owner_name}/{repo_name}/pulls',
        headers=HEADERS,
        json={
            'title': title,
            'head': branch_to_merge,
            'base': merge_into_branch,
            'body': description
        })
    return response

# Run main
if __name__ == '__main__':
    main()
