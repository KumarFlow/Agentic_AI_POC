import streamlit as st
from agentic_sk import run_pipeline 
import os
from PIL import Image

st.title("📊 AI-Powered CSV Analyzer")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
user_goal = st.text_area("What do you want to know?", height=100)

if st.button("Run Analysis"):
    if uploaded_file is None or user_goal.strip() == "":
        st.warning("Please upload a CSV and enter a goal.")
    else:
        # Save file to workspace
        os.makedirs("workspace", exist_ok=True)
        file_path = os.path.join("workspace", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Run the AI pipeline
        with st.spinner("Processing..."):
            try:
                result_text = run_pipeline(file_path, user_goal)
                st.success("✅ Email summary generated and sent!")
                st.subheader("📧 Email Body")
                st.text(result_text)

                # Show plot if available
                plot_path = "workspace/plot.png"
                if os.path.exists(plot_path):
                    st.subheader("📈 Generated Plot")
                    image = Image.open(plot_path)
                    st.image(image, caption="AI-generated plot")
            except Exception as e:
                st.error(f"Something went wrong: {e}")