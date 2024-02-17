import csv
import subprocess
from datetime import datetime
from article import generate_article
from utils import get_llm, check_if_md_file_exists
from dotenv import load_dotenv
import os
from medium import post_to_medium
from utils import update_readme_from_csv

load_dotenv('./.env')

def update_csv(csv_filename, row_index, md_filename, medium_url=''):
    # Update the CSV file with the .md file location in the "Link" column
    with open(csv_filename, "r") as csv_file:
        data = list(csv.reader(csv_file))

    data[row_index][data[0].index("Link")] = md_filename
    data[row_index][data[0].index("Medium")] = medium_url

    with open(csv_filename, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data)


def git_add_and_push(topic):
    # Git add and push
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Added {topic} article"])
    subprocess.run(["git", "push"])

def main():    
    with open(csv_filename, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        topics = list(reader)

    # Select a topic that does not have a link
    selected_topic = None
    for topic in topics:
        if not topic.get("Medium"):
            selected_topic = topic
            break

    md_filename = selected_topic["Link"]
    print(f"md_filename: {md_filename}")
    
    # Post to Medium and get the URL
    try:
        medium_url = post_to_medium(name=selected_topic["Name"], 
                   description=selected_topic["Description"], 
                   tags=selected_topic["Tags"], 
                   md_file_name=md_filename)
    except Exception as e:
        print(f"Failed to post to Medium. Error: {e}")
        medium_url = ''

    # Update the CSV with the .md file location
    update_csv(csv_filename, int(selected_topic["Sr.No"]), md_filename, medium_url=medium_url)

    # Update readme Table
    update_readme_from_csv('README.md', csv_file=csv_filename)

    # Git add and push
    #git_add_and_push(selected_topic["Name"])


if __name__ == "__main__":
    csv_filename = "topics.csv"
    main()
    # update_readme_from_csv('README.md', csv_file=csv_filename)
