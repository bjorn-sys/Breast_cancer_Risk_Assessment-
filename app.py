# --------------------------------------------------------------
# 🩺 Breast Lump Classification: Benign vs Malignant (Market-Ready)
# --------------------------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from PIL import Image
import plotly.graph_objects as go

# --------------------------------------------------------------
# 📘 Load Model and Scaler
# --------------------------------------------------------------
with open("breast_model2.pkl", "rb") as file:
    model = pickle.load(file)

with open("scaler.pkl", "rb") as file:
    scaler = pickle.load(file)

# --------------------------------------------------------------
# 🧬 App Title and Summary
# --------------------------------------------------------------
st.set_page_config(page_title="Breast Lump Classifier", layout="wide")
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
# 🔧 Adjustable Threshold Slider
# --------------------------------------------------------------
threshold = st.sidebar.slider("Decision Threshold for Malignant Prediction", min_value=0.0, max_value=1.0, value=0.40, step=0.01)
st.sidebar.markdown(f"**Current Threshold:** {threshold:.2f}")

# --------------------------------------------------------------
# 🧩 File Upload Section
# --------------------------------------------------------------
st.subheader("📁 Upload CSV or Excel File for Batch Prediction")
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xls', 'xlsx'])

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

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        st.success("File loaded successfully!")
        st.dataframe(df.head())
        
        if all(f in df.columns for f in features):
            scaled_data = scaler.transform(df[features])
            probs = model.predict_proba(scaled_data)
            predictions = np.where(probs[:,1] >= threshold, 'Malignant', 'Benign')
            
            df['Prediction'] = predictions
            df['Prob_Benign'] = probs[:,0]
            df['Prob_Malignant'] = probs[:,1]
            
            # Highlight borderline cases (55%-85%)
            def highlight_borderline(row):
                if 0.55 <= row['Prob_Malignant'] <= 0.85:
                    return ['background-color: yellow']*len(row)
                return ['']*len(row)
            
            st.subheader("📊 Batch Prediction Results")
            st.dataframe(df.style.apply(highlight_borderline, axis=1))
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Predictions as CSV",
                data=csv,
                file_name="breast_predictions.csv",
                mime="text/csv"
            )
        else:
            missing = [f for f in features if f not in df.columns]
            st.error(f"Missing required features: {missing}")
    except Exception as e:
        st.error(f"Error reading file: {e}")

# --------------------------------------------------------------
# 🔢 Single Input Section
# --------------------------------------------------------------
st.subheader("🔢 Or Input Diagnostic Features Manually")

input_data = []
for feature in features:
    val = st.number_input(f"{feature.replace('_',' ').title()}", value=0.0)
    input_data.append(val)

input_df = pd.DataFrame([input_data], columns=features)

# --------------------------------------------------------------
# 🧠 Single Prediction and Visualization
# --------------------------------------------------------------
if st.button("🔍 Predict Single Input"):
    scaled_input = scaler.transform(input_df)
    probabilities = model.predict_proba(scaled_input)[0]
    prediction = 1 if probabilities[1] >= threshold else 0

    st.write("**Prediction Probability:**")
    st.write(f"- Benign: {probabilities[0]*100:.2f}%")
    st.write(f"- Malignant: {probabilities[1]*100:.2f}%")
    
    # Prediction Bar Chart
    fig = go.Figure(go.Bar(
        x=['Benign', 'Malignant'],
        y=[probabilities[0]*100, probabilities[1]*100],
        marker_color=['green','red'],
        text=[f"{probabilities[0]*100:.2f}%", f"{probabilities[1]*100:.2f}%"],
        textposition='auto'
    ))
    fig.update_layout(title_text="Prediction Probability", yaxis_title="Probability (%)")
    st.plotly_chart(fig)

    st.write("---")
    # Prediction Interpretation
    if prediction == 1:
        st.error("### 🧬 Malignant (Cancerous Tumor)")
        reason = "High values in area, radius, or concavity suggest irregular and invasive cell growth patterns consistent with malignancy."
        color = "red"
        # Show malignant image
        try:
            malignant_img = Image.open("malignant_example.jpg")
            st.image(malignant_img, caption="Malignant Tumor Example", use_column_width=True)
        except:
            st.warning("Malignant image not found. Place 'malignant_example.jpg' in app folder.")
        preventive = "- Regular self-exams & mammograms\n- Healthy diet & exercise\n- Avoid alcohol & smoking"
        corrective = "- Consult oncologist immediately\n- Follow biopsy/treatment protocols\n- Consider surgery/chemo/radiotherapy"
        instructions = "- Do not ignore early warning signs\n- Schedule follow-up tests\n- Keep medical records updated"
    else:
        st.success("### ✅ Benign (Non-Cancerous Tumor)")
        reason = "Features suggest small, smooth, and localized growth — typical of benign lesions."
        color = "green"
        # Show benign image
        try:
            benign_img = Image.open("benign_example.jpg")
            st.image(benign_img, caption="Benign Tumor Example", use_column_width=True)
        except:
            st.warning("Benign image not found. Place 'benign_example.jpg' in app folder.")
        preventive = "- Regular breast self-exams\n- Maintain healthy lifestyle\n- Routine check-ups"
        corrective = "- Monitor lump for changes\n- Consult doctor if size/texture changes\n- Follow medical advice"
        instructions = "- Track any new symptoms\n- Maintain regular screenings\n- Stay informed on breast health"

    # Feature Importance Radar Chart
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=input_data,
        theta=features,
        fill='toself',
        name='Feature Values',
        line_color=color
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True,
        title="🔹 Feature Profile (Single Input)"
    )
    st.plotly_chart(fig_radar)

    # Display measures and instructions
    st.subheader("📖 Why this prediction?")
    st.markdown(reason)
    st.write("---")
    st.subheader("💡 Preventive Measures")
    st.markdown(f"<span style='color:{color}'>{preventive.replace('-', '•')}</span>", unsafe_allow_html=True)
    st.subheader("🛠 Corrective Measures")
    st.markdown(f"<span style='color:{color}'>{corrective.replace('-', '•')}</span>", unsafe_allow_html=True)
    st.subheader("📋 Instructions")
    st.markdown(f"<span style='color:{color}'>{instructions.replace('-', '•')}</span>", unsafe_allow_html=True)

# --------------------------------------------------------------
# ⚠️ Medical Disclaimer
# --------------------------------------------------------------
st.write("---")
st.markdown("📚 *Developed for educational and research purposes only — not a medical diagnostic tool.*")
