import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import os
from deep_translator import GoogleTranslator

# Tesseract should be installed and in PATH

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        images = convert_from_path(file_path)
        return "\n".join([pytesseract.image_to_string(img) for img in images])
    else:
        return pytesseract.image_to_string(Image.open(file_path))

def translate_text(text, to_lang="en"):
    return GoogleTranslator(source="auto", target=to_lang).translate(text)

def extract_birth_details_from_file(file_path):
    raw_text = extract_text(file_path)
    translated = translate_text(raw_text)

    prompt = ChatPromptTemplate.from_template("""
    Extract the following from this horoscope text and return as JSON:
    - Full Name
    - Date of Birth (DOB)
    - Time of Birth (TOB)
    - Place of Birth (City or Town)
    If missing, return null.

    Text: {text}
    """)
    chain = LLMChain(
        llm=ChatOpenAI(model_name="gpt-4o", temperature=0),
        prompt=prompt
    )
    return chain.run(text=translated)