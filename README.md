# 📊 Auto EDA Notebook Generator

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?style=for-the-badge&logo=flask)
![Gemini API](https://img.shields.io/badge/Google%20Gemini-AI-orange?style=for-the-badge&logo=google)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter)

**Auto EDA Notebook Generator** is an AI-powered web application that automates the Exploratory Data Analysis (EDA) process for data scientists and analysts. By extracting only the "statistical metadata" from a user-uploaded CSV file, it generates a fully executable, visually stunning **Jupyter Notebook (.ipynb)** packed with advanced Plotly visualizations.

## ✨ Key Features (Why is it different?)

* 🔒 **100% Data Privacy:** The raw user data (rows, customer info, sensitive logs) is **never** sent to the AI API. The system only transmits a lightweight metadata profile (column names, data types, null counts) to the LLM.
* ⚡ **Micro Token Consumption:** Even when processing datasets with millions of rows, the LLM only receives a few lines of summary. This keeps prompt costs and token consumption at an absolute minimum, delivering results in seconds.
* 📓 **Instant Jupyter Notebook Output:** The Markdown response from the LLM is instantly parsed by the backend using the `nbformat` library and converted into a professional `.ipynb` file, beautifully structured with HTML headings, explanation cells, and executable code blocks.
* 🎨 **Advanced Visualizations:** Instead of basic bar charts, the system generates complex Plotly charts tailored to the data's context (Heatmaps, Sunbursts, Violin plots, Time Series) featuring a sleek dark theme (`plotly_dark`) and elegant HTML-formatted titles.

## ⚙️ System Architecture

1. **User Input:** A CSV file is uploaded via the web interface.
2. **Pandas Processing:** The Flask backend reads the CSV and extracts its metadata profile using Pandas (`df.describe()`, `df.isnull()`).
3. **LLM Prompting (Gemini):** A highly engineered prompt—loaded with strict design and data constraints—is sent to the Gemini 1.5 Flash model.
4. **Regex & Nbformat:** The raw Markdown output from the LLM is split into text and code blocks via Regex, converted into Jupyter Notebook cells using `nbformat`, and served as a direct download to the user.

## 🚀 Setup and Installation

Follow these steps to run the project in your local environment.

### 1. Clone the Repository
```bash
git clone https://github.com/goktani/auto-eda-notebook-gen.git
cd auto-eda-notebook-gen
```

### 2. Install Dependencies
```Bash
pip install flask pandas google-generativeai nbformat
```

### 3. Add Your API Key
Open the app.py file and paste your free Gemini API key (obtained from Google AI Studio) into the API_KEY variable:
```Python
API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```

### 4. Run the Application
```Bash
python app.py
```

Once the server starts, open your browser and navigate to http://127.0.0.1:5000/ to start generating notebooks!

## 🛠️ Roadmap
* [ ] Excel (.xlsx) format support.

* [ ] Dynamic input field for custom user prompts (e.g., "Focus only on the sales column").

* [ ] Asynchronous task queues (Celery/Redis) for handling massive datasets.

* [ ] Multi-language output support.

Built entirely with pure Python and a highly modular engineering approach.
