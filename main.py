import streamlit as st
import json
import base64
from dotenv import load_dotenv
from langchain_together import ChatTogether
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from schema import BarcodeRead
from db import insert_record, fetch_all_records

load_dotenv()

# Convert image bytes to base64
def encode_image_bytes(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")

# Extract serial number using LangChain + Together
def read_serial(image_bytes: bytes, model="Qwen/Qwen2.5-VL-72B-Instruct"):
    llm = ChatTogether(model=model, temperature=0)

    parser = JsonOutputParser(pydantic_object=BarcodeRead)

    system_prompt = (
        "You are a barcode/QR decoder assistant.\n"
        "Return ONLY valid JSON. Pick largest/clearest code. "
        "If unreadable, serial_number=null and notes explain why. "
        "Include symbology and confidence."
        
    )

    img_b64 = encode_image_bytes(image_bytes)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=[
            {"type": "text", "text": "Extract the serial number from this barcode image."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
        ])
    ]

    resp = llm.invoke(messages)   #image+text
    result = parser.parse(resp.content)
    return result

# ---------------- Streamlit App ----------------
st.set_page_config(page_title="Barcode Scanner Demo", layout="centered")
st.title("🔍 Barcode/QR Code Scanner Demo")

uploaded_file = st.file_uploader("Upload a barcode/QR image", type=["jpg", "jpeg", "png","gif","webp"])

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    with st.spinner("Reading barcode..."):
        result = read_serial(image_bytes)

    st.success("✅ Extraction Complete!")
    st.json(result)

    # Save to Postgres
    record_id = insert_record(result)
    if record_id:
        st.info(f"Record saved to database with ID: {record_id}")
    else:
        st.warning("Record could not be saved!")

# Display all records
st.subheader("📄 Saved Barcode Records")
records = fetch_all_records()
if records:
    import pandas as pd
    df = pd.DataFrame(records, columns=["ID", "Serial Number", "Symbology", "Confidence", "Notes", "Timestamp"])
    st.dataframe(df)
else:
    st.write("No records found yet.")












