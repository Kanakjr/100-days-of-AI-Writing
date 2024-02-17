import csv
import subprocess
from datetime import datetime
from article import generate_article
from utils import get_llm, check_if_md_file_exists, update_readme_from_csv
from dotenv import load_dotenv
from main_medium import main_medium
import time
from utils import update_csv, git_add_and_push

load_dotenv('./.env')

def main(csv_filename="topics.csv"):    
    with open(csv_filename, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        topics = list(reader)

    # Select a topic that does not have a link
    selected_topic = None
    for topic in topics:
        if not topic.get("Link"):
            selected_topic = topic
            break

    md_filename = check_if_md_file_exists(selected_topic["Name"])
    if md_filename:
        print(f"Article for '{selected_topic['Name']}' already exists.")
    else:
        # Generate the article
        print(f"Processing: {selected_topic['Name']}")
        md_filename = generate_article(
            selected_topic["Name"], selected_topic["Description"], llm=get_llm()
        )

    # Update the CSV with the .md file location
    update_csv(csv_filename, int(selected_topic["Sr.No"]), md_filename)

    # Update readme Table
    update_readme_from_csv('README.md', csv_file=csv_filename)

    # Git add and push
    git_add_and_push(selected_topic["Name"])


if __name__ == "__main__":
    main()
    print("Sleeping for 15 seconds before posting to Medium")
    time.sleep(15)
    main_medium()
