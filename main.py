"""
Main application entry point for MedInsight AI - RadiologyAI Pro
"""
import os
import streamlit as st
import google.generativeai as genai
from gemini_api import GEMINI_API_KEY

# Import all features
from home.home import show_home_page, show_hospital_recommendation_page
from image_classification.classifier import show_classification_page
from xray.xray_report import show_xray_page
from ct_scan.ct_report import show_ct_page
from mri.mri_report import show_mri_page
from ultrasound.ultrasound_report import show_ultrasound_page

# Configure page settings
st.set_page_config(
    page_title="MedInsight AI - RadiologyAI Pro",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    /* Main styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        padding: 2rem;
    }
    
    /* Keep gradient effect but ensure emoji visibility */
    .main-header-with-gradient {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .project-title {
        font-size: 1.2rem;
        color: #667eea;
        text-align: center;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #4b5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Report box styling */
    .report-box {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin-top: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
        height: auto;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Small buttons */
    .stButton>button[kind="secondary"] {
        background: white;
        color: #667eea;
        border: 1px solid #667eea;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        height: auto;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background: #f0f5ff;
        transform: scale(1.05);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Upload area styling */
    .uploadedFile {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Home page cards */
    .home-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 1rem;
        transition: all 0.3s ease;
    }
    
    .home-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
    }
    
    .home-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    /* Stats box */
    .stats-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .stats-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Disclaimer box */
    .disclaimer-box {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0;
    }
    
    /* Quick access buttons */
    .quick-access-buttons {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Testimonials */
    .testimonial-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 3px solid #667eea;
    }
    
    /* Team table */
    .team-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .team-table th {
        padding: 15px;
        text-align: left;
    }
    
    .team-table td {
        padding: 12px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .team-table tr:last-child td {
        border-bottom: none;
    }
    </style>
""", unsafe_allow_html=True)

# Navigation
st.sidebar.title("🏥 MedInsight AI")
st.sidebar.markdown("### RadiologyAI Pro")
st.sidebar.markdown("---")

# Gemini API key setup (manual input supported)
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = GEMINI_API_KEY

st.sidebar.markdown("### Gemini API Key")
manual_key = st.sidebar.text_input(
    "Paste your Gemini API key",
    value=st.session_state["gemini_api_key"],
    type="password",
    help="This key is used only for this running app session."
).strip()

if manual_key:
    st.session_state["gemini_api_key"] = manual_key

active_key = st.session_state.get("gemini_api_key", "").strip()
if active_key:
    os.environ["GEMINI_API_KEY"] = active_key
    genai.configure(api_key=active_key)
    st.sidebar.caption("Gemini key loaded for this session.")
else:
    st.sidebar.warning("Add a valid Gemini API key to enable report generation.")
st.sidebar.markdown("---")

# Check if page is set in session state (from quick access buttons)
if 'page' in st.session_state:
    page = st.session_state['page']
    del st.session_state['page']  # Clear it after use
else:
    page = st.sidebar.radio(
        "Select Page:",
        ["🏠 Home", "🔍 Image Classification", "🩻 X-ray Report", 
         "🔬 CT Scan Report", "🧠 MRI Scan Report", "🔊 Ultrasound Report",
         "🏥 Hospital Recommendation"],
        label_visibility="collapsed"
    )

# Route to appropriate page
if page == "🏠 Home":
    show_home_page()
elif page == "🔍 Image Classification":
    show_classification_page()
elif page == "🩻 X-ray Report":
    show_xray_page()
elif page == "🔬 CT Scan Report":
    show_ct_page()
elif page == "🧠 MRI Scan Report":
    show_mri_page()
elif page == "🔊 Ultrasound Report":
    show_ultrasound_page()
elif page == "🏥 Hospital Recommendation":
    show_hospital_recommendation_page()
