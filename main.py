import csv
import subprocess
from datetime import datetime
from article import generate_article
from utils import get_llm
from dotenv import load_dotenv
import os

load_dotenv('./.env')

def update_csv(csv_filename, row_index, md_filename):
    # Update the CSV file with the .md file location in the "Link" column
    with open(csv_filename, "r") as csv_file:
        data = list(csv.reader(csv_file))

    data[row_index][data[0].index("Link")] = md_filename

    with open(csv_filename, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data)


def git_add_and_push(topic):
    # Git add and push
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Added {topic} article"])
    subprocess.run(["git", "push"])

def update_readme_from_csv(readme_file, csv_file):
    # Read data from CSV
    with open(csv_file, 'r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows_with_links = [row for row in csv_reader if row.get('Link')]

    # Generate table markdown
    GIT_ARTICLE_BASEURL = os.environ.get("GIT_ARTICLE_BASEURL")
    table_markdown = "| Sr.No | Category | Name | Description | Tags | Link |\n"
    table_markdown += "|-------|----------|------|-------------|------|------|\n"
    for row in rows_with_links:
        table_markdown += f"| {row['Sr.No']} | {row['Category']} | {row['Name']} | {row['Description']} | {row['Tags']} | [{row['Link']}]({GIT_ARTICLE_BASEURL}{row['Link']}) |\n"

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


def main():
    # Read the CSV file
    csv_filename = "topics.csv"
    with open(csv_filename, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        topics = list(reader)

    # Select a topic that does not have a link
    selected_topic = None
    for topic in topics:
        if not topic.get("Link"):
            selected_topic = topic
            break

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
