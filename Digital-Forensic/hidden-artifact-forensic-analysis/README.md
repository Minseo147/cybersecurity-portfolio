# 🔍 Digital Forensics CTF - Hidden Artifact Investigation

This project demonstrates a systematic digital forensic analysis
to identify hidden artifacts across multiple file formats.

The analysis was performed in a CLI-based environment (Kali Linux),
focusing on uncovering concealed data such as embedded strings,
encoded content, metadata artifacts, and file carving remnants.

---

## 📌 1. Project Overview

The objective of this project is to simulate real-world forensic workflows
by identifying hidden flags (ANS{...}) from various file types including:

- Text files
- Executables (EXE)
- Images (PNG, JPEG)
- Android APK files

Each challenge demonstrates a different forensic technique.

---

## 🧪 2. Analysis Techniques

- String extraction (`strings`, `grep`)
- File signature analysis (`hexdump`)
- File carving (`dd`)
- Metadata analysis (`exiftool`)
- APK static analysis (`jadx`)
- Encoding/decoding (Base64)

---

## 📊 3. Investigation Workflow

### Challenge 1 - Hidden Text Analysis
- Extracted hidden strings using `grep`

### Challenge 2 - File Carving from Executable
- Identified PNG signature in binary
- Extracted embedded image using `dd`

### Challenge 3 - APK Static Analysis
- Decompiled APK using `jadx`
- Located encoded data in XML resources
- Decoded Base64 content

### Challenge 4 - Metadata Analysis
- Identified hidden flag in EXIF metadata

### Challenge 5 - Image String Analysis
- Extracted hidden flag using `strings`

---

## 📁 4. Project Structure
```text
project1-hidden-artifacts/
│
├── evidence/
│ ├── fig01-grep-hidden-flag-text.png
│ ├── fig02-strings-analysis-exe.png
│ ├── fig03-hexdump-png-signature.png
│ ├── fig04-file-carving-dd-extraction.png
│ ├── fig05-extracted-png-verification.png
│ ├── fig06-extracted-image-output.png
│ ├── fig07-jadx-decompile-apk.png
│ ├── fig08-resource-directory-analysis.png
│ ├── fig09-encoded-string-discovery.png
│ ├── fig10-base64-decoding-result.png
│ ├── fig11-exiftool-metadata-analysis.png
│ ├── fig12-strings-analysis-png.png
│ └── fig13-hidden-flag-output.png
│
├── report/
│ └── 은닉 아티팩트 디지털 포렌식 분석 보고서.pdf
│
└── README.md
```

---

## 🔍 5. Key Findings

- Hidden data can exist in multiple layers (file content, metadata, encoding)
- File carving is effective for extracting embedded objects
- APK resources often contain encoded sensitive data
- Metadata fields may contain critical hidden artifacts

---

## 🛠 6. Tools Used

- Kali Linux
- strings
- grep
- hexdump
- dd
- exiftool
- jadx
- base64

---

## 🚀 7. Author Note

This project was conducted as part of a digital forensics study,
demonstrating practical investigation techniques used in real-world scenarios.
