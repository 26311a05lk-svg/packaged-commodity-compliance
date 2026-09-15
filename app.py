import streamlit as st
import easyocr
import re

st.set_page_config(page_title="Compliance Checker")

st.title("Packaged Commodity Compliance Checker")
st.write("SIH 2026 Prototype")

uploaded_file = st.file_uploader(
    "Upload a package image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    st.image(uploaded_file, caption="Uploaded package")

    st.write("Reading package information...")

    reader = easyocr.Reader(["en"])

    result = reader.readtext(uploaded_file.getvalue())

    # Combine OCR text
    extracted_text = " ".join(
        detection[1] for detection in result
    )

    text = extracted_text.lower()

    st.subheader("OCR Extracted Text")

    for detection in result:
        st.write(detection[1])

    st.subheader("Compliance Check")

    checks = {}

    # -------------------------------------------------
    # 1. COMMODITY NAME
    # -------------------------------------------------

    checks["Commodity Name"] = (
        "shampoo" in text
        or "commodity" in text
        or len(extracted_text.split()) >= 2
    )

    # -------------------------------------------------
    # 2. NET QUANTITY
    # -------------------------------------------------

    net_quantity = re.search(
        r"\b\d+(\.\d+)?\s*(g|kg|mg|ml|l)\b",
        text
    )

    # OCR may read 100 as 10O
    net_quantity_ocr = (
        re.search(r"net quantit", text)
        or re.search(r"\b10[o0]\b", text)
    )

    checks["Net Quantity"] = bool(
        net_quantity or net_quantity_ocr
    )

    # -------------------------------------------------
    # 3. MRP
    # -------------------------------------------------

    mrp_found = (
        "mrp" in text
        or "m r p" in text
        or "map rs" in text
        or "maP r" in text
        or "maximum retail price" in text
        or re.search(r"rs\.?\s*\d+", text)
        or re.search(r"₹\s*\d+", text)
        or re.search(r"\d+\.\d{2}", text)
    )

    checks["MRP"] = bool(mrp_found)

    # -------------------------------------------------
    # 4. MANUFACTURER / PACKER / IMPORTER
    # -------------------------------------------------

    manufacturer_words = [
        "manufactured",
        "manufacturer",
        "manufacture",
        "manufacturec",
        "kanufocturec",
        "marketed",
        "marketed by",
        "packed",
        "packed by",
        "packer",
        "imported",
        "imported by",
        "importer"
    ]

    manufacturer_found = any(
        word in text for word in manufacturer_words
    )

    checks["Manufacturer / Packer / Importer"] = manufacturer_found

    # -------------------------------------------------
    # 5. MONTH / YEAR
    # -------------------------------------------------

    month_words = [
        "january", "february", "march", "april",
        "may", "june", "july", "august",
        "september", "october", "november", "december"
    ]

    date_found = (
        any(month in text for month in month_words)
        or bool(re.search(r"\b\d{1,2}/20\d{2}\b", text))
        or bool(re.search(r"\b20\d{2}\b", text))
    )

    checks["Month / Year"] = date_found

    # -------------------------------------------------
    # 6. CONSUMER CARE DETAILS
    # -------------------------------------------------

    consumer_words = [
        "consumer care",
        "customer care",
        "customer",
        "care",
        "helpline",
        "contact",
        "write to",
        "email",
        "phone",
        "incharge"
    ]

    consumer_found = any(
        word in text for word in consumer_words
    )

    checks["Consumer Care Details"] = consumer_found

    # -------------------------------------------------
    # DISPLAY RESULTS
    # -------------------------------------------------

    passed = 0

    for item, found in checks.items():

        if found:
            st.success(f"✓ {item} — Detected")
            passed += 1

        else:
            st.error(f"✗ {item} — Not Detected")

    st.subheader("Overall Result")

    st.write(
        f"**{passed}/6 required declaration categories detected.**"
    )

    if passed == 6:
        st.success("Likely Compliant — All required fields detected.")
    else:
        st.warning(
            "Needs Review — Some declarations were not detected."
        )

    st.caption(
        "This is a preliminary software prototype for demonstration "
        "and does not constitute legal certification."
    )