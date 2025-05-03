import streamlit as st
from cryptography.fernet import Fernet
import hashlib
from datetime import datetime
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Secure Vault",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
    <style>
        html, body, .stApp {
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: "Times New Roman", Times, serif;
            font-size: 14px;
        }
        .stApp {
            display: flex;
            flex-direction: column;
        }
        .main-container {
            flex: 1 0 auto;
        }
        .footer-text {
            text-align: center;
            padding: 20px;
            margin-top: auto;
            color: gray;
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: white;
        }
        .footer-text span.dev {
            color: #0056b3;
            font-weight: bold;
        }
        .footer-text span.secure {
            color: #008080;
            font-weight: bold;
        }
        h1, h2, h3, h4 {
            color: blue !important;
            font-size: 22px !important;
            font-family: "Times New Roman", Times, serif;
        }
        h1 {
            color: blue !important;
            font-size: 32px !important;
            font-family: "Times New Roman", Times, serif;
        }
        .sidebar .sidebar-content {
            background-color: #2c3e50;
            color: white;
        }
        .stButton>button {
            transition: all 0.3s ease;
            border-radius: 8px;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .card {
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            background: white;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'stored_data' not in st.session_state:
    st.session_state.stored_data = {}

if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"

if 'registered_users' not in st.session_state:
    st.session_state.registered_users = {"admin": hashlib.sha256("admin123".encode()).hexdigest()}

# --- Utility Functions ---
def generate_key():
    return Fernet.generate_key()

def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_text(text, key):
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(text.encode())

def decrypt_text(encrypted_text, key):
    try:
        cipher_suite = Fernet(key)
        return cipher_suite.decrypt(encrypted_text).decode()
    except:
        return None

# --- Registration Page ---
def registration_page():
    st.markdown("<h1 style='text-align: center; color: blue;'>Secure Vault</h1>", unsafe_allow_html=True)
    st.title("📝 Register")
    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.form_submit_button("Register"):
            if not username or not password or not confirm_password:
                st.error("Please fill all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif username in st.session_state.registered_users:
                st.error("Username already exists.")
            else:
                st.session_state.registered_users[username] = hash_passkey(password)
                st.success("Registration successful. Please login.")
                time.sleep(1)
                st.session_state.current_page = "login"
                st.rerun()

    if st.button("🔐 Already have an account? Login here"):
        st.session_state.current_page = "login"
        st.rerun()

# --- Login Page ---
def login_page():
    st.markdown("<h1 style='text-align: center; color: blue;'>Secure Vault</h1>", unsafe_allow_html=True)
    st.title("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.form_submit_button("Login"):
            if username in st.session_state.registered_users:
                if st.session_state.registered_users[username] == hash_passkey(password):
                    st.success("Login successful!")
                    st.session_state.authenticated = True
                    st.session_state.failed_attempts = 0
                    st.session_state.current_page = "home"
                    st.rerun()
                else:
                    st.error("Incorrect password")
            else:
                st.error("User not found")

    if st.button("📝 Don't have an account? Register here"):
        st.session_state.current_page = "register"
        st.rerun()

# --- Home Page ---
def home_page():
    st.title("🛡️ Secure Vault")
    st.markdown("""
    <div class="card">
        <h3>Welcome to Secure Data Encryption System</h3>
        <p>Store and retrieve your sensitive data with military-grade encryption</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h4>New Encryption</h4>
            <p>Securely store new sensitive data</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Store Data", key="store_btn"):
            st.session_state.current_page = "store"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="card">
            <h4>Data Retrieval</h4>
            <p>Access your encrypted data</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Retrieve Data", key="retrieve_btn"):
            st.session_state.current_page = "retrieve"
            st.rerun()

# --- Store Data Page ---
def store_data_page():
    st.title("🛡️ New Encryption")
    with st.form("store_form"):
        st.markdown("### Secure Data Storage")
        data_name = st.text_input("Data Identifier*", help="Unique name to identify your data")
        text_to_store = st.text_area("Sensitive Data*", height=200)
        passkey = st.text_input("Encryption Passkey*", type="password")
        confirm_passkey = st.text_input("Confirm Passkey*", type="password")
        submitted = st.form_submit_button("🔒 Encrypt & Store")

        if submitted:
            if not all([data_name, text_to_store, passkey, confirm_passkey]):
                st.error("All fields are required!")
            elif passkey != confirm_passkey:
                st.error("Passkeys do not match!")
            elif data_name in st.session_state.stored_data:
                st.error("Identifier already exists!")
            else:
                with st.spinner("Encrypting data..."):
                    time.sleep(1)
                    key = generate_key()
                    encrypted_text = encrypt_text(text_to_store, key)
                    hashed_passkey = hash_passkey(passkey)

                    st.session_state.stored_data[data_name] = {
                        "encrypted_text": encrypted_text,
                        "key": key,
                        "passkey_hash": hashed_passkey,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                st.success("Data encrypted and stored securely!")
                st.balloons()
                time.sleep(2)
                st.session_state.current_page = "home"
                st.rerun()

    if st.button("← Back to Home"):
        st.session_state.current_page = "home"
        st.rerun()

# --- Retrieve Data Page ---
def retrieve_data_page():
    st.title("🔓 Data Retrieval")
    if not st.session_state.stored_data:
        st.warning("No encrypted data found")
        if st.button("← Back to Home"):
            st.session_state.current_page = "home"
            st.rerun()
        return

    data_name = st.selectbox("Select Data", options=list(st.session_state.stored_data.keys()))
    with st.form("retrieve_form"):
        passkey = st.text_input("Decryption Passkey", type="password")
        submitted = st.form_submit_button("🔓 Decrypt Data")

        if submitted:
            stored_entry = st.session_state.stored_data[data_name]
            hashed_input = hash_passkey(passkey)

            if hashed_input == stored_entry["passkey_hash"]:
                with st.spinner("Decrypting..."):
                    time.sleep(1)
                    decrypted_text = decrypt_text(stored_entry["encrypted_text"], stored_entry["key"])

                    if decrypted_text is not None:
                        st.success("Decryption successful!")
                        st.markdown(f"""
                            <div class="card">
                                <h4>Decrypted Data</h4>
                                <p style='word-wrap: break-word;'>{decrypted_text}</p>
                                <p class="small">Stored on: {stored_entry["timestamp"]}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Decryption failed")
            else:
                st.session_state.failed_attempts += 1
                st.error("Invalid passkey")
                if st.session_state.failed_attempts >= 3:
                    st.error("🚨 Too many failed attempts! System locked.")
                    st.session_state.authenticated = False
                    st.session_state.current_page = "login"
                    time.sleep(2)
                    st.rerun()

    if st.button("← Back to Home"):
        st.session_state.current_page = "home"
        st.rerun()

# --- Logout ---
def logout_page():
    st.session_state.authenticated = False
    st.session_state.current_page = "login"
    st.success("Logged out successfully.")
    time.sleep(1)
    st.rerun()

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://i.postimg.cc/DfxcvBXf/secure-data-removebg-preview.png", width=120)
    st.title("Navigation")

    if st.session_state.authenticated:
        if st.button("🏠 Home"):
            st.session_state.current_page = "home"
            st.rerun()
        if st.button("🛡️ Store Data"):
            st.session_state.current_page = "store"
            st.rerun()
        if st.button("🔓 Retrieve Data"):
            st.session_state.current_page = "retrieve"
            st.rerun()
        if st.button("🚪 Logout"):
            logout_page()
    else:
        st.info("Please login")

    st.markdown("---")
    st.markdown("### System Info")
    st.write(f"Encrypted Items: {len(st.session_state.stored_data)}")
    st.write(f"Version: 2.1.0")

# --- App Routing Container ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Page Routing Logic
if not st.session_state.authenticated:
    if st.session_state.current_page == "login":
        login_page()
    elif st.session_state.current_page == "register":
        registration_page()
else:
    if st.session_state.current_page == "home":
        home_page()
    elif st.session_state.current_page == "store":
        store_data_page()
    elif st.session_state.current_page == "retrieve":
        retrieve_data_page()

st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
    <div class="footer-text">
        © 2025 <span class="secure">Secure Systems</span> | Developed by <span class="dev">Uzma Azam</span>
    </div>
""", unsafe_allow_html=True)
