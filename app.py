import streamlit as st
import numpy as np
import pandas as pd
import pickle

# Load the saved KNN model
with open('breast_model.pkl', 'rb') as file:
    model = pickle.load(file)

st.set_page_config(page_title="Breast Lump Classifier", layout="wide")

# App title
st.title("🩺 Breast Lump Classification: Benign vs Malignant")
st.markdown("""
This Streamlit app predicts whether a breast lump is **Benign (Non-Cancerous)** or **Malignant (Cancerous)** using either manual entry or uploaded files.
""")

# Tabs for switching between Manual Input and File Upload
tab1, tab2 = st.tabs(["📌 Manual Input", "📂 Upload CSV or Excel"])

# -------------------------------------------
# 📌 TAB 1: MANUAL INPUT
# -------------------------------------------
with tab1:
    st.header("🔬 Enter Diagnostic Features")

    feature_names = [
        'radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean', 'smoothness_mean',
        'compactness_mean', 'concavity_mean', 'concave points_mean', 'symmetry_mean',
        'fractal_dimension_mean', 'radius_se', 'texture_se', 'perimeter_se', 'area_se',
        'smoothness_se', 'compactness_se', 'concavity_se', 'concave points_se',
        'symmetry_se', 'fractal_dimension_se', 'radius_worst', 'texture_worst',
        'perimeter_worst', 'area_worst', 'smoothness_worst', 'compactness_worst',
        'concavity_worst', 'concave points_worst', 'symmetry_worst', 'fractal_dimension_worst'
    ]

    user_input = []

    cols = st.columns(3)
    for i, feature in enumerate(feature_names):
        with cols[i % 3]:
            val = st.number_input(f"{feature.replace('_', ' ').title()}", min_value=0.0, format="%.4f")
            user_input.append(val)

    if st.button("🎯 Predict Diagnosis"):
        input_array = np.array(user_input).reshape(1, -1)
        prediction = model.predict(input_array)
        prob = model.predict_proba(input_array)[0]
        result = "🟢 Benign (Non-Cancerous)" if prediction[0] == 0 else "🔴 Malignant (Cancerous)"

        st.subheader("🔎 Prediction Result")
        st.success(result if prediction[0] == 0 else "")
        st.error(result if prediction[0] == 1 else "")
        st.info(f"🧪 Prediction Confidence: Benign {prob[0]*100:.2f}% | Malignant {prob[1]*100:.2f}%")

# -------------------------------------------
# 📂 TAB 2: FILE UPLOAD
# -------------------------------------------
with tab2:
    st.header("📁 Upload File for Bulk Prediction")

    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
        else:
            st.write("✅ Uploaded Data Preview:")
            st.dataframe(df.head())

            # Ensure all required columns are present
            if all(col in df.columns for col in feature_names):
                X_input = df[feature_names]
                predictions = model.predict(X_input)
                probabilities = model.predict_proba(X_input)

                df["Prediction"] = np.where(predictions == 0, "Benign", "Malignant")
                df["Benign (%)"] = (probabilities[:, 0] * 100).round(2)
                df["Malignant (%)"] = (probabilities[:, 1] * 100).round(2)

                st.subheader("📊 Prediction Summary")
                st.dataframe(df)

              


                # Option to download results
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Results as CSV", data=csv, file_name="breast_lump_predictions.csv", mime='text/csv')

            else:
                st.error("❌ The uploaded file is missing one or more required feature columns.")
                
# -------------------------------------------
# Footer
# -------------------------------------------
st.markdown("""
---
🧬 *Built for awareness and medical education only.*  
⚠️ *This tool does **not** replace a clinical diagnosis.*
""")
