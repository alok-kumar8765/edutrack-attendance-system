# 🏫 EduTrack - Principal Attendance Management System

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Built--in-003B57.svg?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![GitHub Profile](https://img.shields.io/badge/GitHub-alok--kumar8765-181717.svg?style=flat-square&logo=github)](https://github.com/alok-kumar8765)

---

## 📌 Description

**EduTrack** is an all-in-one, local-first **Teacher Attendance and Leave Management System** built for school and college Principals/Administrators. Developed using **Python**, **Streamlit**, and **SQLite**, the app automates daily attendance marking, late arrival deductions, monthly casual leave (CL) tracking, and administrative reporting. 

The system operates with zero external database server setup, relying on local storage to ensure privacy, speed, and reliability.

---

## 📜 Table of Contents

1. [Key Features](#-key-features)
2. [Institutional Policy Rules Engine](#-institutional-policy-rules-engine)
3. [System Architecture & Diagrams](#-system-architecture--diagrams)
   - [File Structure Diagram](#1-file-structure-diagram)
   - [Entity-Relationship (ER) Diagram](#2-entity-relationship-er-diagram)
   - [Data Flow Diagram (DFD Level 1)](#3-data-flow-diagram-dfd-level-1)
4. [Prerequisites & Requirements](#-prerequisites--requirements)
5. [Installation & Setup Guide](#-installation--setup-guide)
6. [User Manual](#-user-manual)
7. [Pros, Cons & Limitations](#-pros-cons--limitations)
8. [Known Issues & Vulnerabilities](#-known-issues--vulnerabilities)
9. [Future Roadmap & Updates](#-future-roadmap--updates)
10. [Contributing & Starring](#-contributing--starring)
11. [License & Contact](#-license--contact)

---

## ✨ Key Features

- 🔐 **Principal Authentication:** Secure login using Username, Email, or Phone Number with SHA-256 password hashing and security question recovery.
- 👨‍🏫 **Full Teacher Lifecycle Management (CRUD):** Add, update, view, disable, or delete teacher records across departments (CS/IT, Mechanical, Civil, Electrical, etc.).
- 📅 **Interactive Daily Roster:** Mark daily attendance (`Present`, `Late`, `Absent`, `On Leave`, `Half Day`) with auto-late flagging based on arrival times.
- 🧮 **Automated Leave & Late Rule Calculations:** Real-time computation of monthly Casual Leaves (CL), late penalties, and unpaid unexcused absences.
- 📈 **Visual Analytics Dashboard:** Interactive pie and bar charts powered by Plotly for daily, monthly, and department-wise attendance.
- 📥 **Exportable Reports:** Download categorized performance and master monthly summary reports in standard `.csv` format.
- 🔒 **100% Local Data Storage:** Built using Python's native SQLite engine requiring zero configuration.

---

## ⚙️ Institutional Policy Rules Engine

The software enforces institutional operational policies automatically:

| Rule Metric | Standard Policy Value |
| :--- | :--- |
| **Official Working Hours** | `09:15 AM` to `04:00 PM` |
| **Late Arrival Benchmark** | Arrival after `09:15 AM` is automatically logged as **Late** |
| **Late Penalty Rule** | **3 Late Arrivals = 1 Day Leave Deduction** |
| **Casual Leave (CL) Quota** | **1 Earned CL per month** |
| **Unpaid Leaves** | Excused absences exceeding monthly CL balance are flagged as Unpaid |

---

## 📐 System Architecture & Diagrams

### 1. File Structure Diagram

```text
edutrack-attendance-system/
│
├── app.py                      # Main Streamlit application source code
├── attendance_system.db        # Auto-generated local SQLite database file
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── assets/                     # UI screenshots and documentation static files
```

---

### 2. Entity-Relationship (ER) Diagram

```text
+-----------------------------------+         +-----------------------------------+
|            PRINCIPALS             |         |             TEACHERS              |
+-----------------------------------+         +-----------------------------------+
| PK | id                 (INT)     |         | PK | id                 (INT)     |
|    | username           (TEXT, U) |         | UK | emp_id             (TEXT, U) |
|    | email              (TEXT, U) |         |    | full_name          (TEXT)    |
|    | phone              (TEXT, U) |         |    | department         (TEXT)    |
|    | password           (TEXT)    |         | UK | email              (TEXT, U) |
|    | full_name          (TEXT)    |         |    | phone              (TEXT)    |
|    | security_question  (TEXT)    |         |    | joining_date       (DATE)    |
|    | security_answer    (TEXT)    |         |    | previous_job       (TEXT)    |
+-----------------------------------+         |    | salary             (REAL)    |
                                              |    | address            (TEXT)    |
                                              |    | photo_url          (TEXT)    |
                                              |    | status             (TEXT)    |
                                              +-----------------------------------+
                                                                | 1
                                                                |
                                                                | N (One-to-Many)
                                              +-----------------------------------+
                                              |            ATTENDANCE             |
                                              +-----------------------------------+
                                              | PK | id                 (INT)     |
                                              | FK | emp_id             (TEXT)    |
                                              |    | date               (DATE)    |
                                              |    | in_time            (TIME)    |
                                              |    | out_time           (TIME)    |
                                              |    | status             (TEXT)    |
                                              |    | notes              (TEXT)    |
                                              +-----------------------------------+
```

---

### 3. Data Flow Diagram (DFD Level 1)

```text
                     +-----------------------------------+
                     |         Principal / Admin         |
                     +-----------------------------------+
                       /               |               \
        1. Login / Creds              /                 \  3. Mark Daily Attendance
                      v              /                   v
           +--------------------+   /        +--------------------+
           |  1.0 Authentication|  /         |   3.0 Attendance   |
           |     Management     | /          |     Processing     |
           +--------------------+/           +--------------------+
                     |          /                      |
                     v         v                       v
            +----------------------+         +--------------------+
            |   2.0 Teacher CRUD   |         |  4.0 Rule Engine   |
            |     Management       |         |   (CL & Late Calc) |
            +----------------------+         +--------------------+
                     |                                 |
                     +-----------------+---------------+
                                       |
                                       v
                           +------------------------+
                           |    SQLite Database     |
                           | (attendance_system.db) |
                           +------------------------+
                                       |
                                       v
                           +------------------------+
                           | 5.0 Report & Analytics |
                           |       Generation       |
                           +------------------------+
```

---

## 📋 Prerequisites & Requirements

Ensure you have Python installed on your local machine:
- **Python Version:** Python `3.9` or higher.
- **Operating System:** Windows, macOS, or Linux.
- **Database Engine:** SQLite3 *(Included natively in standard Python distributions — no separate installation needed!)*.

### `requirements.txt`
```text
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
```

---

## 🚀 Installation & Setup Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/alok-kumar8765/edutrack-attendance-system.git
cd edutrack-attendance-system
```

### Step 2: Create a Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Streamlit Application
```bash
streamlit run app.py
```
The application will automatically launch in your default web browser at `http://localhost:8501`.

---

## 📖 User Manual

### 🔑 Default Credentials
Upon initial run, the application auto-populates a default Principal account and sample teacher data:
- **Username:** `admin`
- **Password:** `admin123`
- **Security Answer:** `london` *(Question: What city were you born in?)*

> **Security Tip:** It is strongly recommended to update the default password immediately via **⚙️ Principal Profile & Security** after logging in.

---

### 📍 App Workflow Guide

1. **Logging In:** Use your Username, Email, or Phone number alongside your password.
2. **Marking Attendance:**
   - Navigate to **📅 Daily Attendance Sheet**.
   - Select the date, update teacher arrival/departure times, and click **Save Attendance Sheet**.
   - Times logged after `09:15 AM` are automatically converted to `Late` status.
3. **Managing Faculty:**
   - Open **👨‍🏫 Teacher Management**.
   - Use tabs to add new teachers, search existing records, or toggle active/disabled states.
4. **Inspecting Profiles & Leave Audits:**
   - Go to **🔍 Detailed Teacher Profiles**.
   - View complete teacher details, current CL balance, accumulated late streaks, and visual pie charts.
5. **Exporting Monthly Reports:**
   - Go to **📈 Institutional Reports**.
   - Pick the month and year to view 100% attendance achievers, late rule offenders, and export raw CSV files.

---

## ⚖️ Pros, Cons & Limitations

### ✅ Advantages (Pros)
- **Zero Configuration:** Native SQLite database requires no database server configuration or administration.
- **Local Data Privacy:** All teacher records, salaries, and attendance records stay entirely on your local machine.
- **Automated Rules:** Eliminates manual errors when calculating late penalties and monthly leave allowances.
- **Fast UI:** Reactive Streamlit layout built for single-screen efficiency.

### ⚠️ Limitations (Cons)
- **Single-Machine Focus:** Designed primarily for single-user (Principal) local administration.
- **No Concurrent Multi-User Access:** SQLite may lock if multiple admins write to the file simultaneously.
- **Manual Data Entry:** Requires the Principal or staff to manually check-in teachers or input times (no biometric hardware sync out-of-the-box).

---

## 🐛 Known Bugs & Vulnerabilities

| Category | Description | Severity | Workaround / Mitigation |
| :--- | :--- | :--- | :--- |
| **Concurrency** | SQLite database file locking occurs during high-frequency simultaneous writes. | Low | App is optimized for single-user Principal operation. |
| **Authentication** | Passwords hashed using SHA-256 without salt. | Medium | Adequate for local applications; plan to add `bcrypt` salt in future releases. |

---

## 🔮 Future Roadmap & Updates

- [ ] **Biometric & QR Code Integration:** Direct integration with RFID/Biometric scanners for automated self-check-in.
- [ ] **Email Notifications:** Automatic email alerts sent to teachers when late penalties or leave deductions occur.
- [ ] **Multi-Role Access:** Dedicated login portals for Teachers to view their personal attendance logs and request leaves online.
- [ ] **PDF Payslip & Attendance Certificate Generator:** Generate downloadable PDF reports with institutional letterheads.

---

## ⭐ Support & Contributions

Contributions, bug reports, and feature suggestions are welcome! 

### How to Contribute
1. **Fork** the Repository.
2. Create a Feature Branch (`git checkout -b feature/AmazingFeature`).
3. **Commit** your Changes (`git commit -m 'Add some AmazingFeature'`).
4. **Push** to the Branch (`git push origin feature/AmazingFeature`).
5. Open a **Pull Request**.

If you found this project helpful, please consider giving it a ⭐ **Star** on GitHub!

---

## 👤 Author & Maintainer

Developed with ❤️ by **Alok Kumar**

- **GitHub:** [@alok-kumar8765](https://github.com/alok-kumar8765)

---

## 📄 License

This project is open-source software licensed under the **[MIT License](LICENSE)**.