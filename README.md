🛠️ Technology Stack
Backend: Python
AI Model: Anthropic Claude 3.5 Sonnet
Web Framework: Streamlit
Data Handling: Pandas
PDF Processing: pdf2image + Poppler
Image Processing: Pillow, OpenCV



# Gen Menu: AI-Powered Menu Data Extractor

An interactive web application that automates the tedious process of digitizing restaurant menus. This tool allows a user to upload a menu as a multi-page PDF or an image, and leverages the power of **Anthropic's Claude 3.5 Sonnet** to intelligently extract all items, categories, descriptions, and prices into a structured format.

The final output is a ready-to-use Excel file, perfectly formatted for bulk upload into e-commerce systems like Hyperzod, transforming hours of manual data entry into a task of minutes.

---

## ✨ Features

- **Multi-Format Support:** Accepts multi-page PDFs, PNGs, and JPGs.
- **State-of-the-Art AI:** Powered by Claude 3.5 Sonnet for high-accuracy vision and data extraction.
- **Structured Data Output:** Parses complex menu layouts, including items with multiple sizes and prices.
- **Automated Excel Formatting:** Generates a downloadable `.xlsx` file that is directly compatible with a target business system (e.g., Hyperzod).
- **Interactive Web Interface:** Built with Streamlit for a simple, user-friendly experience.
- **Robust PDF Processing:** Uses the `pdf2image` library with the Poppler engine to reliably handle PDF files.

---

## 🚀 How to Run This Project Locally

This project is built as a Streamlit application and can be run on your local machine.

### 1. Prerequisites

- Python 3.9+
- The `poppler` utility must be installed on your system. For Windows, this requires downloading the binaries and adding the `bin` folder to your system's PATH.
- An API key from Anthropic (Claude).

### 2. Clone the Repository

Clone this repository to your local machine:
```bash
git clone https://github.com/your-username/AI-Menu-Extractor-Streamlit.git
cd AI-Menu-Extractor-Streamlit
