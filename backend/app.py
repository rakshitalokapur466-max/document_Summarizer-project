"""
AI Document Summarizer - Complete Working Backend
Location: D:\document-summarizer\backend\app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import sys
import os
import re
import tempfile
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow frontend to communicate

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Supported file types
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md'}

# Global summarizer
summarizer = None

# Try to import optional packages
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("⚠️ PyPDF2 not installed. PDF support disabled.")

try:
    from docx import Document
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False
    print("⚠️ python-docx not installed. DOCX support disabled.")

def allowed_file(filename):
    """Check if file type is supported"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path, file_extension):
    """Extract text from uploaded file"""
    text = ""
    
    try:
        if file_extension in ['txt', 'md']:
            # Handle text files
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        
        elif file_extension == 'pdf' and PDF_SUPPORT:
            # Handle PDF files
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        
        elif file_extension == 'docx' and DOCX_SUPPORT:
            # Handle DOCX files
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
        
        else:
            raise Exception(f"Unsupported file type: {file_extension}")
        
        return text.strip()
        
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")

def load_summarization_model():
    """Load the AI model"""
    global summarizer
    try:
        print("🔄 Loading AI model... (First time may take 2-5 minutes)")
        # Using t5-small for better compatibility with lower RAM
        summarizer = pipeline("summarization", model="t5-small", device=-1)
        print("✅ Model loaded successfully!")
        return summarizer
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        sys.exit(1)

def format_summary(text):
    """
    Improve summary formatting with proper capitalization
    and fix common brand names
    """
    if not text:
        return text
    
    # Capitalize first letter of each sentence
    sentences = re.split(r'(?<=[.!?])\s+', text)
    fixed_sentences = []
    for sentence in sentences:
        if sentence:
            sentence = sentence.strip()
            if len(sentence) > 1:
                sentence = sentence[0].upper() + sentence[1:]
            else:
                sentence = sentence.upper()
            fixed_sentences.append(sentence)
    
    # Join sentences back
    text = ' '.join(fixed_sentences)
    
    # Ensure ends with period
    if text and text[-1] not in '.!?':
        text += '.'
    
    # Fix common brand names and proper nouns (THIS IS THE NEW PART)
    text = re.sub(r'\bamazon\b', 'Amazon', text, flags=re.IGNORECASE)
    text = re.sub(r'\bnetflix\b', 'Netflix', text, flags=re.IGNORECASE)
    text = re.sub(r'\bsiri\b', 'Siri', text, flags=re.IGNORECASE)
    text = re.sub(r'\balexa\b', 'Alexa', text, flags=re.IGNORECASE)
    text = re.sub(r'\bai\b', 'AI', text, flags=re.IGNORECASE)
    text = re.sub(r'\bml\b', 'ML', text, flags=re.IGNORECASE)
    text = re.sub(r'\bapi\b', 'API', text, flags=re.IGNORECASE)
    
    return text

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": summarizer is not None,
        "server": "running",
        "pdf_support": PDF_SUPPORT,
        "docx_support": DOCX_SUPPORT
    })

@app.route('/summarize', methods=['POST', 'OPTIONS'])
def summarize_text():
    """Main summarization endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        text = ""
        
        # Check if file upload or text input
        if 'file' in request.files:
            # File upload
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            if not allowed_file(file.filename):
                return jsonify({"error": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
            
            # Save and process file
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)
            
            try:
                text = extract_text_from_file(temp_path, file_extension)
                os.remove(temp_path)
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return jsonify({"error": str(e)}), 400
        
        else:
            # Text input
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            text = data.get('text', '').strip()
        
        # Validate text
        if not text:
            return jsonify({"error": "No content to summarize"}), 400
        
        if len(text) < 30:
            return jsonify({"error": f"Text too short ({len(text)} chars). Minimum 30 characters required."}), 400
        
        print(f"📝 Processing {len(text)} characters")
        
        # Generate summary
        # Calculate appropriate summary length
        max_length = min(200, len(text) // 2)
        min_length = min(50, len(text) // 4)
        
        result = summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            num_beams=4,
            early_stopping=True
        )
        
        summary = result[0]['summary_text']
        summary = format_summary(summary)  # ← This now includes brand name fixes
        
        # Calculate statistics
        compression_ratio = (len(summary) / len(text)) * 100
        
        return jsonify({
            "success": True,
            "summary": summary,
            "stats": {
                "original_length": len(text),
                "summary_length": len(summary),
                "compression": f"{compression_ratio:.1f}%"
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        "name": "AI Document Summarizer API",
        "version": "3.0",
        "status": "running",
        "endpoints": {
            "POST /summarize": "Send text or file for summarization",
            "GET /health": "Check server health"
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 AI DOCUMENT SUMMARIZER - BACKEND SERVER")
    print("=" * 60)
    print(f"📍 Location: D:\\document-summarizer\\backend")
    print(f"📡 Server URL: http://127.0.0.1:5000")
    print("=" * 60)
    
    # Load the AI model
    load_summarization_model()
    
    print("\n" + "=" * 60)
    print("✅ SERVER READY!")
    print("=" * 60)
    print("🚀 Running on: http://127.0.0.1:5000")
    print("📊 Supported files: TXT, PDF, DOCX, MD")
    print(f"📄 PDF Support: {'✅' if PDF_SUPPORT else '❌'}")
    print(f"📄 DOCX Support: {'✅' if DOCX_SUPPORT else '❌'}")
    print("=" * 60)
    print("\n💡 Press CTRL+C to stop the server\n")
    
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)