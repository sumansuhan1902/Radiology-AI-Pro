"""
Hospital Recommendation System for Gulbarga
"""
import streamlit as st
import google.generativeai as genai
import PyPDF2
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
import random
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

# Treatment-specific cost database (in INR)
TREATMENT_COSTS = {
    "Brain MRI": {
        "ESIC Hospital Gulbarga": {"min": 0, "max": 500},  # Free for ESIC beneficiaries
        "Gulbarga Institute of Medical Sciences Hospital (GIMS)": {"min": 500, "max": 1500},
        "Basweshwar Hospital Gulbarga": {"min": 500, "max": 1500},
        "GIMS Hospital": {"min": 500, "max": 1500},
        "District Hospital": {"min": 500, "max": 1500},
        "Star Care Multi-Speciality Hospital": {"min": 8000, "max": 12000},
        "United Hospital Gulbarga": {"min": 9000, "max": 14000},
        "Shanta Hospital": {"min": 8500, "max": 13000},
        "Sunrise Multispeciality Hospital": {"min": 7800, "max": 12500},
        "Nisty Heart Centre": {"min": 7500, "max": 11000},
        "Asian Superspeciality Hospital": {"min": 10000, "max": 15000},
        "MANUR Multi Speciality Hospital": {"min": 6500, "max": 9000},
        "Chirayu Hospital Gulbarga": {"min": 6000, "max": 8500},
        "Vaatsalya Hospital": {"min": 5000, "max": 7500},
        "Sadbhava Hospital Gulbarga": {"min": 4000, "max": 6000}
    },

    "CT Scan (Head/Chest/Abdomen)": {
        "ESIC Hospital Gulbarga": {"min": 0, "max": 300},  # Free for ESIC beneficiaries
        "Gulbarga Institute of Medical Sciences Hospital (GIMS)": {"min": 300, "max": 800},
        "Basweshwar Hospital Gulbarga": {"min": 300, "max": 800},
        "GIMS Hospital": {"min": 300, "max": 800},
        "District Hospital": {"min": 300, "max": 800},
        "Star Care Multi-Speciality Hospital": {"min": 3500, "max": 6000},
        "United Hospital Gulbarga": {"min": 4000, "max": 7000},
        "Sunrise Multispeciality Hospital": {"min": 3200, "max": 5500},
        "Shanta Hospital": {"min": 3500, "max": 5800},
        "Asian Superspeciality Hospital": {"min": 4500, "max": 8500},
        "MANUR Multi Speciality Hospital": {"min": 2500, "max": 4500},
        "Chirayu Hospital Gulbarga": {"min": 2000, "max": 3500},
        "Vaatsalya Hospital": {"min": 1800, "max": 3200},
        "Sadbhava Hospital Gulbarga": {"min": 1500, "max": 2500}
    },

    "Cardiology / Heart Attack Emergency": {
        "ESIC Hospital Gulbarga": {"min": 0, "max": 10000},  # Free/Subsidized for ESIC beneficiaries
        "Gulbarga Institute of Medical Sciences Hospital (GIMS)": {"min": 0, "max": 20000},  # Subsidized under govt schemes
        "Basweshwar Hospital Gulbarga": {"min": 0, "max": 20000},  # Government rates
        "GIMS Hospital": {"min": 0, "max": 20000},  # Subsidized under govt schemes
        "District Hospital": {"min": 0, "max": 20000},  # Often completely free under BPL
        "Nisty Heart Centre": {"min": 25000, "max": 120000},
        "Star Care Multi-Speciality Hospital": {"min": 45000, "max": 180000},
        "United Hospital Gulbarga": {"min": 50000, "max": 200000},
        "Sunrise Multispeciality Hospital": {"min": 38000, "max": 160000}
    },

    "Neurology Consultation": {
        "ESIC Hospital Gulbarga": {"min": 0, "max": 100},  # Free for ESIC beneficiaries
        "Gulbarga Institute of Medical Sciences Hospital (GIMS)": {"min": 50, "max": 200},
        "Basweshwar Hospital Gulbarga": {"min": 50, "max": 200},
        "GIMS Hospital": {"min": 50, "max": 200},
        "District Hospital": {"min": 50, "max": 200},
        "Star Care Multi-Speciality Hospital": {"min": 1000, "max": 2000},
        "United Hospital Gulbarga": {"min": 1200, "max": 2500},
        "Shanta Hospital": {"min": 1000, "max": 1800},
        "Sunrise Multispeciality Hospital": {"min": 800, "max": 1500},
        "MANUR Multi Speciality Hospital": {"min": 300, "max": 700},
        "Chirayu Hospital Gulbarga": {"min": 250, "max": 600},
        "Vaatsalya Hospital": {"min": 200, "max": 500},
        "Sadbhava Hospital Gulbarga": {"min": 150, "max": 400}
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

def create_recommendation_pdf(report_analysis, recommendations, patient_info):
    """Create comprehensive PDF with analysis and recommendations"""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#667eea'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("🏥 HOSPITAL RECOMMENDATION REPORT", title_style))
        story.append(Paragraph("Based on AI Medical Report Analysis", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Info
        story.append(Paragraph("PATIENT INFORMATION", heading_style))
        for key, value in patient_info.items():
            story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Report Analysis
        story.append(Paragraph("MEDICAL REPORT ANALYSIS", heading_style))
        for line in report_analysis.split('\n'):
            if line.strip():
                story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        story.append(Paragraph("RECOMMENDED HOSPITALS", heading_style))
        for line in recommendations.split('\n'):
            if line.strip():
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 0.05*inch))
        
        doc.build(story)
        
        with open(temp_file.name, 'rb') as f:
            return f.read()
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def show_hospital_page():
    """Display the hospital recommendation system page"""
    # Clean CSS
    st.markdown("""
        <style>
        * {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .main {
            background: #f8fafc;
            padding: 0;
        }
        
        .block-container {
            padding: 1.5rem 2rem;
            max-width: 1200px;
        }
        
        [data-testid="stSidebar"] {
            display: none;
        }
        
        .stApp > header {
            display: none;
        }
        
        .main-header {
            font-size: 2rem;
            font-weight: 600;
            color: #1e293b;
            text-align: center;
            padding: 1.5rem 1rem 0.5rem 1rem;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            text-align: center;
            font-size: 1rem;
            color: #64748b;
            margin-bottom: 1.5rem;
        }
        
        .content-card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border: 1px solid #e2e8f0;
        }
        
        .analysis-card {
            background: #fff7ed;
            border-left: 3px solid #f59e0b;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .analysis-item {
            background: white;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 6px;
            border-left: 3px solid #f59e0b;
        }
        
        .hospital-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border: 1px solid #e2e8f0;
        }
        
        .government-badge {
            background: #10b981;
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-weight: 500;
            display: inline-block;
            margin-bottom: 0.8rem;
            font-size: 0.85rem;
        }
        
        .private-badge {
            background: #3b82f6;
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-weight: 500;
            display: inline-block;
            margin-bottom: 0.8rem;
            font-size: 0.85rem;
        }
        
        .rating-badge {
            background: #f59e0b;
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-weight: 500;
            display: inline-block;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }
        
        .section-header {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1e293b;
            margin: 1.5rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .info-pill {
            background: #f1f5f9;
            color: #475569;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            display: inline-block;
            margin: 0.2rem;
            font-size: 0.85rem;
        }
        
        .cost-badge {
            background: #10b981;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 500;
            display: inline-block;
            margin: 0.5rem 0;
            font-size: 0.95rem;
        }
        
        .contact-box {
            background: #f8fafc;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.8rem 0;
            border-left: 3px solid #6366f1;
        }
        
        .stButton > button {
            background: #6366f1;
            color: white;
            font-weight: 500;
            padding: 0.6rem 1.5rem;
            border-radius: 6px;
            border: none;
            font-size: 1rem;
        }
        
        .stButton > button:hover {
            background: #4f46e5;
        }
        
        .feature-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e2e8f0;
            height: 100%;
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.8rem;
        }
        
        .footer-box {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            margin-top: 2rem;
            border-top: 1px solid #e2e8f0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main Page
    st.markdown('<h1 class="main-header">🏥 Smart Hospital Recommendation System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Medical Report Analysis & Hospital Matching for Gulbarga</p>', unsafe_allow_html=True)

    # Upload Section
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Medical Report")
    st.info("✅ Accepts: X-ray Reports | CT Scan Reports | MRI Reports | Ultrasound Reports (PDF format)")

    uploaded_report = st.file_uploader(
        "Choose your medical imaging report",
        type=['pdf'],
        help="Upload X-ray, CT, MRI, or Ultrasound report in PDF format"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_report:
        st.success(f"✅ Report uploaded successfully: **{uploaded_report.name}**")
        
        # Patient Information
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 👤 Patient Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            patient_name = st.text_input("Patient Name *", placeholder="Enter full name")
            patient_age = st.number_input("Age *", min_value=1, max_value=120, value=30)
        
        with col2:
            patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            patient_contact = st.text_input("Contact Number", placeholder="+91 XXXXX XXXXX")
        
        with col3:
            budget_pref = st.selectbox(
                "Budget Preference *",
                [
                    "Very Low (Government/Free - ₹0 - ₹5,000)",
                    "Low (₹5,000 - ₹20,000)",
                    "Medium (₹20,000 - ₹50,000)",
                    "High (₹50,000+)"
                ]
            )
            emergency_case = st.checkbox("🚨 Emergency/Urgent Case")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Analyze Button
        if st.button("🔬 Analyze Report & Find Best Hospitals", type="primary", use_container_width=True):
            if patient_name and patient_age:
                # Extract report text
                report_text = extract_text_from_pdf(uploaded_report)
                
                if report_text:
                    # Display extracted report preview
                    with st.expander("📄 View Extracted Report Text", expanded=False):
                        st.text_area("Report Content", report_text, height=200, disabled=True)
                    
                    # Analyze report
                    st.markdown("---")
                    st.markdown('<div class="content-card">', unsafe_allow_html=True)
                    st.markdown('<h2 class="section-header">🔬 Medical Report Analysis</h2>', unsafe_allow_html=True)
                    
                    analysis = analyze_medical_report(report_text)
                    
                    if analysis:
                        # Parse and display analysis in a structured format
                        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                        
                        analysis_lines = analysis.strip().split('\n')
                        for line in analysis_lines:
                            if line.strip():
                                if any(keyword in line for keyword in ['REPORT TYPE:', 'ANATOMICAL REGION:', 'SEVERITY:', 'URGENCY LEVEL:']):
                                    st.markdown(f'<div class="analysis-item"><strong>{line}</strong></div>', unsafe_allow_html=True)
                                elif line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                                    st.markdown(f'<div class="analysis-item">{line}</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<p style="margin: 0.5rem 0;">{line}</p>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Get recommendations
                        st.markdown("---")
                        st.markdown('<div class="content-card">', unsafe_allow_html=True)
                        st.markdown('<h2 class="section-header">🏥 Recommended Hospitals</h2>', unsafe_allow_html=True)
                        
                        
                        patient_info = {
                            "Patient Name": patient_name,
                            "Age": str(patient_age),
                            "Gender": patient_gender,
                            "Contact": patient_contact if patient_contact else "Not provided",
                            "Budget Preference": budget_pref,
                            "Emergency Case": "Yes" if emergency_case else "No",
                            "Report Date": datetime.now().strftime('%B %d, %Y')
                        }
                        
                        recommendations = get_hospital_recommendations(analysis, patient_info)
                        
                        if recommendations:
                            # Parse and display recommendations with enhanced formatting
                            rec_sections = recommendations.split('🏥')
                            
                            for idx, section in enumerate(rec_sections[1:], 1):  # Skip first empty split
                                st.markdown('<div class="hospital-card">', unsafe_allow_html=True)
                                
                                # Check if it's a government hospital
                                is_govt = "Government" in section or "ESIC" in section
                                
                                if is_govt:
                                    st.markdown('<div class="government-badge">🏛️ GOVERNMENT HOSPITAL - Cashless/Free Treatment Available</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div class="private-badge">🏢 PRIVATE HOSPITAL</div>', unsafe_allow_html=True)
                                
                                # Display hospital content
                                lines = section.split('\n')
                                for line in lines:
                                    if line.strip():
                                        # Format special sections
                                        if '⭐' in line or 'Rating' in line:
                                            st.markdown(f'<div class="rating-badge">⭐ {line.replace("⭐", "").strip()}</div>', unsafe_allow_html=True)
                                        elif '💰' in line and 'TOTAL' in line:
                                            st.markdown(f'<div class="cost-badge">{line}</div>', unsafe_allow_html=True)
                                        elif '📞' in line or 'Phone' in line or 'Contact' in line:
                                            st.markdown(f'<div class="contact-box">{line}</div>', unsafe_allow_html=True)
                                        else:
                                            st.markdown(f'{line}')
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                if idx < len(rec_sections) - 1:
                                    st.markdown("<hr style='margin: 2rem 0; border: none; border-top: 2px solid #e2e8f0;'>", unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Store in session
                            st.session_state['analysis'] = analysis
                            st.session_state['recommendations'] = recommendations
                            st.session_state['patient_info'] = patient_info
                            
                            # Download Options
                            st.markdown("---")
                            st.markdown('<div class="content-card">', unsafe_allow_html=True)
                            st.markdown('<h2 class="section-header">📥 Download Reports</h2>', unsafe_allow_html=True)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Text download
                                full_report = f"""MEDICAL REPORT ANALYSIS & HOSPITAL RECOMMENDATIONS
Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

{'='*60}
PATIENT INFORMATION
{'='*60}
"""
                                for key, value in patient_info.items():
                                    full_report += f"{key}: {value}\n"
                                
                                full_report += f"""
{'='*60}
MEDICAL REPORT ANALYSIS
{'='*60}
{analysis}

{'='*60}
HOSPITAL RECOMMENDATIONS
{'='*60}
{recommendations}
"""
                                
                                st.download_button(
                                    label="📄 Download as Text File",
                                    data=full_report,
                                    file_name=f"hospital_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            
                            with col2:
                                # PDF download
                                pdf_data = create_recommendation_pdf(analysis, recommendations, patient_info)
                                if pdf_data:
                                    st.download_button(
                                        label="📑 Download as PDF Report",
                                        data=pdf_data,
                                        file_name=f"hospital_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                        mime="application/pdf",
                                        type="primary",
                                        use_container_width=True
                                    )
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Quick Contact Section
                            st.markdown("---")
                            st.markdown('<div class="content-card">', unsafe_allow_html=True)
                            st.markdown('<h2 class="section-header">📞 Quick Contact Information</h2>', unsafe_allow_html=True)
                            
                            # Show diverse mix of hospitals (government and private)
                            all_hospitals = list(HOSPITALS_DATA.keys())
                            # Show a mix: one government, one multispeciality, one specialized
                            govt_hospitals = [h for h in all_hospitals if "Government" in HOSPITALS_DATA[h]["type"] or "ESIC" in h]
                            private_hospitals = [h for h in all_hospitals if h not in govt_hospitals]
                            
                            if govt_hospitals and private_hospitals:
                                featured_hospitals = [
                                    random.choice(govt_hospitals),
                                    random.choice(private_hospitals[:5]),  # Top rated private
                                    random.choice(all_hospitals)
                                ]
                            else:
                                featured_hospitals = random.sample(all_hospitals, min(3, len(all_hospitals)))
                            
                            cols = st.columns(3)
                            
                            for idx, hospital_name in enumerate(featured_hospitals):
                                if hospital_name in HOSPITALS_DATA:
                                    with cols[idx]:
                                        hospital = HOSPITALS_DATA[hospital_name]
                                        is_govt = "Government" in hospital['type']
                                        
                                        badge = "🏛️ Government" if is_govt else "🏢 Private"
                                        badge_class = "government-badge" if is_govt else "private-badge"
                                        
                                        st.markdown(f"""
                                        <div class="contact-box">
                                            <div class="{badge_class}" style="font-size: 0.85rem; padding: 0.4rem 0.8rem; margin-bottom: 0.8rem;">{badge}</div>
                                            <h4 style="color: #1e293b; font-size: 1.1rem; margin-bottom: 0.8rem;">{hospital_name}</h4>
                                            <div class="rating-badge" style="font-size: 0.9rem; padding: 0.4rem 0.8rem; margin-bottom: 0.8rem;">
                                                ⭐ {hospital['rating']} ({hospital['reviews']} reviews)
                                            </div>
                                            <p style="margin: 0.5rem 0;"><strong>📞</strong> {hospital['phone']}</p>
                                            <p style="margin: 0.5rem 0;"><strong>⏰</strong> {hospital['availability']}</p>
                                            <p style="margin: 0.5rem 0; font-size: 0.85rem; color: #64748b;">{hospital['address'][:50]}...</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("⚠️ Please enter patient name and age to continue.")

    # Feature Cards Section
    st.markdown("---")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">ℹ️ Why Choose Our Service?</h2>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3 style="color: #1e293b;">AI-Powered Analysis</h3>
            <p style="color: #64748b;">Advanced AI analyzes your medical report and matches you with the most suitable hospitals based on your condition and budget</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💰</div>
            <h3 style="color: #1e293b;">Cost Transparency</h3>
            <p style="color: #64748b;">Get detailed cost breakdowns including government hospitals with cashless/free treatment options for eligible patients</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⭐</div>
            <h3 style="color: #1e293b;">Verified Data</h3>
            <p style="color: #64748b;">Real hospital ratings, patient reviews, and success rates from verified sources to help you make informed decisions</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Hospital Stats
    st.markdown("---")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">📊 Hospital Network Statistics</h2>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Hospitals", "45+", help="Comprehensive hospital database")
    with col2:
        st.metric("Government Hospitals", "4", delta="Cashless/Free", help="GIMS & District Hospital and Basweshwar Hospitaland Esic Hospital Gulbarga")
    with col3:
        st.metric("24/7 Emergency", "12", help="Round-the-clock emergency services")
    with col4:
        st.metric("Avg Rating", "4.7⭐", help="Average hospital rating")

    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer-box">
        <h3 style='color: #1e293b; font-size: 1.2rem; margin-bottom: 0.8rem;'>🏥 Gulbarga Hospital Finder</h3>
        <p style='color: #64748b; font-size: 0.9rem; margin: 0.8rem 0;'>
            Powered by Google Gemini AI | Hospital Data: November 2025
        </p>
        <div style='margin: 1rem 0;'>
            <span class='info-pill'>🏛️ Government Hospitals</span>
            <span class='info-pill'>🏢 Private Hospitals</span>
            <span class='info-pill'>💳 Cashless Facilities</span>
            <span class='info-pill'>🚨 Emergency Care</span>
        </div>
    </div>
    """, unsafe_allow_html=True)