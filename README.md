# 🤖 Smart Summary Generator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

## 📌 Overview

An intelligent document summarization tool that uses AI to automatically generate concise summaries from long texts, PDFs, and Word documents.

## ✨ Features

- 📝 **Text Summarization** - Paste any text and get instant summary
- 📁 **File Upload** - Support for TXT, PDF, DOCX, MD files
- 📋 **Copy to Clipboard** - One-click copy functionality
- 💾 **Multiple Export Options** - TXT, PDF, DOCX formats
- 📊 **Real-time Statistics** - Compression ratio and length comparison
- 🎨 **Clean UI** - Modern gradient design with responsive layout

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python, Flask |
| AI Model | Hugging Face Transformers (T5-small) |
| File Processing | PyPDF2, python-docx |

## 📊 How It Works

1. **Input**: User provides text or uploads document
2. **Processing**: Backend extracts text and sends to AI model
3. **Summarization**: T5-small transformer generates concise summary
4. **Output**: Summary displayed with statistics and export options

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/rakshitalokapur466-max/document_Summarizer_project.git
cd document_Summarizer project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Run backend server
python app.py

# In new terminal, run frontend
cd ../frontend
python -m http.server 3000
