import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, time, timedelta
import hashlib
import io
import base64

# ==========================================================
# PAGE CONFIGURATION & MODERN STYLING
# ==========================================================
st.set_page_config(
    page_title="EduTrack - Attendance & Staff Management",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphism & High-Contrast Modern Dashboard Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main {
        background-color: #f8fafc;
    }
    
    /* Header Card */
    .app-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
    }
    
    .app-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    .app-header p {
        margin: 6px 0 0 0;
        color: #94a3b8;
        font-size: 0.95rem;
    }

    /* Metric Cards */
    .metric-box {
        background: white;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.2s ease-in-out;
    }
    
    /* Custom Badges */
    .status-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-active { background-color: #dcfce7; color: #15803d; }
    .badge-disabled { background-color: #f1f5f9; color: #64748b; }
    
    /* Streamlit Tab Fixes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
        border-color: #2563eb !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================
DB_FILE = "attendance_system.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Principals Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS principals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        security_question TEXT,
        security_answer TEXT
    )
    ''')
    
    # 2. Teachers Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        department TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        joining_date DATE NOT NULL,
        previous_job TEXT,
        salary REAL,
        address TEXT,
        photo_url TEXT,
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 3. Attendance Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT NOT NULL,
        date DATE NOT NULL,
        in_time TIME,
        out_time TIME,
        status TEXT NOT NULL,
        notes TEXT,
        UNIQUE(emp_id, date),
        FOREIGN KEY (emp_id) REFERENCES teachers(emp_id)
    )
    ''')
    
    # Check & Seed Default Admin
    cursor.execute("SELECT * FROM principals WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO principals (username, email, phone, password, full_name, security_question, security_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', 'principal@school.edu', '9876543210', hash_password('admin123'), 'Dr. Arthur Pendelton', 'What city were you born in?', hash_password('london')))
        
    # Check & Seed Sample Teachers
    cursor.execute("SELECT COUNT(*) FROM teachers")
    if cursor.fetchone()[0] == 0:
        sample_teachers = [
            ('EMP101', 'Dr. Sarah Connor', 'CS/IT', 'sarah.c@school.edu', '9876543211', '2021-06-15', 'Sr. Software Engineer', 85000, '123 Tech Park, Innovation City', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah', 'Active'),
            ('EMP102', 'Prof. John Matrix', 'Mechanical', 'john.m@school.edu', '9876543212', '2019-03-20', 'Assistant Professor', 78000, '456 Engine Lane, Industrial Zone', 'https://api.dicebear.com/7.x/avataaars/svg?seed=John', 'Active'),
            ('EMP103', 'Dr. Ellen Ripley', 'Civil', 'ellen.r@school.edu', '9876543213', '2020-01-10', 'Structural Engineer', 82000, '789 Bridge St, Metro', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Ellen', 'Active'),
            ('EMP104', 'Prof. Alan Grant', 'Science & Humanities', 'alan.g@school.edu', '9876543214', '2018-08-01', 'Researcher', 75000, '101 Fossil Way, Campus Area', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alan', 'Active'),
            ('EMP105', 'Prof. Tony Stark', 'Electrical', 'tony.s@school.edu', '9876543215', '2022-02-14', 'Chief Tech Officer', 95000, '1 Stark Tower, Downtown', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Tony', 'Disabled')
        ]
        cursor.executemany('''
        INSERT INTO teachers (emp_id, full_name, department, email, phone, joining_date, previous_job, salary, address, photo_url, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_teachers)
        
        # Populate Sample Attendance Records
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        statuses = ['Present', 'Present', 'Present', 'Late', 'Absent', 'On Leave']
        
        for teacher_id in ['EMP101', 'EMP102', 'EMP103', 'EMP104']:
            curr_d = start_of_month
            while curr_d <= today:
                if curr_d.weekday() < 5:  # Monday to Friday
                    idx = (curr_d.day + int(teacher_id[-1])) % len(statuses)
                    st_val = statuses[idx]
                    
                    in_t = '09:05:00' if st_val == 'Present' else ('09:35:00' if st_val == 'Late' else None)
                    out_t = '16:00:00' if st_val in ['Present', 'Late'] else None
                        
                    cursor.execute('''
                    INSERT OR IGNORE INTO attendance (emp_id, date, in_time, out_time, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (teacher_id, curr_d.strftime('%Y-%m-%d'), in_t, out_t, st_val, 'Auto Logged'))
                curr_d += timedelta(days=1)
                
    conn.commit()
    conn.close()

# Initialize Database
init_db()

# FIXED SESSION STATE INITIALIZATION
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# ==========================================================
# AUTHENTICATION FUNCTIONS
# ==========================================================
def login_user(identifier, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pwd = hash_password(password)
    
    cursor.execute('''
    SELECT * FROM principals 
    WHERE (username = ? OR email = ? OR phone = ?) AND password = ?
    ''', (identifier, identifier, identifier, hashed_pwd))
    
    user = cursor.fetchone()
    conn.close()
    return user

def update_principal_password(username, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pwd = hash_password(new_password)
    cursor.execute("UPDATE principals SET password = ? WHERE username = ?", (hashed_pwd, username))
    conn.commit()
    conn.close()

def render_login_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; margin-bottom: 25px;'>
                <h1 style='color: #0f172a; font-size: 2.2rem; font-weight: 700;'>🏫 EduTrack Portal</h1>
                <p style='color: #64748b;'>Principal & Administration Sign-In</p>
            </div>
        """, unsafe_allow_html=True)
        
        login_tab, forgot_tab = st.tabs(["🔒 Log In", "🔑 Reset Password"])
        
        with login_tab:
            st.markdown("<br>", unsafe_allow_html=True)
            identifier = st.text_input("Username, Email, or Phone", key="login_id")
            password = st.text_input("Password", type="password", key="login_pwd")
            
            if st.button("Log In to Portal", type="primary", use_container_width=True):
                if identifier and password:
                    user = login_user(identifier, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = dict(user)
                        st.success("Authenticated! Loading dashboard...")
                        st.rerun()
                    else:
                        st.error("Invalid credentials provided.")
                else:
                    st.warning("Please enter your login ID and password.")
                    
        with forgot_tab:
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("Verify your security details to reset your password.")
            rec_username = st.text_input("Username", key="rec_user")
            
            if rec_username:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT security_question, security_answer FROM principals WHERE username = ?", (rec_username,))
                res = cursor.fetchone()
                conn.close()
                
                if res:
                    st.markdown(f"**Question:** {res['security_question']}")
                    answer = st.text_input("Security Answer", type="password", key="rec_ans")
                    new_pwd = st.text_input("New Password", type="password", key="rec_new_pwd")
                    
                    if st.button("Update Password", type="primary", use_container_width=True):
                        if hash_password(answer) == res['security_answer']:
                            if new_pwd:
                                update_principal_password(rec_username, new_pwd)
                                st.success("Password reset successfully! You can now log in.")
                            else:
                                st.error("Please provide a new password.")
                        else:
                            st.error("Incorrect security answer.")
                else:
                    st.error("Username not found.")

# ==========================================================
# CALCULATION & RULE ENGINE (Lates & Leaves)
# ==========================================================
def calculate_teacher_stats(emp_id, month=None, year=None):
    if not month: month = date.today().month
    if not year: year = date.today().year
    
    conn = get_db_connection()
    query = '''
    SELECT * FROM attendance 
    WHERE emp_id = ? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
    '''
    df = pd.read_sql_query(query, conn, params=(emp_id, f"{month:02d}", str(year)))
    conn.close()
    
    total_days = len(df)
    present_count = len(df[df['status'] == 'Present'])
    late_count = len(df[df['status'] == 'Late'])
    absent_count = len(df[df['status'] == 'Absent'])
    leave_count = len(df[df['status'] == 'On Leave'])
    half_day_count = len(df[df['status'] == 'Half Day'])
    
    # Core Logic: 3 Lates = 1 Leave Deduction
    late_leaves_deducted = late_count // 3
    remaining_lates_streak = late_count % 3
    
    # CL Calculations (1 Casual Leave earned per month)
    monthly_cl_earned = 1.0
    total_leave_debited = leave_count + (half_day_count * 0.5) + late_leaves_deducted
    cl_balance = max(0.0, monthly_cl_earned - total_leave_debited)
    unpaid_leave = max(0.0, total_leave_debited - monthly_cl_earned)
    
    return {
        "total_days": total_days,
        "present": present_count,
        "late": late_count,
        "absent": absent_count,
        "leave": leave_count,
        "half_day": half_day_count,
        "late_leaves_deducted": late_leaves_deducted,
        "remaining_lates_streak": remaining_lates_streak,
        "monthly_cl_earned": monthly_cl_earned,
        "cl_balance": cl_balance,
        "unpaid_leaves": unpaid_leave
    }

# ==========================================================
# MAIN APPLICATION
# ==========================================================
def render_main_app():
    user = st.session_state.user
    
    # Top Navigation Header Bar
    head_c1, head_c2 = st.columns([4, 1])
    with head_c1:
        st.markdown(f"""
        <div class="app-header">
            <h1>🏫 Principal Administration Dashboard</h1>
            <p>Welcome back, <b>{user['full_name']}</b> | System Active</p>
        </div>
        """, unsafe_allow_html=True)
    with head_c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    # Sidebar
    st.sidebar.title("📌 Menu")
    nav_option = st.sidebar.radio(
        "Navigation",
        [
            "📊 Dashboard & Overview",
            "📅 Daily Attendance Sheet",
            "👨‍🏫 Teacher Management",
            "🔍 Detailed Teacher Profiles",
            "📈 Institutional Reports",
            "⚙️ Security & Password"
        ]
    )

    # ------------------------------------------------------
    # 1. DASHBOARD & OVERVIEW
    # ------------------------------------------------------
    if nav_option == "📊 Dashboard & Overview":
        st.subheader("Today's Campus Summary")
        today_str = date.today().strftime('%Y-%m-%d')
        st.caption(f"Date: {date.today().strftime('%A, %B %d, %Y')}")
        
        conn = get_db_connection()
        teachers_df = pd.read_sql_query("SELECT * FROM teachers WHERE status='Active'", conn)
        att_df = pd.read_sql_query("SELECT * FROM attendance WHERE date = ?", conn, params=(today_str,))
        conn.close()
        
        total_active = len(teachers_df)
        present_count = len(att_df[att_df['status'] == 'Present'])
        late_count = len(att_df[att_df['status'] == 'Late'])
        absent_count = len(att_df[att_df['status'] == 'Absent'])
        leave_count = len(att_df[att_df['status'] == 'On Leave'])
        unmarked_count = total_active - (present_count + late_count + absent_count + leave_count)
        
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Active Teachers", total_active)
        m2.metric("Present Today", present_count)
        m3.metric("Late (> 9:15 AM)", late_count)
        m4.metric("Absent / Leave", absent_count + leave_count)
        m5.metric("Pending Logs", unmarked_count)

        st.markdown("---")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("Attendance Distribution")
            if not att_df.empty:
                fig_pie = px.pie(
                    att_df, 
                    names='status', 
                    hole=0.4,
                    color='status',
                    color_discrete_map={
                        'Present': '#22c55e',
                        'Late': '#f59e0b',
                        'Absent': '#ef4444',
                        'On Leave': '#6366f1'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No attendance recorded for today yet.")

        with col_c2:
            st.subheader("Faculty by Department")
            if not teachers_df.empty:
                dept_counts = teachers_df['department'].value_counts().reset_index()
                dept_counts.columns = ['Department', 'Count']
                fig_bar = px.bar(dept_counts, x='Department', y='Count', color='Department')
                st.plotly_chart(fig_bar, use_container_width=True)

    # ------------------------------------------------------
    # 2. DAILY ATTENDANCE SHEET
    # ------------------------------------------------------
    elif nav_option == "📅 Daily Attendance Sheet":
        st.subheader("Mark Daily Attendance")
        
        selected_date = st.date_input("Attendance Date", value=date.today())
        selected_date_str = selected_date.strftime('%Y-%m-%d')
        
        st.info("🕒 **Shift Rules:** Arrival standard is **9:15 AM**. Arrival after 9:15 AM automatically marks as **Late**. Every 3 lates calculate as 1 leave deduction.")
        
        conn = get_db_connection()
        teachers = pd.read_sql_query("SELECT emp_id, full_name, department FROM teachers WHERE status='Active'", conn)
        existing_att = pd.read_sql_query("SELECT * FROM attendance WHERE date = ?", conn, params=(selected_date_str,))
        conn.close()
        
        existing_dict = {row['emp_id']: row for _, row in existing_att.iterrows()}
        
        with st.form("daily_attendance_form"):
            attendance_data = []
            
            # Header
            h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2.5, 2, 2.5, 2, 2])
            h1.markdown("**ID**")
            h2.markdown("**Name**")
            h3.markdown("**Department**")
            h4.markdown("**Status**")
            h5.markdown("**In-Time**")
            h6.markdown("**Out-Time**")
            st.markdown("---")
            
            for _, idx in teachers.iterrows():
                emp_id = idx['emp_id']
                name = idx['full_name']
                dept = idx['department']
                
                prev_status = existing_dict.get(emp_id, {}).get('status', 'Present')
                prev_in = existing_dict.get(emp_id, {}).get('in_time', '09:15:00')
                prev_out = existing_dict.get(emp_id, {}).get('out_time', '16:00:00')
                
                c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2.5, 2, 2.5, 2, 2])
                c1.write(emp_id)
                c2.write(name)
                c3.write(dept)
                
                status_opt = c4.selectbox(
                    f"Status_{emp_id}", 
                    ['Present', 'Late', 'Absent', 'On Leave', 'Half Day'], 
                    index=['Present', 'Late', 'Absent', 'On Leave', 'Half Day'].index(prev_status) if prev_status in ['Present', 'Late', 'Absent', 'On Leave', 'Half Day'] else 0,
                    label_visibility="collapsed"
                )
                
                in_time_val = c5.text_input(f"In_{emp_id}", value=prev_in if prev_in else "09:15:00", label_visibility="collapsed")
                out_time_val = c6.text_input(f"Out_{emp_id}", value=prev_out if prev_out else "16:00:00", label_visibility="collapsed")
                
                attendance_data.append({
                    'emp_id': emp_id,
                    'status': status_opt,
                    'in_time': in_time_val,
                    'out_time': out_time_val
                })
                
            save_btn = st.form_submit_button("💾 Save Attendance Sheet", type="primary", use_container_width=True)
            
            if save_btn:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                for item in attendance_data:
                    final_status = item['status']
                    # Auto Late Flag Check (> 09:15)
                    if item['in_time'] and final_status == 'Present':
                        try:
                            t_obj = datetime.strptime(item['in_time'], "%H:%M:%S").time()
                            if t_obj > time(9, 15):
                                final_status = 'Late'
                        except ValueError:
                            pass
                            
                    cursor.execute('''
                    INSERT INTO attendance (emp_id, date, in_time, out_time, status)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(emp_id, date) DO UPDATE SET
                        in_time = excluded.in_time,
                        out_time = excluded.out_time,
                        status = excluded.status
                    ''', (item['emp_id'], selected_date_str, item['in_time'], item['out_time'], final_status))
                    
                conn.commit()
                conn.close()
                st.success(f"Attendance for {selected_date_str} successfully recorded!")

    # ------------------------------------------------------
    # 3. TEACHER MANAGEMENT
    # ------------------------------------------------------
    elif nav_option == "👨‍🏫 Teacher Management":
        st.subheader("Faculty Records Management")
        
        crud_1, crud_2, crud_3 = st.tabs(["📋 Staff Directory", "➕ Add New Teacher", "⚙️ Status & Actions"])
        
        with crud_1:
            conn = get_db_connection()
            teachers_df = pd.read_sql_query("SELECT emp_id, full_name, department, email, phone, joining_date, salary, status FROM teachers", conn)
            conn.close()
            
            s1, s2 = st.columns([2, 1])
            search_q = s1.text_input("🔍 Search Name or Employee ID", "")
            dept_filter = s2.selectbox("Department", ["All"] + list(teachers_df['department'].unique()))
            
            filtered_df = teachers_df.copy()
            if search_q:
                filtered_df = filtered_df[filtered_df['full_name'].str.contains(search_q, case=False) | filtered_df['emp_id'].str.contains(search_q, case=False)]
            if dept_filter != "All":
                filtered_df = filtered_df[filtered_df['department'] == dept_filter]
                
            st.dataframe(filtered_df, use_container_width=True)

        with crud_2:
            st.markdown("### Add New Teacher")
            with st.form("add_teacher_form"):
                ac1, ac2 = st.columns(2)
                emp_id = ac1.text_input("Employee ID *", f"EMP{np.random.randint(100, 999)}")
                full_name = ac2.text_input("Full Name *")
                
                ac3, ac4 = st.columns(2)
                department = ac3.selectbox("Department *", ["CS/IT", "Civil", "Mechanical", "Electrical", "Electronics", "Science & Humanities"])
                email = ac4.text_input("Email *")
                
                ac5, ac6 = st.columns(2)
                phone = ac5.text_input("Phone Number *")
                joining_date = ac6.date_input("Joining Date", date.today())
                
                ac7, ac8 = st.columns(2)
                previous_job = ac7.text_input("Previous Job")
                salary = ac8.number_input("Monthly Salary (₹)", min_value=0.0, value=50000.0)
                
                address = st.text_area("Address")
                photo_url = st.text_input("Photo / Avatar URL", "https://api.dicebear.com/7.x/avataaars/svg?seed=" + full_name)
                
                if st.form_submit_button("Create Teacher Record", type="primary"):
                    if emp_id and full_name and email and phone:
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute('''
                            INSERT INTO teachers (emp_id, full_name, department, email, phone, joining_date, previous_job, salary, address, photo_url, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')
                            ''', (emp_id, full_name, department, email, phone, joining_date.strftime('%Y-%m-%d'), previous_job, salary, address, photo_url))
                            conn.commit()
                            conn.close()
                            st.success(f"Teacher {full_name} added successfully!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Employee ID or Email already exists.")
                    else:
                        st.error("Please fill in required fields (*)")

        with crud_3:
            conn = get_db_connection()
            teachers = pd.read_sql_query("SELECT emp_id, full_name, status FROM teachers", conn)
            conn.close()
            
            if not teachers.empty:
                selected_emp = st.selectbox("Select Teacher", teachers['emp_id'] + " - " + teachers['full_name'])
                emp_code = selected_emp.split(" - ")[0]
                
                curr_status = teachers[teachers['emp_id'] == emp_code].iloc[0]['status']
                st.write(f"Current Status: **{curr_status}**")
                
                u1, u2 = st.columns(2)
                with u1:
                    new_st = st.selectbox("Update Status", ["Active", "Disabled"])
                    if st.button("Save Status"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE teachers SET status = ? WHERE emp_id = ?", (new_st, emp_code))
                        conn.commit()
                        conn.close()
                        st.success("Status updated.")
                        st.rerun()
                        
                with u2:
                    if st.button("🗑️ Delete Teacher", type="secondary"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM attendance WHERE emp_id = ?", (emp_code,))
                        cursor.execute("DELETE FROM teachers WHERE emp_id = ?", (emp_code,))
                        conn.commit()
                        conn.close()
                        st.warning("Teacher removed.")
                        st.rerun()

    # ------------------------------------------------------
    # 4. DETAILED TEACHER PROFILES
    # ------------------------------------------------------
    elif nav_option == "🔍 Detailed Teacher Profiles":
        st.subheader("Teacher Analytics & Profile")
        
        conn = get_db_connection()
        teachers_df = pd.read_sql_query("SELECT * FROM teachers", conn)
        conn.close()
        
        if not teachers_df.empty:
            selected_emp_id = st.selectbox(
                "Select Teacher", 
                teachers_df['emp_id'] + " - " + teachers_df['full_name']
            ).split(" - ")[0]
            
            info = teachers_df[teachers_df['emp_id'] == selected_emp_id].iloc[0]
            
            p1, p2 = st.columns([1, 3])
            with p1:
                st.image(info['photo_url'] if info['photo_url'] else "https://via.placeholder.com/150", width=140)
                st.markdown(f"**Status:** {info['status']}")
                
            with p2:
                st.markdown(f"## {info['full_name']}")
                st.markdown(f"**ID:** {info['emp_id']} | **Department:** {info['department']}")
                st.markdown(f"📧 {info['email']} | 📞 {info['phone']}")
                st.markdown(f"💼 **Exp:** {info['previous_job']} | 💰 **Salary:** ₹{info['salary']:,.2f}")
                st.markdown(f"🏠 **Address:** {info['address']}")

            st.markdown("---")
            st.markdown("### 🧮 Monthly Rule Analytics")
            stats = calculate_teacher_stats(selected_emp_id)
            
            sc1, sc2, sc3, sc4, sc5 = st.columns(5)
            sc1.metric("Present Days", stats['present'])
            sc2.metric("Late Days", stats['late'], delta=f"-{stats['late_leaves_deducted']} Leave" if stats['late_leaves_deducted'] > 0 else "0")
            sc3.metric("Absents", stats['absent'])
            sc4.metric("Leaves / Earned CL", f"{stats['leave']} / {stats['monthly_cl_earned']}")
            sc5.metric("Remaining CL", f"{stats['cl_balance']} CL")
            
            if stats['remaining_lates_streak'] > 0:
                st.warning(f"⚠️ Late Streak: {stats['remaining_lates_streak']} late arrival(s). {3 - stats['remaining_lates_streak']} more late will trigger 1 day leave deduction.")

            st.markdown("---")
            conn = get_db_connection()
            att_records = pd.read_sql_query("SELECT date, status, in_time, out_time FROM attendance WHERE emp_id = ? ORDER BY date DESC", conn, params=(selected_emp_id,))
            conn.close()
            
            if not att_records.empty:
                c1, c2 = st.columns(2)
                with c1:
                    fig_p = px.pie(att_records, names='status', title="Overall Status Ratio")
                    st.plotly_chart(fig_p, use_container_width=True)
                with c2:
                    st.markdown("### Recent Log Records")
                    st.dataframe(att_records.head(10), use_container_width=True)

    # ------------------------------------------------------
    # 5. INSTITUTIONAL REPORTS
    # ------------------------------------------------------
    elif nav_option == "📈 Institutional Reports":
        st.subheader("Monthly Institutional Reports")
        
        rep_month = st.selectbox("Select Month", list(range(1, 13)), index=date.today().month - 1)
        rep_year = st.selectbox("Select Year", [2025, 2026, 2027], index=1)
        
        conn = get_db_connection()
        teachers = pd.read_sql_query("SELECT emp_id, full_name, department FROM teachers WHERE status='Active'", conn)
        conn.close()
        
        report_data = []
        for _, t in teachers.iterrows():
            st_data = calculate_teacher_stats(t['emp_id'], month=rep_month, year=rep_year)
            report_data.append({
                'Employee ID': t['emp_id'],
                'Teacher Name': t['full_name'],
                'Department': t['department'],
                'Present': st_data['present'],
                'Late Days': st_data['late'],
                'Absents': st_data['absent'],
                'Leaves Taken': st_data['leave'],
                'Late Deductions': st_data['late_leaves_deducted'],
                'CL Balance': st_data['cl_balance']
            })
            
        rep_df = pd.DataFrame(report_data)
        st.dataframe(rep_df, use_container_width=True)
        
        csv = rep_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Report as CSV",
            data=csv,
            file_name=f"Attendance_Report_{rep_month}_{rep_year}.csv",
            mime="text/csv",
            type="primary"
        )

    # ------------------------------------------------------
    # 6. SECURITY & PASSWORD
    # ------------------------------------------------------
    elif nav_option == "⚙️ Security & Password":
        st.subheader("Principal Credentials & Security")
        
        with st.form("sec_form"):
            curr_p = st.text_input("Current Password", type="password")
            new_p = st.text_input("New Password", type="password")
            conf_p = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Credentials", type="primary"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM principals WHERE id = ?", (user['id'],))
                db_pass = cursor.fetchone()[0]
                
                if hash_password(curr_p) == db_pass:
                    if new_p and new_p == conf_p:
                        cursor.execute("UPDATE principals SET password = ? WHERE id = ?", (hash_password(new_p), user['id']))
                        conn.commit()
                        st.success("Password updated successfully!")
                    else:
                        st.error("Passwords do not match.")
                else:
                    st.error("Current password incorrect.")
                conn.close()

# ==========================================================
# ENTRY POINT
# ==========================================================
if __name__ == "__main__":
    if not st.session_state.logged_in:
        render_login_page()
    else:
        render_main_app()