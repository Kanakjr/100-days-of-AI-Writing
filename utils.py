from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.utilities.dalle_image_generator import DallEAPIWrapper
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import os
import json
import requests
import csv

from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache

set_llm_cache(SQLiteCache(database_path=".langchain.db"))


class CustomDallEAPIWrapper(DallEAPIWrapper):
    """Custom subclass of DallEAPIWrapper with additional parameters."""

    quality: str = "standard"
    """Quality of the generated image"""

    model: str = "dall-e-3"
    """Model to use for image generation"""

    def _dalle_image_url(self, prompt: str) -> str:
        params = {
            "prompt": prompt,
            "n": self.n,
            "size": self.size,
            "quality": self.quality,
            "model": self.model,
        }
        response = self.client.create(**params)
        return response["data"][0]["url"]


def get_llm(OPENAI_MODEL=None, max_tokens=1000):
    if not OPENAI_MODEL:
        OPENAI_MODEL = os.environ.get("OPENAI_MODEL")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    llm = ChatOpenAI(
        temperature=0,
        model_name=OPENAI_MODEL,
        openai_api_key=OPENAI_API_KEY,
        max_tokens=max_tokens,
    )
    return llm


def get_openAPI_response(text, task, OPENAI_MODEL=None, max_tokens=1000, llm=None):
    messages = [HumanMessage(content=text)]
    llm = get_llm(OPENAI_MODEL=OPENAI_MODEL, max_tokens=max_tokens)
    response = llm.invoke(messages, config={"run_name": task})
    response = str(response.content)
    return response


def save_to_md_file(topic_name, text):
    # Replace blank spaces with "-"
    filename = topic_name.replace(" ", "-") + ".md"
    # Create the "articles" folder if it doesn't exist
    folder_path = "articles"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Create and write to the Markdown file
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "w") as file:
        file.write(f"{text}")
    print(f"File '{filename}' saved successfully in the 'articles' folder.")
    return filename

def check_if_md_file_exists(topic_name):
    # Replace blank spaces with "-"
    filename = topic_name.replace(" ", "-") + ".md"
    # Create the "articles" folder if it doesn't exist
    folder_path = "articles"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Create and write to the Markdown file
    file_path = os.path.join(folder_path, filename)
    if os.path.exists(file_path):
        return filename
    else:
        None


def download_and_save_image(url, topic_name):
    # Create the "images" folder if it doesn't exist
    folder_path = "images"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Get the filename from the URL
    filename = topic_name.replace(" ", "-") + ".png"
    # Download the image
    response = requests.get(url)
    if response.status_code == 200:
        # Save the image to the "images" folder
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "wb") as file:
            file.write(response.content)

        print(f"Image downloaded and saved successfully in the 'images' folder.")
        git_file_url = os.environ.get("GIT_IMG_BASEURL") + filename
        return git_file_url

    else:
        print(f"Failed to download the image. Status code: {response.status_code}")
        return None

def update_readme_from_csv(readme_file, csv_file):
    # Read data from CSV
    with open(csv_file, 'r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows_with_links = [row for row in csv_reader if row.get('Link')]

    # Generate table markdown
    GIT_ARTICLE_BASEURL = os.environ.get("GIT_ARTICLE_BASEURL")
    table_markdown = "| Sr.No | Category | Name | Description | Medium | Link |\n"
    table_markdown += "|-------|----------|------|-------------|------|------|\n"
    for row in rows_with_links:
        table_markdown += f"| {row['Sr.No']} | {row['Category']} | {row['Name']} | {row['Description']} | {row['Medium']} | [{row['Link']}]({GIT_ARTICLE_BASEURL}{row['Link']}) |\n"

    # Read existing README content
    with open(readme_file, 'r', encoding='utf-8') as readme:
        readme_content = readme.read()

    # Find the position of the existing table (if it exists)
    table_start = readme_content.find("<!-- TABLE START -->")
    table_end = readme_content.find("<!-- TABLE END -->")

    # Update README content with the new table
    if table_start != -1 and table_end != -1:
        updated_readme_content = (
            readme_content[:table_start] +
            "<!-- TABLE START -->\n\n" +
            table_markdown +
            "<!-- TABLE END -->\n\n" +
            readme_content[table_end + len("<!-- TABLE END -->"):]
        )
    else:
        # If the table doesn't exist, simply append it to the end of the README
        updated_readme_content = readme_content + "\n\n<!-- TABLE START -->\n\n" + table_markdown + "<!-- TABLE END -->\n"

    # Write the updated content back to README
    with open(readme_file, 'w', encoding='utf-8') as readme:
        readme.write(updated_readme_content)