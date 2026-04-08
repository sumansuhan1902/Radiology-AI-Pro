"""
Home page module for MedInsight AI - RadiologyAI Pro
"""
import streamlit as st
import google.generativeai as genai
import PyPDF2
from gemini_api import GEMINI_API_KEY
from utils import generate_text_report_with_retry

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# Comprehensive Hospital Database for Gulbarga
HOSPITALS_DATA = {
    # ✅ GOVERNMENT HOSPITALS
    "ESIC Hospital Gulbarga": {
        "rating": 4.8,
        "reviews": 1892,
        "type": "Government ESIC Hospital",
        "address": "ESIC Hospital, Industrial Area, Kalaburagi – 585104",
        "phone": "08472 247777",
        "availability": "24/7",
        "specialties": ["All Medical Specialties", "Emergency Care", "ICU", "Surgery", "Orthopedics", "Cardiology", "Neurology"],
        "equipment": ["MRI", "CT Scanner", "Digital X-ray", "Ultrasound", "ICU Equipment"],
        "success_rate": "95%",
        "patient_reviews": "Excellent ESIC facility with comprehensive healthcare services.",
        "cost_reputation": "Free for ESIC Beneficiaries / Very Low",
        "insurance": ["ESIC Scheme", "Cashless for ESIC Members"],
        "why_best": "Best for ESIC beneficiaries with free quality healthcare."
    },

    "Gulbarga Institute of Medical Sciences Hospital (GIMS)": {
        "rating": 4.9,
        "reviews": 2156,
        "type": "Government Medical College Hospital",
        "address": "New District Hospital Building, Adjacent to SP Office, Sedam Road, Kalaburagi – 585105",
        "phone": "09448 281614",
        "availability": "24/7",
        "specialties": ["All Medical Specialties", "Neurology", "Neurosurgery", "Cardiology", "Orthopedics", "Emergency Care", "Trauma Care", "Advanced Surgery", "ICU", "Critical Care"],
        "equipment": ["Latest MRI Machines", "128-slice CT Scanner", "Digital X-ray", "Ultrasound", "Cath Lab", "Advanced ICU Equipment"],
        "success_rate": "96%",
        "patient_reviews": "Premier medical college hospital with experienced specialists and full facilities.",
        "cost_reputation": "Minimal - Very Low cost with government subsidies & Cashless under govt schemes",
        "insurance": ["Ayushman Bharat", "State Schemes", "Most Private TPA"],
        "why_best": "Best option for critical and serious cases with low cost."
    },

    "Basweshwar Hospital Gulbarga": {
        "rating": 4.7,
        "reviews": 1245,
        "type": "Government Hospital",
        "address": "Basweshwar Hospital, Kalaburagi – 585105",
        "phone": "08472 256789",
        "availability": "24/7",
        "specialties": ["General Medicine", "Surgery", "Emergency Care", "Pediatrics", "Orthopedics", "ICU"],
        "equipment": ["CT Scanner", "X-ray", "Ultrasound", "Lab Facilities", "ICU"],
        "success_rate": "93%",
        "patient_reviews": "Reliable government hospital with good patient care.",
        "cost_reputation": "Minimal - Very Low government rates with subsidies",
        "insurance": ["Government Schemes", "Ayushman Bharat"],
        "why_best": "Trusted government facility with minimal cost and quality care."
    },

    "District Government Hospital (Old GIMS Wing)": {
        "rating": 4.6,
        "reviews": 1543,
        "type": "Government District Hospital",
        "address": "District Hospital Campus, Sedam Road, Kalaburagi – 585105",
        "phone": "08472 278644",
        "availability": "24/7",
        "specialties": ["Emergency", "General Medicine", "Surgery", "OBG", "Pediatrics", "Orthopedics"],
        "equipment": ["CT", "X-ray", "Ultrasound"],
        "success_rate": "92%",
        "patient_reviews": "Affordable treatment with government support.",
        "cost_reputation": "Very Low / Free",
        "insurance": ["Government Schemes", "Free BPL Support"],
        "why_best": "Best for patients needing free or subsidized treatment."
    },

    # ✅ TOP MULTISPECIALITY
    "Star Care Multi-Speciality Hospital": {
        "rating": 5.0,
        "reviews": 764,
        "type": "Multispeciality Hospital",
        "address": "Sy.no 81 & 82, Sedam Road, Kalaburagi",
        "phone": "088929 85555",
        "availability": "24/7",
        "specialties": ["Neurology", "Cardiology", "Orthopedics", "ICU", "Critical Care"],
        "equipment": ["Latest MRI", "128-slice CT", "Digital Radiography", "4D Ultrasound"],
        "success_rate": "97%",
        "patient_reviews": "Best ICU & doctor quality in Gulbarga.",
        "cost_reputation": "Medium",
        "insurance": ["Cashless + Govt Schemes"],
        "why_best": "Best overall private hospital with top emergency care."
    },

    "United Hospital Gulbarga": {
        "rating": 4.8,
        "reviews": 1835,
        "type": "General Hospital",
        "address": "#1-43/A, Opp. Siddarth Law College, Court Road, Kalaburagi",
        "phone": "084722 55006",
        "availability": "24/7",
        "specialties": ["Emergency", "Cardiology", "Neurology", "ICU", "General Surgery"],
        "equipment": ["CT", "MRI", "ICU Ventilators"],
        "success_rate": "95%",
        "patient_reviews": "Strong doctors and clean facility.",
        "cost_reputation": "Medium to High",
        "insurance": ["Full Cashless Available"],
        "why_best": "Fast-response emergency & well-equipped ICU."
    },

    "Shanta Hospital": {
        "rating": 4.8,
        "reviews": 183,
        "type": "Multispeciality Hospital",
        "address": "Near High Court, Kalaburagi",
        "phone": "099646 05999",
        "availability": "24/7",
        "specialties": ["Trauma", "Critical Care", "Emergency Surgery"],
        "equipment": ["Emergency CT", "ICU Ventilators", "Rapid Response Team"],
        "success_rate": "94%",
        "patient_reviews": "Best emergency and trauma handling.",
        "cost_reputation": "Medium to High",
        "insurance": ["Cashless"],
        "why_best": "Fastest emergency stabilization team."
    },

    "Sunrise Multispeciality Hospital": {
        "rating": 4.7,
        "reviews": 840,
        "type": "Multispeciality Hospital",
        "address": "MSK Mill Road, Kalaburagi",
        "phone": "082968 94908",
        "availability": "24/7",
        "specialties": ["Cardiology", "Gastro", "Neurology", "Pediatrics"],
        "equipment": ["MRI", "CT", "Cath Lab"],
        "success_rate": "93%",
        "patient_reviews": "Good for chronic and heart cases.",
        "cost_reputation": "Medium",
        "insurance": ["Cashless"],
        "why_best": "Strong heart care and diagnostics."
    },

    "MANUR Multi Speciality Hospital": {
        "rating": 4.7,
        "reviews": 424,
        "type": "Multispeciality Hospital",
        "address": "Barey Hills Circle, Ring Road, Kalaburagi",
        "phone": "072049 47892",
        "availability": "24/7",
        "specialties": ["General Medicine", "Surgery", "Gynecology", "Orthopedics"],
        "equipment": ["CT", "X-ray", "USG"],
        "success_rate": "91%",
        "patient_reviews": "Excellent nursing and post-surgery care.",
        "cost_reputation": "Medium",
        "insurance": ["Standard insurance"],
        "why_best": "Best patient comfort and nursing care."
    },

    "Asian Superspeciality Hospital": {
        "rating": 4.5,
        "reviews": 74,
        "type": "Superspeciality",
        "address": "Ring Road, Kalaburagi",
        "phone": "096064 96370",
        "availability": "24/7",
        "specialties": ["Superspeciality Surgeries", "Advanced Cases"],
        "equipment": ["High-end MRI", "Advanced CT"],
        "success_rate": "95%",
        "patient_reviews": "Expert surgical teams.",
        "cost_reputation": "High",
        "insurance": ["Premium Insurance"],
        "why_best": "Used for rare / complex operations."
    },

    # ✅ SPECIALIZED CENTERS
    "Nisty Heart Centre": {
        "rating": 4.6,
        "reviews": 512,
        "type": "Cardiac Super Speciality Hospital",
        "address": "Lahoti Enclave, Aiwan-E-Shahi Road, Kalaburagi",
        "phone": "08472 232596",
        "availability": "24/7",
        "specialties": ["Cardiology", "Heart Surgery", "Cardiac ICU"],
        "equipment": ["Cath Lab", "ECG", "Echo", "Holter"],
        "success_rate": "93%",
        "patient_reviews": "Best trusted cardiac hub.",
        "cost_reputation": "Medium-High",
        "insurance": ["Cashless"],
        "why_best": "#1 Choice for heart attacks & heart disease."
    },

    "HCG Cancer Center (Kalaburagi)": {
        "rating": 4.7,
        "reviews": 691,
        "type": "Cancer Super Speciality Hospital",
        "address": "Khuba Plot, Brhampur, Kalaburagi – 585105",
        "phone": "08472 661000",
        "availability": "24/7",
        "specialties": ["Medical Oncology", "Radiation Oncology", "Cancer Surgery"],
        "equipment": ["Linear Accelerator", "PET-CT", "Day Care Chemo"],
        "success_rate": "88%",
        "patient_reviews": "Best cancer center in region.",
        "cost_reputation": "High",
        "insurance": ["Private Insurance", "Govt Cancer Schemes"],
        "why_best": "Only advanced integrated cancer center in the city."
    },

    # ✅ MID-RANGE PRACTICAL HOSPITALS
    "Chirayu Hospital Gulbarga": {
        "rating": 4.2,
        "reviews": 491,
        "type": "Multispeciality Hospital",
        "address": "Court Road, Opp GESCOM Office, Kalaburagi",
        "phone": "08472 241717",
        "availability": "24/7",
        "specialties": ["General Surgery", "OBG", "Pediatrics", "ICU"],
        "equipment": ["X-ray", "Ultrasound", "Ventilators"],
        "success_rate": "88%",
        "patient_reviews": "Common admission hospital.",
        "cost_reputation": "Medium",
        "insurance": ["Insurance Accepted"],
        "why_best": "Reliable mid-range treatment option."
    },

    "Vaatsalya Hospital": {
        "rating": 4.1,
        "reviews": 332,
        "type": "Multispeciality Hospital",
        "address": "RTO Circle, SH-10, Kalaburagi",
        "phone": "08472 222299",
        "availability": "24/7",
        "specialties": ["Pediatrics", "Maternity", "General Medicine"],
        "equipment": ["NICU", "USG", "X-ray"],
        "success_rate": "85%",
        "patient_reviews": "Affordable family-centered care.",
        "cost_reputation": "Low to Medium",
        "insurance": ["Govt + Private Insurance"],
        "why_best": "Go-to hospital for maternity & child care."
    },

    "Sadbhava Hospital Gulbarga": {
        "rating": 4.5,
        "reviews": 253,
        "type": "Hospital",
        "address": "Old Jewargi Rd, Opp Muddi Hanuman Temple",
        "phone": "084722 43555",
        "availability": "8 AM - 8 PM",
        "specialties": ["General Medicine", "Minor Surgery", "Diagnostics"],
        "equipment": ["Digital X-ray", "Ultrasound", "Lab"],
        "success_rate": "89%",
        "patient_reviews": "Budget-friendly, clean environment.",
        "cost_reputation": "Low",
        "insurance": ["Basic Insurance"],
        "why_best": "Best for OPD & non-emergency cases."
    }
}

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF report"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def analyze_medical_report(report_text):
    """Analyze medical report and extract key information"""
    prompt = f"""Analyze this medical imaging report and extract key information:

MEDICAL REPORT:
{report_text}

Provide analysis in this exact format:
1. REPORT TYPE: (X-ray/CT Scan/MRI/Ultrasound)
2. ANATOMICAL REGION: (which body part)
3. KEY FINDINGS: (main findings from the report)
4. SEVERITY: (Normal/Mild/Moderate/Severe/Critical)
5. ABNORMALITIES DETECTED: (list any, or "None")
6. RECOMMENDED SPECIALTIES: (which medical specialists needed)
7. URGENCY LEVEL: (Routine/Urgent/Emergency)
8. TREATMENT IMPLICATIONS: (what type of care might be needed)

Be specific and medical in your analysis."""
    
    try:
        with st.spinner("🔬 Analyzing medical report with AI..."):
            response = generate_text_report_with_retry(prompt, model_name='gemini-2.0-flash-lite')
            return response
    except Exception as e:
        st.error(f"Error analyzing report: {str(e)}")
        return None

def get_hospital_recommendations(report_analysis, patient_info):
    """Get AI-powered hospital recommendations based on report"""
    prompt = f"""Based on this medical report analysis, recommend the TOP 3-4 best hospitals in Gulbarga (Kalaburagi):

REPORT ANALYSIS:
{report_analysis}

PATIENT INFO:
- Age: {patient_info.get('Age', 'Not provided')}
- Gender: {patient_info.get('Gender', 'Not provided')}
- Budget: {patient_info.get('Budget Preference', 'Not provided')}
- Emergency Case: {patient_info.get('Emergency Case', 'No')}

AVAILABLE HOSPITALS:
{HOSPITALS_DATA}

Recommend hospitals based on best match for the patient's condition, budget, and requirements. All hospitals should be considered equally without any special priority.

For EACH recommended hospital, provide:

🏥 **HOSPITAL NAME**
⭐ **Rating & Reviews**: [rating] ([review count] reviews)
🏛️ **Hospital Type**: Government/Private Multispeciality

✅ **Why This Hospital is BEST for This Case:**
   - Specific reasons based on the medical findings
   - Relevant specialties and equipment available
   - Success rate for similar cases

🔬 **Treatment Approach:**
   - Expected diagnostic procedures
   - Specialist consultations needed
   - Treatment protocol

💰 **COST BREAKDOWN (in INR):**
   - Consultation: ₹X - ₹Y
   - Diagnostic tests: ₹X - ₹Y
   - **TOTAL ESTIMATED: ₹X - ₹Y**
   - Insurance/Cashless: [details]

⏱️ **Timeline:**
   - Diagnosis time
   - Treatment duration

📞 **Contact:**
   - Phone: [number]
   - Address: [address]
   - Availability: [hours]

Rank by: 1) Condition relevance, 2) Budget appropriateness, 3) Success rate, 4) Patient reviews, 5) Hospital ratings."""
    
    try:
        with st.spinner("🏥 Finding best hospitals for your condition..."):
            response = generate_text_report_with_retry(prompt, model_name='gemini-2.0-flash-lite')
            return response
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return None

def show_hospital_recommendation_system():
    """Display the hospital recommendation system on the same page"""
    st.markdown('<h2 class="main-header">🏥 Smart Hospital Recommendation System</h2>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Medical Report Analysis & Hospital Matching for Gulbarga</p>', unsafe_allow_html=True)

    # Upload Section
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Medical Report")
    st.info("✅ Accepts: X-ray Reports | CT Scan Reports | MRI Reports | Ultrasound Reports (PDF format)")

    uploaded_report = st.file_uploader(
        "Choose your medical imaging report",
        type=['pdf'],
        key="hospital_report_uploader",
        help="Upload X-ray, CT, MRI, or Ultrasound report in PDF format"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_report:
        st.success(f"✅ Report uploaded successfully: **{uploaded_report.name}**")
        
        # Patient Information
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 👤 Patient Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            patient_name = st.text_input("Patient Name *", placeholder="Enter full name", key="patient_name")
            patient_age = st.number_input("Age *", min_value=1, max_value=120, value=30, key="patient_age")
        
        with col2:
            patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="patient_gender")
            patient_contact = st.text_input("Contact Number", placeholder="+91 XXXXX XXXXX", key="patient_contact")
        
        with col3:
            budget_pref = st.selectbox(
                "Budget Preference *",
                [
                    "Very Low (Government/Free - ₹0 - ₹5,000)",
                    "Low (₹5,000 - ₹20,000)",
                    "Medium (₹20,000 - ₹50,000)",
                    "High (₹50,000+)"
                ],
                key="budget_preference"
            )
            emergency_case = st.checkbox("🚨 Emergency/Urgent Case", key="emergency_case")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Analyze Button
        if st.button("🔬 Analyze Report & Find Best Hospitals", type="primary", use_container_width=True, key="analyze_hospitals_btn"):
            if patient_name and patient_age:
                # Extract report text
                report_text = extract_text_from_pdf(uploaded_report)
                
                if report_text:
                    # Display extracted report preview
                    with st.expander("📄 View Extracted Report Text", expanded=False):
                        st.text_area("Report Content", report_text, height=200, disabled=True, key="report_content")
                    
                    # Analyze report
                    st.markdown("---")
                    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                    st.markdown('<h3 class="sub-header">🔬 Medical Report Analysis</h3>', unsafe_allow_html=True)
                    
                    analysis = analyze_medical_report(report_text)
                    
                    if analysis:
                        # Parse and display analysis in a structured format
                        st.markdown('<div style="background: #fff7ed; border-left: 3px solid #f59e0b; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">', unsafe_allow_html=True)
                        
                        analysis_lines = analysis.strip().split('\n')
                        for line in analysis_lines:
                            if line.strip():
                                if any(keyword in line for keyword in ['REPORT TYPE:', 'ANATOMICAL REGION:', 'SEVERITY:', 'URGENCY LEVEL:']):
                                    st.markdown(f'<div style="background: white; padding: 1rem; margin: 0.5rem 0; border-radius: 6px; border-left: 3px solid #f59e0b;"><strong>{line}</strong></div>', unsafe_allow_html=True)
                                elif line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                                    st.markdown(f'<div style="background: white; padding: 1rem; margin: 0.5rem 0; border-radius: 6px; border-left: 3px solid #f59e0b;">{line}</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<p style="margin: 0.5rem 0;">{line}</p>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Get recommendations
                        st.markdown("---")
                        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                        st.markdown('<h3 class="sub-header">🏥 Recommended Hospitals</h3>', unsafe_allow_html=True)
                        
                        patient_info = {
                            "Patient Name": patient_name,
                            "Age": str(patient_age),
                            "Gender": patient_gender,
                            "Contact": patient_contact if patient_contact else "Not provided",
                            "Budget Preference": budget_pref,
                            "Emergency Case": "Yes" if emergency_case else "No"
                        }
                        
                        recommendations = get_hospital_recommendations(analysis, patient_info)
                        
                        if recommendations:
                            # Parse and display recommendations with enhanced formatting
                            rec_sections = recommendations.split('🏥')
                            
                            for idx, section in enumerate(rec_sections[1:], 1):  # Skip first empty split
                                st.markdown('<div style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 1rem 0; border: 1px solid #e2e8f0;">', unsafe_allow_html=True)
                                
                                # Check if it's a government hospital
                                is_govt = "Government" in section or "ESIC" in section
                                
                                if is_govt:
                                    st.markdown('<div style="background: #10b981; color: white; padding: 0.4rem 0.8rem; border-radius: 6px; font-weight: 500; display: inline-block; margin-bottom: 0.8rem; font-size: 0.85rem;">🏛️ GOVERNMENT HOSPITAL - Cashless/Free Treatment Available</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div style="background: #3b82f6; color: white; padding: 0.4rem 0.8rem; border-radius: 6px; font-weight: 500; display: inline-block; margin-bottom: 0.8rem; font-size: 0.85rem;">🏢 PRIVATE HOSPITAL</div>', unsafe_allow_html=True)
                                
                                # Display hospital content
                                lines = section.split('\n')
                                for line in lines:
                                    if line.strip():
                                        # Format special sections
                                        if '⭐' in line or 'Rating' in line:
                                            st.markdown(f'<div style="background: #f59e0b; color: white; padding: 0.4rem 0.8rem; border-radius: 6px; font-weight: 500; display: inline-block; margin-bottom: 0.5rem; font-size: 0.9rem;">⭐ {line.replace("⭐", "").strip()}</div>', unsafe_allow_html=True)
                                        elif '💰' in line and 'TOTAL' in line:
                                            st.markdown(f'<div style="background: #10b981; color: white; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 500; display: inline-block; margin: 0.5rem 0; font-size: 0.95rem;">{line}</div>', unsafe_allow_html=True)
                                        elif '📞' in line or 'Phone' in line or 'Contact' in line:
                                            st.markdown(f'<div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 0.8rem 0; border-left: 3px solid #6366f1;">{line}</div>', unsafe_allow_html=True)
                                        else:
                                            st.markdown(f'{line}')
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                if idx < len(rec_sections) - 1:
                                    st.markdown("<hr style='margin: 2rem 0; border: none; border-top: 2px solid #e2e8f0;'>", unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("❌ Failed to analyze the medical report. Please try again.")
            else:
                st.error("⚠️ Please enter patient name and age to continue.")

def show_hospital_recommendation_page():
    """Display the hospital recommendation system as a separate page"""
    st.markdown('<h1 class="main-header">🏥 <span class="main-header-with-gradient">Smart Hospital Recommendation System</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Medical Report Analysis & Hospital Matching for Gulbarga</p>', unsafe_allow_html=True)
    
    # Information section
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("""
    <h3 style="color: #667eea; text-align: center;">🏥 Hospital Recommendation System</h3>
    <p style="text-align: center; color: #6b7280; font-size: 1.1rem;">
    Upload a medical report and get AI-powered hospital recommendations based on your condition, 
    budget, and location in Gulbarga. Our system analyzes your medical report and matches you with 
    the most suitable hospitals in your area.
    </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Upload Section
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Medical Report")
    st.info("✅ Accepts: X-ray Reports | CT Scan Reports | MRI Reports | Ultrasound Reports (PDF format)")

    uploaded_report = st.file_uploader(
        "Choose your medical imaging report",
        type=['pdf'],
        key="hospital_report_uploader",
        help="Upload X-ray, CT, MRI, or Ultrasound report in PDF format"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_report:
        st.success(f"✅ Report uploaded successfully: **{uploaded_report.name}**")
        
        # Patient Information
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 👤 Patient Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            patient_name = st.text_input("Patient Name *", placeholder="Enter full name", key="patient_name")
            patient_age = st.number_input("Age *", min_value=1, max_value=120, value=30, key="patient_age")
        
        with col2:
            patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="patient_gender")
            patient_contact = st.text_input("Contact Number", placeholder="+91 XXXXX XXXXX", key="patient_contact")
        
        with col3:
            budget_pref = st.selectbox(
                "Budget Preference *",
                [
                    "Very Low (Government/Free - ₹0 - ₹5,000)",
                    "Low (₹5,000 - ₹20,000)",
                    "Medium (₹20,000 - ₹50,000)",
                    "High (₹50,000+)"
                ],
                key="budget_preference"
            )
            emergency_case = st.checkbox("🚨 Emergency/Urgent Case", key="emergency_case")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Analyze Button
        if st.button("🔬 Analyze Report & Find Best Hospitals", type="primary", use_container_width=True, key="analyze_hospitals_btn"):
            if patient_name and patient_age:
                # Extract report text
                report_text = extract_text_from_pdf(uploaded_report)
                
                if report_text:
                    # Display extracted report preview
                    with st.expander("📄 View Extracted Report Text", expanded=False):
                        st.text_area("Report Content", report_text, height=200, disabled=True, key="report_content")
                    
                    # Analyze report
                    st.markdown("---")
                    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                    st.markdown('<h3 class="sub-header">🔬 Medical Report Analysis</h3>', unsafe_allow_html=True)
                    
                    analysis = analyze_medical_report(report_text)
                    
                    if analysis:
                        # Parse and display analysis in a structured format
                        st.markdown('<div style="background: #fff7ed; border-left: 3px solid #f59e0b; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">', unsafe_allow_html=True)
                        
                        analysis_lines = analysis.strip().split('\n')
                        for line in analysis_lines:
                            if line.strip():
                                if any(keyword in line for keyword in ['REPORT TYPE:', 'ANATOMICAL REGION:', 'SEVERITY:', 'URGENCY LEVEL:']):
                                    st.markdown(f'<div style="background: white; padding: 1rem; margin: 0.5rem 0; border-radius: 6px; border-left: 3px solid #f59e0b;"><strong>{line}</strong></div>', unsafe_allow_html=True)
                                elif line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                                    st.markdown(f'<div style="background: white; padding: 1rem; margin: 0.5rem 0; border-radius: 6px; border-left: 3px solid #f59e0b;">{line}</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<p style="margin: 0.5rem 0;">{line}</p>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Get recommendations
                        st.markdown("---")
                        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                        st.markdown('<h3 class="sub-header">🏥 Recommended Hospitals</h3>', unsafe_allow_html=True)
                        
                        patient_info = {
                            "Patient Name": patient_name,
                            "Age": str(patient_age),
                            "Gender": patient_gender,
                            "Contact": patient_contact if patient_contact else "Not provided",
                            "Budget Preference": budget_pref,
                            "Emergency Case": "Yes" if emergency_case else "No"
                        }
                        
                        recommendations = get_hospital_recommendations(analysis, patient_info)
                        
                        if recommendations:
                            # Parse and display recommendations with enhanced formatting
                            rec_sections = recommendations.split('🏥')
                            
                            for idx, section in enumerate(rec_sections[1:], 1):  # Skip first empty split
                                st.markdown('<div style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 1rem 0; border: 1px solid #e2e8f0;">', unsafe_allow_html=True)
                                
                                # Check if it's a government hospital
                                is_govt = "Government" in section or "ESIC" in section
                                
                                if is_govt:
                                    st.markdown('<div style="background: #10b981; color: white; padding: 0.4rem 0.8rem; border-radius: 6px; font-weight: 500; display: inline-block; margin-bottom: 0.8rem; font-size: 0.85rem;">🏛️ GOVERNMENT HOSPITAL - Cashless/Free Treatment Available</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div style="background: #3b82f6; color: white; padding: 0.4rem 0.8rem; border-radius: 6px; font-weight: 500; display: inline-block; margin-bottom: 0.8rem; font-size: 0.85rem;">🏢 PRIVATE HOSPITAL</div>', unsafe_allow_html=True)
                                
                                # Display hospital content
                                lines = section.split('\n')
                                for line in lines:
                                    if line.strip():
                                        # Format special sections
                                        if '⭐' in line or 'Rating' in line:
                                            st.markdown(f'<div style="background: #f59e0b; color: white; padding: 0.4rem 0.8rem; border-radius: 6px; font-weight: 500; display: inline-block; margin-bottom: 0.5rem; font-size: 0.9rem;">⭐ {line.replace("⭐", "").strip()}</div>', unsafe_allow_html=True)
                                        elif '💰' in line and 'TOTAL' in line:
                                            st.markdown(f'<div style="background: #10b981; color: white; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 500; display: inline-block; margin: 0.5rem 0; font-size: 0.95rem;">{line}</div>', unsafe_allow_html=True)
                                        elif '📞' in line or 'Phone' in line or 'Contact' in line:
                                            st.markdown(f'<div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 0.8rem 0; border-left: 3px solid #6366f1;">{line}</div>', unsafe_allow_html=True)
                                        else:
                                            st.markdown(f'{line}')
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                if idx < len(rec_sections) - 1:
                                    st.markdown("<hr style='margin: 2rem 0; border: none; border-top: 2px solid #e2e8f0;'>", unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("❌ Failed to analyze the medical report. Please try again.")
            else:
                st.error("⚠️ Please enter patient name and age to continue.")

def show_home_page():
    """Display the home page content"""
    # Hero Section with improved styling
    st.markdown('<p class="project-title">MedInsight AI Presents</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">RadiologyAI Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Diagnostic Image Analysis Platform</p>', unsafe_allow_html=True)
    
    # Enhanced Introduction with better visual appeal
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="feature-card">
        <h3 style="color: #667eea; text-align: center;">Welcome to the Future of Medical Imaging</h3>
        <p style="text-align: center; color: #6b7280; font-size: 1.1rem;">
        Our advanced AI-powered platform provides instant, comprehensive analysis of medical images, 
        helping healthcare professionals make faster and more informed decisions.
        </p>
        <p style="text-align: center; color: #667eea; font-weight: 600; margin-top: 1rem;">
        MedInsight AI - RadiologyAI Pro
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Stats Section with improved visuals
    st.markdown("### 📊 Platform Capabilities")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-box">
            <div class="stats-number">5</div>
            <div class="stats-label">Imaging Modalities</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-box">
            <div class="stats-number">AI</div>
            <div class="stats-label">Powered Analysis</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-box">
            <div class="stats-number">PDF</div>
            <div class="stats-label">Report Export</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stats-box">
            <div class="stats-number">24/7</div>
            <div class="stats-label">Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Features Section with improved layout and icons
    st.markdown("### 🎯 Key Features")
    
    # First row of features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="home-card">
            <div class="home-icon">🔍</div>
            <h3 style="color: #667eea;">Image Classification</h3>
            <p style="color: #6b7280;">
            Automatically identify and classify medical images into X-ray, CT, MRI, or Ultrasound categories 
            with high accuracy and confidence scoring.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="home-card">
            <div class="home-icon">🩻</div>
            <h3 style="color: #667eea;">X-ray Diagnostics</h3>
            <p style="color: #6b7280;">
            Generate structured diagnostic reports from X-ray images with detailed findings, 
            impressions, and clinical recommendations.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="home-card">
            <div class="home-icon">🧠</div>
            <h3 style="color: #667eea;">MRI Interpretation</h3>
            <p style="color: #6b7280;">
            Advanced MRI scan analysis with sequence identification, signal characteristics, 
            and detailed anatomical assessments.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="home-card">
            <div class="home-icon">🔬</div>
            <h3 style="color: #667eea;">CT Scan Analysis</h3>
            <p style="color: #6b7280;">
            Comprehensive CT scan interpretation with detailed analysis of anatomical structures, 
            densities, and potential abnormalities.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="home-card">
            <div class="home-icon">🔊</div>
            <h3 style="color: #667eea;">Ultrasound Reports</h3>
            <p style="color: #6b7280;">
            Detailed ultrasound image analysis with measurements, echogenicity patterns, 
            and diagnostic impressions.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="home-card">
            <div class="home-icon">🏥</div>
            <h3 style="color: #667eea;">Hospital Recommendation</h3>
            <p style="color: #6b7280;">
            Get AI-powered hospital recommendations based on your medical condition, 
            budget, and location in Gulbarga.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # How it works section with improved visuals
    st.markdown("### 🚀 How It Works")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <h2 style="color: #667eea;">1️⃣</h2>
            <h4>Upload Image</h4>
            <p style="color: #6b7280;">Select and upload your medical image in supported formats</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <h2 style="color: #667eea;">2️⃣</h2>
            <h4>AI Analysis</h4>
            <p style="color: #6b7280;">Our AI analyzes the image and generates comprehensive insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <h2 style="color: #667eea;">3️⃣</h2>
            <h4>Get Report</h4>
            <p style="color: #6b7280;">Receive detailed analysis and download PDF report</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    

    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Access Section
    st.markdown("### ⚡ Quick Access")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if st.button("🔍 Classification", use_container_width=True, type="secondary"):
            st.session_state['page'] = "🔍 Image Classification"
            st.rerun()
    
    with col2:
        if st.button("🩻 X-ray", use_container_width=True, type="secondary"):
            st.session_state['page'] = "🩻 X-ray Report"
            st.rerun()
            
    with col3:
        if st.button("🔬 CT Scan", use_container_width=True, type="secondary"):
            st.session_state['page'] = "🔬 CT Scan Report"
            st.rerun()
            
    with col4:
        if st.button("🧠 MRI", use_container_width=True, type="secondary"):
            st.session_state['page'] = "🧠 MRI Scan Report"
            st.rerun()
            
    with col5:
        if st.button("🔊 Ultrasound", use_container_width=True, type="secondary"):
            st.session_state['page'] = "🔊 Ultrasound Report"
            st.rerun()
            
    with col6:
        if st.button("🏥 Hospital", use_container_width=True, type="secondary"):
            st.session_state['page'] = "🏥 Hospital Recommendation"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Testimonials Section
    st.markdown("### 🌟 What Our Users Say")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #6b7280;">"This platform has significantly reduced the time we spend on preliminary image analysis. The accuracy is impressive!"</p>
            <p style="font-weight: 600; color: #667eea; margin-top: 1rem;">- Dr. Sarah Johnson, Radiologist</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #6b7280;">"The hospital recommendation system is a game-changer for patient care. It helps us find the best facilities quickly."</p>
            <p style="font-weight: 600; color: #667eea; margin-top: 1rem;">- Dr. Michael Chen, Emergency Medicine</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Call to action with improved design
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white;">
            <h3 style="color: white;">Ready to Transform Your Medical Imaging Workflow?</h3>
            <p style="color: #e0e7ff;">Select a feature from the navigation menu or use the quick access buttons above to begin your analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Team Section with improved styling
    st.markdown("### 👥 Project Team")
    st.markdown("""
    <div class="feature-card">
        <table class="team-table">
            <thead>
                <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <th style="border-radius: 10px 0 0 0;">Role</th>
                    <th style="border-radius: 0 10px 0 0;">Name</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #f8f9fa;">
                    <td><b>👨‍✈️ Captain</b></td>
                    <td>Mohd Zaheeruddin</td>
                </tr>
                <tr style="background-color: #ffffff;">
                    <td><b>🎖️ Vice Captain</b></td>
                    <td>Suman Suhan</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td><b>👤 Team Member</b></td>
                    <td>Subiya Mahveen</td>
                </tr>
                <tr style="background-color: #ffffff;">
                    <td><b>👤 Team Member</b></td>
                    <td>Syed Amaan Hussani</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td><b>👤 Team Member</b></td>
                    <td>Humayun Attar</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)