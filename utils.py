import streamlit as st
from PIL import Image
import google.generativeai as genai
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
import tempfile
import time
import random
import re

def _normalize_model_name(model_name):
    """Normalize model names returned by API (models/xxx -> xxx)."""
    return model_name.replace("models/", "").strip()

def _list_generate_content_models(preferred_model=None):
    """
    Discover all Gemini models that support generateContent.
    Falls back to a curated list if listing is unavailable.
    """
    discovered = []
    try:
        for model in genai.list_models():
            name = getattr(model, "name", "")
            methods = getattr(model, "supported_generation_methods", []) or []
            if name and name.startswith("models/gemini") and "generateContent" in methods:
                discovered.append(_normalize_model_name(name))
    except Exception:
        # Fallback when model listing API is unavailable.
        discovered = []

    fallback = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-flash-latest",
        "gemini-pro-latest",
    ]

    models_to_try = []
    if preferred_model:
        models_to_try.append(preferred_model)
    models_to_try.extend(discovered if discovered else fallback)

    # Remove duplicates while preserving order.
    seen = set()
    return [m for m in models_to_try if m and not (m in seen or seen.add(m))]

def _classify_error(error):
    msg = str(error).lower()
    if "api key was reported as leaked" in msg or "api key not valid" in msg or "permission denied" in msg or "403" in msg:
        return "auth"
    if "quota exceeded" in msg or "429" in msg or "resource exhausted" in msg:
        return "quota"
    if "internal" in msg or "overloaded" in msg or "500" in msg or "503" in msg:
        return "transient"
    return "other"

def _generate_with_models(prompt_payload, max_retries=3, base_delay=2, model_name="gemini-2.0-flash-lite"):
    """Shared retry/fallback engine for image and text prompts."""
    available_models = _list_generate_content_models(preferred_model=model_name)
    last_error = None

    for current_model_name in available_models:
        try:
            model = genai.GenerativeModel(current_model_name)
        except Exception:
            continue

        for attempt in range(max_retries + 1):
            try:
                response = model.generate_content(prompt_payload)
                if getattr(response, "text", None):
                    return response.text
            except Exception as e:
                last_error = e
                error_type = _classify_error(e)

                if error_type == "auth":
                    st.error(
                        "Gemini API authentication failed (invalid or leaked key). "
                        "Set a fresh key in GEMINI_API_KEY and restart the app."
                    )
                    return None

                if error_type in ("quota", "transient"):
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(delay)
                        continue
                    break

                break

    if last_error:
        if _classify_error(last_error) == "quota":
            st.error(
                "Failed after trying available Gemini models. Quota/rate limit reached. "
                "Please check Gemini billing/limits and try again."
            )
        else:
            st.error(f"Failed to generate report after trying available Gemini models. Last error: {str(last_error)}")
    else:
        st.error("Failed to generate report: no compatible Gemini model was available.")
    return None

def process_image(uploaded_file):
    """Process uploaded image file"""
    try:
        image = Image.open(uploaded_file)
        return image
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def generate_report_with_retry(image, prompt, max_retries=3, base_delay=2, model_name='gemini-2.0-flash-lite'):
    """Generate report with retry mechanism and model fallback"""
    # Convert image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    payload = [prompt, {'mime_type': 'image/png', 'data': img_byte_arr}]
    return _generate_with_models(
        payload,
        max_retries=max_retries,
        base_delay=base_delay,
        model_name=model_name,
    )

def generate_text_report_with_retry(prompt, max_retries=3, base_delay=2, model_name='gemini-2.0-flash-lite'):
    """Generate text-based report with retry mechanism and model fallback"""
    return _generate_with_models(
        prompt,
        max_retries=max_retries,
        base_delay=base_delay,
        model_name=model_name,
    )

def generate_report(image, prompt):
    """Generate report using Gemini API with retry mechanism (backward compatibility)"""
    return generate_report_with_retry(image, prompt)

def _clean_markdown_inline(text):
    """Convert common markdown inline syntax to ReportLab-friendly tags."""
    if not text:
        return ""
    cleaned = text.strip()
    # Bold: **text** -> <b>text</b>
    cleaned = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", cleaned)
    # Italic: *text* -> <i>text</i> (only simple cases)
    cleaned = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", cleaned)
    # Inline code: `text` -> plain text (monospace unsupported in base styles)
    cleaned = re.sub(r"`(.+?)`", r"\1", cleaned)
    return cleaned


def _markdown_like_to_story(story, analysis_text, styles_map):
    """
    Convert markdown-like AI output into better structured PDF blocks.
    Supports:
    - # / ## / ### headings
    - bullet lists (-, *, •)
    - numbered points (1. ...)
    - key-value lines (KEY: value)
    - plain paragraphs
    """
    if not analysis_text:
        story.append(Paragraph("No analysis content available.", styles_map["body"]))
        return

    lines = analysis_text.replace("\r\n", "\n").split("\n")
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 0.07 * inch))
            continue

        # Markdown headings
        if line.startswith("### "):
            story.append(Paragraph(_clean_markdown_inline(line[4:]), styles_map["h3"]))
            continue
        if line.startswith("## "):
            story.append(Paragraph(_clean_markdown_inline(line[3:]), styles_map["h2"]))
            continue
        if line.startswith("# "):
            story.append(Paragraph(_clean_markdown_inline(line[2:]), styles_map["h1"]))
            continue

        # Bullet points
        bullet_match = re.match(r"^[-*•]\s+(.+)$", line)
        if bullet_match:
            bullet_text = _clean_markdown_inline(bullet_match.group(1))
            story.append(Paragraph(f"&bull; {bullet_text}", styles_map["bullet"]))
            continue

        # Numbered lists
        number_match = re.match(r"^(\d+)[\.\)]\s+(.+)$", line)
        if number_match:
            idx, item_text = number_match.groups()
            story.append(Paragraph(f"<b>{idx}.</b> {_clean_markdown_inline(item_text)}", styles_map["bullet"]))
            continue

        # KEY: value formatting
        kv_match = re.match(r"^([A-Za-z0-9 /()_-]{2,}):\s*(.+)$", line)
        if kv_match:
            key, value = kv_match.groups()
            story.append(Paragraph(f"<b>{_clean_markdown_inline(key)}:</b> {_clean_markdown_inline(value)}", styles_map["body"]))
            continue

        # Default paragraph
        story.append(Paragraph(_clean_markdown_inline(line), styles_map["body"]))


def create_pdf_report(analysis_text, image=None, report_type="Medical Report", patient_info=None):
    """Create a polished, structured PDF report from AI analysis text."""
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
        # Create document
        doc = SimpleDocTemplate(
            temp_file.name,
            pagesize=A4,
            leftMargin=0.65 * inch,
            rightMargin=0.65 * inch,
            topMargin=0.65 * inch,
            bottomMargin=0.65 * inch
        )
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=HexColor('#0f172a'),
            spaceAfter=14,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#1d4ed8'),
            spaceAfter=8,
            spaceBefore=10
        )

        sub_heading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=HexColor('#334155'),
            spaceAfter=6,
            spaceBefore=8
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10.5,
            leading=15,
            textColor=HexColor('#111827'),
            alignment=TA_LEFT
        )

        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=body_style,
            leftIndent=12,
            spaceBefore=1,
            spaceAfter=2
        )

        muted_style = ParagraphStyle(
            'MutedText',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor('#475569'),
            alignment=TA_CENTER
        )
        
        # Title
        story.append(Paragraph(report_type, title_style))
        story.append(Paragraph("AI-Powered Medical Analysis Report", muted_style))
        story.append(Spacer(1, 0.20 * inch))
        
        # Patient Information
        if patient_info:
            story.append(Paragraph("Patient Information", heading_style))
            for key, value in patient_info.items():
                story.append(Paragraph(f"<b>{key}:</b> {_clean_markdown_inline(str(value))}", body_style))
            story.append(Spacer(1, 0.12 * inch))
        
        # Timestamp
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", muted_style))
        story.append(Spacer(1, 0.20 * inch))
        
        # Image (if provided)
        if image:
            # Save image to temporary file
            img_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(img_temp.name, 'PNG')
            
            # Add image to PDF
            story.append(Paragraph("Medical Image", heading_style))
            img = RLImage(img_temp.name, width=4*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 0.20 * inch))
        
        # Analysis
        story.append(Paragraph("AI Analysis Results", heading_style))

        style_map = {
            "h1": heading_style,
            "h2": heading_style,
            "h3": sub_heading_style,
            "body": body_style,
            "bullet": bullet_style,
        }
        _markdown_like_to_story(story, analysis_text, style_map)
        
        # Build PDF
        doc.build(story)
        
        # Read the PDF content
        with open(temp_file.name, 'rb') as f:
            pdf_data = f.read()
        
        return pdf_data
        
    except Exception as e:
        st.error(f"Error creating PDF report: {str(e)}")
        return None