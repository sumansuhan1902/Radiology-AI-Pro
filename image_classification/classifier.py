"""
Image Classification module for MedInsight AI - RadiologyAI Pro
"""
import streamlit as st
from PIL import Image
import google.generativeai as genai
from datetime import datetime
from utils import process_image, generate_report_with_retry, create_pdf_report

def show_classification_page():
    """Display the image classification page"""
    st.markdown('<h1 class="main-header">🔍 <span class="main-header-with-gradient">Medical Image Classification</span></h1>', unsafe_allow_html=True)
    description = "Upload a medical image to automatically detect its type (X-ray, CT, MRI, or Ultrasound)"
    report_type = "Image Classification"
    prompt = """Analyze this medical image and classify it into one of the following categories:
    1. X-ray
    2. CT Scan
    3. MRI Scan
    4. Ultrasound
    
    Provide the classification with a confidence level and a brief explanation of the key features 
    that led to this classification. Format your response clearly with the classification type, 
    confidence percentage, and reasoning."""
    
    st.markdown(f'<p class="sub-header">{description}</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Optional patient information
    with st.expander("📋 Add Patient Information (Optional)"):
        col1, col2 = st.columns(2)
        with col1:
            patient_id = st.text_input("Patient ID")
            patient_age = st.text_input("Age")
        with col2:
            patient_gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
            referring_physician = st.text_input("Referring Physician")
    
    # File upload
    st.markdown("### 📤 Upload Medical Image")
    uploaded_file = st.file_uploader(
        "Choose a medical image file", 
        type=["jpg", "jpeg", "png", "dicom"],
        help="Supported formats: JPG, JPEG, PNG, DICOM"
    )
    
    if uploaded_file is not None:
        # Two column layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🖼️ Uploaded Image")
            image = process_image(uploaded_file)
            if image:
                st.image(image, use_container_width=True, caption=f"Uploaded: {uploaded_file.name}")
                
                # Image info
                st.markdown(f"""
                <div class="feature-card">
                    <b>File Name:</b> {uploaded_file.name}<br>
                    <b>File Size:</b> {uploaded_file.size / 1024:.2f} KB<br>
                    <b>Image Dimensions:</b> {image.size[0]} x {image.size[1]} px
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📊 Analysis Results")
            
            if st.button("🚀 Generate Report", use_container_width=True, type="primary"):
                result = generate_report_with_retry(image, prompt, model_name='gemini-2.0-flash-lite')
                
                if result:
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Store in session state for download
                    st.session_state['report_text'] = result
                    st.session_state['report_image'] = image
                    st.session_state['report_type'] = report_type
                    
                    st.success("✅ Report generated successfully!")
                else:
                    st.error("❌ Failed to generate report. Please try again.")
        
        # Download section (full width below)
        if 'report_text' in st.session_state:
            st.markdown("---")
            st.markdown("### 📥 Download Report")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                # Text download
                st.download_button(
                    label="📄 Download as Text",
                    data=st.session_state['report_text'],
                    file_name=f"{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                # PDF download
                patient_info = {}
                if patient_id:
                    patient_info["Patient ID"] = patient_id
                if patient_age:
                    patient_info["Age"] = patient_age
                if patient_gender:
                    patient_info["Gender"] = patient_gender
                if referring_physician:
                    patient_info["Referring Physician"] = referring_physician
                
                pdf_data = create_pdf_report(
                    st.session_state['report_text'],
                    st.session_state['report_image'],
                    st.session_state['report_type'],
                    patient_info if patient_info else None
                )
                
                if pdf_data:
                    st.download_button(
                        label="📑 Download as PDF",
                        data=pdf_data,
                        file_name=f"{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary"
                    )
            
            with col3:
                if st.button("🔄 Clear Results", use_container_width=True):
                    del st.session_state['report_text']
                    del st.session_state['report_image']
                    del st.session_state['report_type']
                    st.rerun()