# 🔍 Windows OS Forensic Analysis

This project presents a structured digital forensic investigation
of a Windows system disk image to identify system activity,
user behavior, and potential security risks.

The analysis was conducted using Autopsy in a controlled environment,
focusing on system artifacts such as registry data, user accounts,
installed programs, and web activity.

---

## 📌 1. Project Overview

The objective of this project is to simulate a real-world forensic investigation
by analyzing a seized laptop disk image (E01 format) and reconstructing:

- Operating system installation history
- User account activity and security posture
- Program installation behavior
- Web browsing and search activity

This project emphasizes both **technical analysis** and **behavioral interpretation**.

---

## 🧪 2. Analysis Scope

- Disk Image Format: EnCase (E01)
- Analysis Tool: Autopsy 4.22.0
- Environment: Windows 11 (UTM Virtual Machine)
- Method: Static forensic analysis (artifact-based)

---

## 📊 3. Investigation Workflow

### 1. Evidence Loading & Integrity Check
- Loaded E01 image in read-only mode
- Verified MD5 hash consistency

### 2. Operating System Analysis
- Identified current OS using registry (SOFTWARE hive)
- Determined initial installation via SYSTEM hive timestamps
- Confirmed OS upgrade using Windows.old directory

### 3. User Account Analysis
- Extracted active user accounts from OS Accounts artifact
- Analyzed login count, account creation time, and privileges
- Evaluated password security configuration

### 4. Installed Programs Analysis
- Identified OS installation time using BuildLabEx
- Extracted programs installed within 48 hours
- Distinguished system initialization artifacts vs user-installed apps

### 5. Web Activity Analysis
- Extracted Web History and Search artifacts
- Filtered activity within specific time window (09:00–18:00 PST)
- Analyzed domains, search keywords, and user intent

---

## 📁 4. Project Structure
```text
windows-os-forensic-analysis/
│
├── report/
│ └── Windows 시스템 디지털 포렌식 분석 보고서.pdf
│
├── evidence/
│ ├── fig01_hash.png
│ ├── fig02_system_registry_creation_timestamp.png
│ ├── fig03_software_hive_windows10_home.png
│ ├── fig04_current_build_number_windows11_22543.png
│ ├── fig05_current_version_registry_value.png
│ ├── fig06_patrick_1.png
│ ├── fig06_patrick_2.png
│ ├── fig07_minecraftsteve_1.png
│ ├── fig07_minecraftsteve_2.png
│ ├── fig08_buildlabex_registry.png
│ ├── fig09_installed_programs_1.png
│ ├── fig09_installed_programs_2.png
│ ├── fig10_web_history_autopsy.png
│ ├── fig11_web_search_autopsy.png
│ ├── fig12_web_history_csv-overview.png
│ └── fig13_web_activity_time_filter.png
│
└── README.md
```
---

### 🔍 5. Key Findings
- The system was initially installed with Windows 10 and later upgraded to Windows 11
- Evidence integrity showed inconsistency (MD5 mismatch), indicating potential acquisition issues
- A primary user account was identified with weak security configurations
- Installed programs were mostly OS initialization components
- Web activity revealed user concern regarding potential system compromise

---

### 🔨 6. Tools Used
- Autopsy 4.22.0
- Windows Registry Analysis
- Excel (data filtering using HOUR function)
- UTM Virtual Machine
- Windows 11 Environment

---

### 🚀 7. Author Note

This project demonstrates a practical digital forensic workflow
from evidence verification to behavioral analysis.

It highlights the importance of not only extracting artifacts,
but also interpreting their meaning in a security context.

The analysis reflects a reproducible and structured approach
aligned with real-world forensic investigation practices.
