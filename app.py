# --------------------------------------------------------------
# 🩺 Breast Lump Classification: Benign vs Malignant
# --------------------------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import pickle

# --------------------------------------------------------------
# 📘 Load Model and Scaler
# --------------------------------------------------------------
with open("breast_model2.pkl", "rb") as file:
    model = pickle.load(file)

with open("scaler.pkl", "rb") as file:
    scaler = pickle.load(file)

# --------------------------------------------------------------
# 🧬 App Title and Medical Summary
# --------------------------------------------------------------
st.title("🩺 Breast Lump Classification: Benign vs Malignant")

st.markdown("""
### 🧬 Benign vs Malignant Findings

**✅ Benign Findings**
- Growth Pattern: Non-invasive, localized  
- Borders: Well-defined, smooth margins  
- Growth Rate: Slow or stable  
- Histology: Normal cell structure, no atypia  
💡 *Typical Examples:* Fibroadenoma, cysts, fibrocystic changes  

**⚠️ Malignant Findings**
- Growth Pattern: Invasive, may spread (metastasis)  
- Borders: Irregular or spiculated  
- Growth Rate: Rapid  
- Histology: Atypical cells with abnormal nuclei  
💡 *Typical Examples:* Invasive ductal or lobular carcinoma  
""")

st.write("---")

# --------------------------------------------------------------
# 🧩 Feature Input Section
# --------------------------------------------------------------
st.subheader("🔢 Input Diagnostic Features")

# Define the top 10 important features
features = [
    'concave points_worst',
    'concave points_mean',
    'radius_worst',
    'perimeter_mean',
    'area_worst',
    'area_mean',
    'radius_mean',
    'perimeter_worst',
    'concavity_mean',
    'concavity_worst'
]

# Collect user input
input_data = []
for feature in features:
    val = st.number_input(f"{feature.replace('_', ' ').title()}", value=0.0)
    input_data.append(val)

# Convert input to DataFrame
input_df = pd.DataFrame([input_data], columns=features)

# --------------------------------------------------------------
# 🧠 Make Prediction
# --------------------------------------------------------------
if st.button("🔍 Predict"):
    # ✅ Apply the same scaler used during training
    scaled_input = scaler.transform(input_df)

    # Get probabilities and prediction
    probabilities = model.predict_proba(scaled_input)[0]

    # --------------------------------------------------------------
    # 🧩 Apply a tuned threshold for balanced output
    # --------------------------------------------------------------
    threshold = 0.40  # adjust slightly (0.5–0.6) for your dataset
    prediction =  1 if probabilities[1] >= threshold else 0


    # --------------------------------------------------------------
# 📈 Show Prediction Probabilities
# --------------------------------------------------------------
    st.write("**Prediction Probability:**")
    st.write(f"- Benign: {probabilities[0]*100:.2f}%")
    st.write(f"- Malignant: {probabilities[1]*100:.2f}%")
    st.info(f"🧭 Custom decision threshold applied: {threshold}")
  

    st.write("---")
    st.subheader("📊 Prediction Result")

    # --------------------------------------------------------------
    # 🎯 Display Prediction Outcome
    # --------------------------------------------------------------
    if prediction == 1:
        st.error("### 🧬 The model predicts: **Malignant (Cancerous Tumor)**")
        reason = (
            "High values in area, radius, or concavity suggest irregular and invasive "
            "cell growth patterns consistent with malignancy."
        )
    else:
        st.success("### ✅ The model predicts: **Benign (Non-Cancerous Tumor)**")
        reason = (
            "Features suggest small, smooth, and localized growth — typical of benign lesions."
        )

   
    # --------------------------------------------------------------
    # 🧩 Explain the Prediction
    # --------------------------------------------------------------
    st.subheader("📖 Why this prediction?")
    st.markdown("""
    The model relies heavily on:
    - **Concave points (mean/worst):** measures irregularities in tumor shape.  
      Higher values usually mean malignancy.  
    - **Radius & Perimeter (mean/worst):** larger sizes often correspond to invasive tumors.  
    - **Area (mean/worst):** larger mass area tends to indicate cancerous growth.  
    - **Concavity (mean/worst):** measures inward curvature of the tumor boundary.  

    💡 *Interpretation:*  
    When several shape-related features show large or irregular values,
    the model leans toward **malignant**; otherwise, it suggests **benign**.
    """)

    # Reason summary
    st.write("---")
    st.markdown(f"🩺 **Interpretation Summary:** {reason}")

# --------------------------------------------------------------
# ⚠️ Medical Disclaimer
# --------------------------------------------------------------
st.write("---")
st.markdown("📚 *Developed for educational and research purposes only — not a medical diagnostic tool.*")
