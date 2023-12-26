from langchain.utilities.dalle_image_generator import DallEAPIWrapper
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


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


# text_type = ['News Title','News Description','News Summary','Social Post']
def generate_image_from_text(
    llm, text, text_type, image_type="image", image_style=None, custom_rules=""
):
    # Define the prompt template and input variables
    if image_style:
        custom_rules += f"Generate image in a {image_style} Style."
    prompt = PromptTemplate(
        input_variables=["text", "text_type", "image_type", "custom_rules"],
        template="""Write a DALL.E prompt to generate an {image_type}" based on the following {text_type}. 
# {text_type}: {text}
# Rules: Only output the prompt in less than 100 words.
{custom_rules}
# Prompt:""",
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    image_prompt = chain.invoke(
        input={
            "text": text,
            "text_type": text_type,
            "image_type": image_type,
            "custom_rules": custom_rules,
        },
        config={"run_name": "Dalle Prompt"},
    )
    image_prompt = image_prompt["text"]
    image_url = CustomDallEAPIWrapper().run(image_prompt)
    return image_url, image_prompt
