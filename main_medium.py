import csv
from dotenv import load_dotenv
from medium import post_to_medium
from utils import update_readme_from_csv
from utils import update_csv, git_add_and_push

load_dotenv('./.env')

def main_medium():    
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
    print(f"selected md_filename: {md_filename}")
    
    # Post to Medium and get the URL
    try:
        print(f"Posting to Medium: {selected_topic['Name']}")
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
    git_add_and_push(selected_topic["Name"])


if __name__ == "__main__":
    csv_filename = "topics.csv"
    main_medium()