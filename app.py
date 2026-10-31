import streamlit as st
import csv
import os
from datetime import datetime
from brake import run_evaluation

# Page Configuration
st.set_page_config(
    page_title="Mushroom Safety Brake & Field Guide",
    page_icon="🍄",
    layout="wide"
)

# Custom Styling for a Professional UI
st.markdown("""
    <style>
    .main-title { font-size: 2.8rem; font-weight: 800; color: #1e293b; margin-bottom: 0px; }
    .subtitle { font-size: 1.2rem; color: #64748b; margin-bottom: 2rem; }
    .lock-card {
        background-color: #fdf2f2; padding: 25px; border-radius: 12px;
        border-left: 6px solid #e74c3c; margin-bottom: 20px; color: #900c3f;
    }
    .lock-card h3, .lock-card p { color: #900c3f !important; }
    .success-card {
        background-color: #f0fdf4; padding: 25px; border-radius: 12px;
        border-left: 6px solid #2ecc71; margin-bottom: 20px; color: #145a32;
    }
    .success-card h4, .success-card p { color: #145a32 !important; }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🍄 Navigation")
page = st.sidebar.radio("Go to", ["🛡️ Safety Brake Evaluation", "📖 Mushroom Catalog", "📁 Past History & Logbook"])

# -------------------------------------------------------------
# PAGE 1: SAFETY BRAKE EVALUATION
# -------------------------------------------------------------
if page == "🛡️ Safety Brake Evaluation":
    st.markdown('<p class="main-title">🍄 Mushroom Safety Brake</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Refusing to answer when the AI disagrees with itself or when being wrong is fatal.</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload a clear photo of the mushroom...", type=["png", "jpg", "jpeg", "webp", "heic"])

    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            st.image(uploaded_file, caption="Target Field Specimen", width="stretch")
            
        with col2:
            st.markdown("### 🔍 Evaluation Console")
            st.markdown("Click below to run multi-pass verification and check against the deadly mushroom database.")
            if st.button("🛡️ Run Safety Evaluation", type="primary", use_container_width=True):
                with st.spinner("Analyzing mushroom morphology safely..."):
                    image_bytes = uploaded_file.read()
                    result = run_evaluation(image_bytes)
                    st.session_state['result'] = result
                    st.session_state['image_name'] = uploaded_file.name
                    
                    # Save record to results.csv for history logbook
                    file_exists = os.path.isfile("results.csv")
                    with open("results.csv", mode="a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        if not file_exists:
                            writer.writerow(["timestamp", "image_name", "common_name", "genus", "agreement", "locked", "reason"])
                        writer.writerow([
                            datetime.now().strftime("%Y-%m-%d %H:%M"),
                            uploaded_file.name,
                            result["common_name"],
                            result["top_genus"],
                            result["agreement"],
                            result["locked"],
                            result["lock_reason"]
                        ])
                    st.rerun()

    if 'result' in st.session_state:
        res = st.session_state['result']
        st.markdown("---")
        
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Model Agreement", value=f"{int(res['agreement']*100)}%")
        m2.metric(label="Identified Specimen", value=res['common_name'])
        m3.metric(label="System Status", value="LOCKED 🔒" if res['locked'] else "UNVERIFIED ⚠️")

        if res["locked"]:
            st.markdown(f"""
                <div class="lock-card">
                    <h3>🔒 LOCKED BY SAFETY BRAKE</h3>
                    <p><strong>Reason:</strong> {res['lock_reason']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if res["simple_traits"]:
                st.markdown("### 👁️ Visible Features Detected:")
                for trait in res["simple_traits"]:
                    st.markdown(f"- {trait}")
                    
            st.markdown("### 📋 Simple Field Verification Checklist (Required to Unlock)")
            st.markdown("Answer these easy questions about what you see in front of you:")
            
            c1 = st.checkbox("1. Does it match the shape or color described above?")
            t1 = st.text_input("What is the main color of the cap?")
            
            c2 = st.checkbox("2. Did you check where it is growing (e.g., on soil vs directly on a log)?")
            t2 = st.text_input("Where is it growing?:")
            
            c3 = st.checkbox("3. Are you willing to seek confirmation from an expert?")
            t3 = st.text_input("Your initials or notes:")
            
            all_checked = c1 and c2 and c3 and t1 and t2 and t3
            
            st.markdown("")
            if st.button("Unlock Specimen Data", disabled=not all_checked, use_container_width=True):
                st.markdown(f"""
                    <div class="success-card">
                        <h4>Manual Override Successful</h4>
                        <p>Specimen classified as: <strong>{res['common_name']} ({res['top_genus'].capitalize()})</strong></p>
                    </div>
                """, unsafe_allow_html=True)
                st.warning("🛑 **Final Safety Reminder:** Never consume wild mushrooms based on app results. Have this confirmed in person by a certified local mycological society.")
        else:
            st.markdown(f"""
                <div class="success-card">
                    <h3>⚠️ UNVERIFIED RESULT</h3>
                    <p>Agreement score is high, but all wild mushrooms carry inherent risks.</p>
                </div>
            """, unsafe_allow_html=True)
            st.info("🛑 **Final Safety Reminder:** Have this confirmed in person by a local mycological society.")

# -------------------------------------------------------------
# PAGE 2: MUSHROOM CATALOG
# -------------------------------------------------------------
elif page == "📖 Mushroom Catalog":
    st.markdown('<p class="main-title">📖 Mushroom Safety Catalog</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Reference guide of common edible vs. dangerous deadly genera.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔴 Deadly / Toxic Genera (Instant Brake Triggers)")
        st.markdown("""
        * **Amanita (*Death Cap, Destroying Angel, Fly Agaric*):** Features distinct bulbous bases (volva) and skirt-like rings. Extremely toxic.
        * **Galerina (*Funeral Bell*):** Small brown woodland mushrooms containing deadly amatoxins.
        * **Lepiota (*Deadly Lepiota*):** Small scaly caps with white gills. High toxicity.
        * **Gyromitra (*False Morels*):** Brain-like wrinkled caps. Highly toxic raw or improperly cooked.
        * **Cortinarius (*Webcaps*):** Rust-brown spore prints with cobweb-like partial veils. Causes delayed kidney failure.
        """)
        
    with col2:
        st.markdown("### 🟢 Common Beneficial / Choice Genera")
        st.markdown("""
        * **Cantharellus (*Chanterelles*):** Golden-yellow, trumpet-shaped with false blunt ridges instead of sharp gills. Apricot-like aroma.
        * **Boletus (*Porcini / Boletes*):** Spongy pore surface under the cap instead of gills. Thick sturdy stems.
        * **Pleurotus (*Oyster Mushrooms*):** Shelf-like clusters growing on dead wood with decurrent gills.
        * **Morchella (*True Morels*):** Distinct honeycomb pit-and-ridge cap structure, completely hollow inside.
        """)

# -------------------------------------------------------------
# PAGE 3: PAST HISTORY & LOGBOOK
# -------------------------------------------------------------
elif page == "📁 Past History & Logbook":
    st.markdown('<p class="main-title">📁 Past Specimen Logbook</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Review your past mushroom evaluations and safety logs.</p>', unsafe_allow_html=True)
    
    if os.path.exists("results.csv"):
        import pandas as pd
        df = pd.read_csv("results.csv")
        st.dataframe(df, use_container_width=True)
        
        if st.button("Clear Log History"):
            os.remove("results.csv")
            st.success("Log history cleared!")
            st.rerun()
    else:
        st.info("No saved evaluation records found yet. Upload a mushroom photo on the main evaluation page to create your first log entry!")