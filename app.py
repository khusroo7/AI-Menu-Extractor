# claude-streamlit-test/app.py

import os
import base64
import streamlit as st
import anthropic
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List, Union
from pdf2image import convert_from_bytes
import io

# --- Pydantic Models (Unchanged) ---
class PriceObject(BaseModel):
    size: Optional[str] = None
    price: float

class MenuItem(BaseModel):
    name: str = Field(..., description="The exact name of the menu item.")
    description: Optional[str] = Field(None, description="The description of the item, if one exists.")
    price: Union[float, List[PriceObject]] = Field(..., description="The price of the item.")
    category: str = Field(..., description="The name of the category this item belongs to.")
    dietary_tags: List[str] = Field(default_factory=list, description="A list of dietary tags like 'V', 'GF'.")

class Category(BaseModel):
    category_name: str = Field(..., description="The name of a menu category.")
    items: List[MenuItem]

class Menu(BaseModel):
    """The root model for the entire structured menu."""
    categories: List[Category]

# --- Main Functions ---
# --- THIS IS THE FIX (Part 1) ---
# The function now accepts the media_type so it can be dynamic.
def process_image_with_claude(image_bytes, client, media_type):
    """Takes raw image bytes and sends them to Claude for extraction with the correct media type."""
    
    base64_image_data = base64.b64encode(image_bytes).decode("utf-8")

    tool_definition = {
        "name": "extract_menu_data",
        "description": "Extracts structured data from a menu image.",
        "input_schema": Menu.model_json_schema()
    }
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        system="You are an expert menu data extraction AI. Analyze the image and use the provided 'extract_menu_data' tool to return the structured data.",
        tool_choice={"type": "tool", "name": "extract_menu_data"},
        tools=[tool_definition],
        messages=[
            {
                "role": "user",
                "content": [
                    # The media_type is now correctly passed in.
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": base64_image_data}},
                    {"type": "text", "text": "Please extract all menu items from this image."}
                ]
            }
        ]
    )

    tool_use = next((block for block in response.content if block.type == "tool_use"), None)
    
    if tool_use:
        try:
            return Menu.model_validate(tool_use.input)
        except ValidationError as e:
            st.warning(f"Pydantic validation failed for this page. The AI's output may not be a valid menu. Skipping.")
            print(f"\n--- Pydantic Validation Error ---\nRaw AI Output: {tool_use.input}\nError: {e}\n---")
            return None
            
    return None

# --- Streamlit UI ---
load_dotenv(find_dotenv())
api_key = os.environ.get("ANTHROPIC_API_KEY")

st.set_page_config(page_title="Claude Menu Extractor", layout="centered")
st.title("Menu Extractor powered by Claude 3.5 Sonnet")

if not api_key:
    st.error("ANTHROPIC_API_KEY not found. Please create a `.env` file and add your key.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

uploaded_file = st.file_uploader("Upload a Menu (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    file_type = uploaded_file.type
    if "pdf" not in file_type:
        st.image(uploaded_file, caption="Uploaded Image Preview")
    else:
        st.info(f"PDF file selected: {uploaded_file.name}")

    if st.button("Extract Menu Data"):
        file_bytes = uploaded_file.read()
        
        with st.spinner("Claude is analyzing your menu..."):
            try:
                final_menu_items = []
                
                if "pdf" in file_type:
                    st.info("Detected PDF. Converting pages to images...")
                    poppler_path = r"C:\Release-24.08.0-0\poppler-24.08.0\Library\bin"
                    images = convert_from_bytes(file_bytes, dpi=200, poppler_path=poppler_path, fmt="jpeg")
                    st.success(f"Converted PDF to {len(images)} pages.")

                    for i, image in enumerate(images):
                        page_num = i + 1
                        st.write(f"--- Processing Page {page_num} of {len(images)} ---")
                        
                        with io.BytesIO() as output:
                            image.save(output, format="JPEG")
                            img_bytes = output.getvalue()
                        
                        # We know these are JPEGs because we converted them.
                        page_result = process_image_with_claude(img_bytes, client, "image/jpeg")
                        if page_result and page_result.categories:
                            st.success(f"Successfully extracted {len(page_result.categories)} categories from page {page_num}.")
                            final_menu_items.extend(page_result.categories)
                else: 
                    # --- THIS IS THE FIX (Part 2) ---
                    # For direct image uploads, we now pass the *actual* file type.
                    st.info(f"Detected {file_type}. Processing...")
                    image_result = process_image_with_claude(file_bytes, client, file_type)
                    # --- END OF FIX ---
                    if image_result and image_result.categories:
                        final_menu_items.extend(image_result.categories)
                
                final_menu = Menu(categories=final_menu_items)

                st.success("Extraction Complete!")
                st.subheader("Final Structured JSON Output")
                st.json(final_menu.model_dump())

            except Exception as e:
                st.error(f"A fatal error occurred during processing: {e}")
                st.error("Please check your terminal for more detailed error information.")
