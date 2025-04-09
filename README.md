
# 📊 AI-Powered CSV Analyzer

This app lets you upload a CSV file and ask a question in natural language. It will:

- 🧠 Use Azure OpenAI (GPT-4) to understand your question
- 🗃️ Convert the CSV to a SQLite database
- 🧾 Generate a SQL query
- 📈 Create a matplotlib plot
- ✉️ Send the results by email
- 🌐 Show the results in a simple web UI (Streamlit)

---

## 🧰 Built With

- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [Semantic Kernel (Microsoft)](https://github.com/microsoft/semantic-kernel)
- Azure OpenAI (GPT-4)
- Azure Communication Services (Email)
- SQLite (for temp data storage)
- Matplotlib (for charts)

---

## 🚀 How to Run the App (Local Setup)

Follow these steps from start to finish:

---

### ✅ Step 1: Clone the Repo

```bash
git clone https://github.com/your-username/ai-csv-analyzer.git
cd ai-csv-analyzer
```

---

### ✅ Step 2: Create and Activate a Virtual Environment (optional)

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

---

### ✅ Step 3: Install Dependencies

Create a file called `requirements.txt` with the following content:

```txt
streamlit
pandas
matplotlib
openai
semantic-kernel==0.3.15.dev0
azure-communication-email
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

---

### ✅ Step 4: Create Azure API Keys File

Create a file called `keys.py` in the root folder of the project with the following content:

```python
keys = {
    "service_id": "your_service_id",
    "deployment_name": "your_gpt_deployment_name",
    "endpoint": "https://your-resource-name.openai.azure.com/",
    "api_key": "your_azure_openai_api_key"
}
```

> 🔒 **Important**: Replace the placeholder values with your actual Azure OpenAI credentials.

---

### ✅ Step 5: Configure Email Settings

Open the file `agentic_sk.py` and locate the `send_email()` function.

Update the following:

```python
"senderAddress": "DoNotReply@xxxxxxx.azurecomm.net",  # Your verified Azure sender address
"recipients": {
    "to": [{"address": "you@example.com", "displayName": "Your Name"}]
}
```

You can add more recipients or CC/BCC if needed.

---

### ✅ Step 6: Run the App

Start the Streamlit app with:

```bash
streamlit run app.py
```

Then open your browser and go to: [http://localhost:8501](http://localhost:8501)

---

### ✅ Step 7: Use the App

1. Upload a `.csv` file (e.g., `cars.csv`)
2. Type a natural language question (e.g. _"Show me average prices by brand"_)
3. Click **Run Analysis**

The app will:

- Convert CSV to an in-memory SQLite DB
- Use GPT-4 to generate SQL + Python chart code + a professional summary
- Generate a matplotlib chart
- Send an email with the chart and summary
- Display everything in the web interface

---

## 📬 Example Output

Here’s what you’ll get:

- 📊 A visualization shown on the page
- 🧠 A GPT-generated SQL query
- 💡 A human-like summary of insights
- ✉️ An email with all the results attached

---

## 🛡️ Notes

- Make sure your Azure OpenAI and Communication Services resources are properly configured and enabled.
- This app is for educational/demo use. Secure your keys and sensitive info before production use.

---

## 💡 Future Improvements

- Add support for Excel files
- Enable multiple file uploads
- Improve chart customization
- Add error handling and retry mechanisms
- Add accessibility and responsive design

---

