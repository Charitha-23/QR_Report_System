
QR Division Digital Report Management System

An AI-powered document repository and report intelligence system designed to digitize, organize, and search technical reports. The system allows users to upload documents, extract text using OCR, generate AI summaries, and search reports through a centralized digital platform.

This project was developed as part of a capstone system for the QR Division (NSTL) to modernize document storage and improve report retrieval.

⸻

Project Features

Document Upload

Users can upload reports with required metadata including:
	•	Document ID
	•	Report Name
	•	Report Type
	•	Prepared By
	•	Report Date
	•	File Attachment

Supported file types:
	•	PDF
	•	DOCX
	•	TXT
	•	PPTX
	•	JPG
	•	PNG

⸻

OCR Text Extraction

The system automatically extracts text from documents:
	•	Direct text extraction for digital PDFs
	•	OCR processing for scanned PDFs and images
	•	Supports multiple document formats

OCR is implemented using Tesseract OCR.

⸻

AI Report Summarization

Once text is extracted, the system generates a short AI summary using a transformer-based summarization model.

Model used:

sshleifer/distilbart-cnn-12-6

The summarization pipeline:
	1.	Extract document text
	2.	Clean and preprocess text
	3.	Split large documents into chunks
	4.	Generate partial summaries
	5.	Combine summaries into a final report summary

⸻

Intelligent Report Search

Users can search reports using keywords.

Search is performed on:
	•	Report name
	•	Extracted OCR text

Search results display:
	•	Report title
	•	AI-generated summary
	•	Button to open the report

⸻

Dashboard Report Management

The dashboard provides an overview of all reports in the system.

Features include:
	•	List of all uploaded reports
	•	Short AI summaries
	•	View full summary
	•	Open report file
	•	Delete report

Statistics displayed:
	•	Total reports
	•	Reports with AI summaries

⸻

Responsive User Interface

The frontend is designed to be simple and responsive using:
	•	HTML
	•	CSS
	•	Bootstrap
	•	JavaScript

Key UI features:
	•	Upload form with validation
	•	Enter-key search functionality
	•	Summary preview
	•	Modal for viewing full report summaries
	•	Dashboard report table

⸻

System Architecture

Frontend
   |
   | (HTTP Requests)
   |
Flask Backend
   |
   |---- OCR Service (Tesseract)
   |---- AI Summarization (Transformers)
   |
MongoDB Database
   |
File Storage (Uploads Folder)


⸻

Tech Stack

Frontend
	•	HTML
	•	CSS
	•	Bootstrap
	•	JavaScript

Backend
	•	Python
	•	Flask

AI & NLP
	•	HuggingFace Transformers
	•	DistilBART Summarization Model

OCR
	•	Tesseract OCR
	•	pdf2image

Database
	•	MongoDB

File Handling
	•	PyPDF2
	•	python-docx
	•	python-pptx

⸻

Project Structure

QR_Report_System
│
├── app.py
├── config.py
│
├── routes
│   ├── report_routes.py
│   └── auth_routes.py
│
├── services
│   ├── ai_service.py
│   ├── ocr_service.py
│   └── storage_service.py
│
├── models
│   └── report_model.py
│
├── static
│   ├── css
│   │   └── style.css
│   └── js
│       └── main.js
│
├── templates
│   ├── dashboard.html
│   ├── upload.html
│   └── search.html
│
└── uploads
    └── reports


⸻

Installation & Setup

1. Clone Repository

git clone https://github.com/yourusername/qr-report-system.git
cd qr-report-system


⸻

2. Create Virtual Environment

python -m venv venv

Activate:

Windows

venv\Scripts\activate

Mac/Linux

source venv/bin/activate


⸻

3. Install Dependencies

pip install flask pymongo transformers torch pytesseract pdf2image pillow PyPDF2 python-docx python-pptx


⸻

4. Install Tesseract OCR

Download:

https://github.com/tesseract-ocr/tesseract

Set the path in ocr_service.py.

⸻

5. Install Poppler (for PDF OCR)

Download Poppler and update the path inside ocr_service.py.

⸻

6. Start MongoDB

Ensure MongoDB is running locally:

mongodb://localhost:27017


⸻

7. Run Application

python app.py

Open in browser:

http://127.0.0.1:5000


⸻

Example Workflow
	1.	Upload a report
	2.	System extracts text using OCR
	3.	AI generates a summary
	4.	Report is stored in MongoDB
	5.	User can search and retrieve reports
	6.	Dashboard displays all reports and summaries

⸻

Future Improvements

Potential upgrades include:
	•	Semantic search using embeddings
	•	Vector database for AI document retrieval
	•	Document chat interface
	•	Role-based authentication
	•	Advanced analytics dashboard

⸻

Author

Developed as part of a Digital Repository & AI Report Intelligence System project.

