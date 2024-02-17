import requests
import os
from dotenv import load_dotenv

load_dotenv('./.env')

def post_to_medium(name, description, tags, md_file_name, access_token=os.environ.get('MEDIUM_ACCESS_TOKEN'), user_id=os.environ.get('MEDIUM_USER_ID')):
    """
    Create a public Medium post from a Markdown file.
    
    Parameters:
    - name: Title of the blog post
    - description: A brief description of the blog post
    - tags: Comma-separated tags for the blog post
    - md_file_name: Path to the Markdown file
    - access_token: Medium access token for authentication
    - user_id: Medium user ID for the blog post author
    """
    # Setup the headers with the provided access token
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Charset': 'utf-8'
    }

    # Read the Markdown file content
    with open(os.path.join('articles' , md_file_name), 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    # Prepare the data payload
    data = {
        'title': f'{name} - {description}',
        'contentFormat': 'markdown',
        'content': markdown_content,
        'tags': tags.split(', '),  # Split the tags string into a list
        'publishStatus': 'public',  # Make the post public
    }

    # Make a POST request to create the new post
    response = requests.post(f'https://api.medium.com/v1/users/{user_id}/posts', headers=headers, json=data)

    # Check response status and return URL or error message
    if response.status_code == 201:
        post_info = response.json()
        return post_info['data']['url']
    else:
        return "Failed to create post. Error: " + response.text

if __name__ == "__main__":
    # Call the function with example parameters
    url = post_to_medium(
        name="Blockchain for Voting Systems",
        description="Exploring the potential of blockchain technology to create secure and transparent voting systems.",
        tags="Blockchain, Voting, Security, Transparency",
        md_file_name="Blockchain-for-Voting-Systems.md",
    )
    print(f"Post created successfully! \nURL: {url}")