import streamlit as st
from io import StringIO
import pandas as pd
import openai
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import requests
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch

# Initialize your OpenAI API key
openai.api_key = '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'

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")

# Streamlit interface setup
st.title('Document Analyzer')

# Upload file
uploaded_file = st.file_uploader("Choose a file (PDF, text, etc.)")
extracted_text = ""  # Initialize extracted text variable

def extract_text_with_trocr(image):
    # Process the image
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    # Generate text with TrOCR
    generated_ids = model.generate(pixel_values)
    # Decode the generated text
    text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(text)
    return text

# Function to extract text from PDF, including OCR fallback
def extract_text_from_pdf_with_trocr(pdf_file):
    doc = fitz.open(stream=pdf_file.read())
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        # Use TrOCR for OCR
        page_text = extract_text_with_trocr(img)
        text += page_text
        print(text)
    return text

# Process uploaded PDF file
if uploaded_file is not None and uploaded_file.type == "application/pdf":
    extracted_text = extract_text_from_pdf_with_trocr(uploaded_file)

# Text input area
text_input = st.text_area("Or paste your text here:")

# Function to analyze text with OpenAI
def analyze_text_with_openai(text):
    response = openai.chat.completions.create(
        messages=[
            {"role": "system", 
                "content": "Du bist ab sofort ein Kundeserviceprofi und arbeitest in einem Einkausunternehmen welches sich hauptsächlich um Tailspend kümmert. Groß und kleinschreibung sind für dich fremde Konzepte. Extrahiere mir folgende Daten und strukturiere sie mir bitte in einer Tabelle bei der Spalte 1 die Attribute enthält und jede weitere Spalte eine Position: Positionsnummer, Lieferantenname, pro Einzelpreispreis eine Position, Menge und Mengeneinheit die der Lieferant angegeben hat, Artikelnummer, Artikelkurzbeschreibung, ca. Preis, Rabatte, Bruttopreis, Nettopreis, Versandanschrift, Versandkosten, Lieferdatum, Zahlungsbedingungen und Incoterms. Wenn du diese Daten nicht findest lasse sie bitte leer und markiere sie mit ---: . Strukturiere die Daten in einer vertikalen Tabelle. Wenn du mehrere Positionen hast schreibe sie bitte in eine einzige Tabelle."},
                {"role": "user", "content": text}
    ],
    model="gpt-4-0125-preview",
    )
    return response

# If there's text input or extracted text, process it
if text_input or extracted_text:
    result_text = analyze_text_with_openai(text_input or extracted_text)
    st.text_area("Extracted Information:", value=result_text, height=300)


# Assuming `extracted_text` or `text_input` contains the text to be structured
text_to_structure = text_input if text_input else extracted_text

# Initialize an empty dictionary to hold the structured data
structured_data = {}

# Split the text by lines to process each line individually
lines = text_to_structure.split('\n')

# Iterate over each line and parse key information
for line in lines:
    if line.startswith('- '):  # Assuming key information lines start with '- '
        # Further processing to split keys and values
        key_value_pair = line[2:].split(': ')
        if len(key_value_pair) == 2:  # Ensure there's a key and a value
            key, value = key_value_pair
            structured_data[key.strip()] = value.strip()

# Use `structured_data` as needed in your application
# For example, displaying the structured data:
st.write(structured_data)