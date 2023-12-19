from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from typing import Dict
from pydantic import BaseModel,Field
from dalle import generate_image_from_text
from utils import save_to_md_file, download_and_save_image


class ResponseOutput(BaseModel):
    text: str = Field(description="markdown article text")
    links: Dict[str, str] = Field(description='{"link1":<dalle3 prompt to generate the image>,...}')

response_output_parser = PydanticOutputParser(pydantic_object=ResponseOutput)

def get_generate_article_prompt_template():    
    prompt = PromptTemplate(
        template = """As an expert in the given technical subject, your task is to write a comprehensive and easy-to-understand article in markdown format. The article should be based on the provided Topic Name and Topic Description.

### Instructions:
1. Use clear, jargon-free language to make the content accessible to a broad audience.
2. Break up your content into shorter paragraphs to make it more digestible.
3. Illustrate your key points with examples and real-world applications.
4. Incorporate 1 images that is relevant to the article after the title using the markdown format ![alt text](link1). Add the dalle3 prompt to generate the image in the output links.
5. The output should be a JSON as follows: {{"text":markdown article text, "links": {{"link1":<dalle3 prompt to generate the image>}} }}

### Desired Outcome:
A well-structured, comprehensive, and easy-to-understand technical article in markdown format that effectively communicates the given Topic Name and Topic Description. The article should be enriched with relevant examples, real-world applications, and images. 

Topic Name: {topic_name}
Topic Description: {topic_description}

{format_instructions}

Output:
""",
        input_variables=["topic_name","topic_description"],
        partial_variables={"format_instructions": response_output_parser.get_format_instructions()},
    )
    return prompt

def generate_article(topic_name,topic_description,llm):
    x = {"topic_name":topic_name,
        "topic_description":topic_description,}

    generate_article_prompt_template = get_generate_article_prompt_template()
    question_context_chain = generate_article_prompt_template | llm | response_output_parser
    response = question_context_chain.invoke(x)
    response = ResponseOutput.parse_obj(response)
    
    text = response.text
    links = response.links

    if links:
        for link,description in links.items():
            imageurl, _ = generate_image_from_text(llm=llm,text=description,text_type='description',image_type='image')
            local_imageurl = download_and_save_image(url=imageurl,topic_name=topic_name)
            text = text.replace(f'({link})',f'({local_imageurl})')

    filename = save_to_md_file(topic_name=topic_name,text=text)
    return filename


if __name__ == "__main__":
    from utils import get_llm
    llm = get_llm()

    topic_name = 'AI in Healthcare: Predictive Analytics'
    topic_description = 'How AI is revolutionizing healthcare by predicting diseases and patient outcomes.'

    generate_article(topic_name,topic_description,llm=llm)