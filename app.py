import streamlit as st
import pandas as pd
import urllib.parse
import requests
import time
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="4G_fastfood System", page_icon="🍔", layout="wide")

# ----------------- BRANDED ADVANCED CSS STYLING -----------------
st.markdown("""
    <style>
    .stApp { background-color: #FAFAFA; }
    .brand-title { font-size: 42px; font-weight: 900; color: #1B5E20; text-align: center; margin-bottom: 5px; letter-spacing: 1px; }
    .brand-subtitle { font-size: 16px; color: #558B2F; text-align: center; margin-bottom: 30px; font-weight: 500; }
    .section-header { font-size: 24px; font-weight: bold; color: #2E7D32; border-bottom: 3px solid #A5D6A7; padding-bottom: 8px; margin-top: 25px; margin-bottom: 15px; }
    .menu-card { background-color: #E8F5E9; padding: 18px; border-radius: 12px; border-left: 6px solid #2E7D32; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .menu-card strong { font-size: 18px; color: #1B5E20; }
    .price-tag { color: #E65100; font-weight: bold; font-size: 16px; float: right; }
    .floating-wa { position: fixed; bottom: 25px; right: 25px; background-color: #25D366; color: white !important; padding: 14px 22px; border-radius: 50px; font-weight: bold; font-size: 16px; box-shadow: 0px 5px 15px rgba(0,0,0,0.3); z-index: 999999; text-decoration: none !important; }
    </style>
""", unsafe_allow_html=True)

# ----------------- 🚨 LIVE LINK YA GOOGLE APPS SCRIPT ULIYOWEKA -----------------
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzo5PUYDG9tOHJ_r8IzlUEtJGEQ5kojJAfI6sKm__td6RwbdOEiQaqNEqVZbNJxXeNksg/exec"

ORDER_COLS = ['Order_ID', 'Customer_Name', 'Phone_Number', 'Items_Ordered', 'Total_Amount', 'Delivery_Required', 'Delivery_Address', 'Status', 'Timestamp', 'Assigned_Staff']
EXPENSE_COLS = ['Expense_ID', 'Date', 'Category', 'Vendor', 'Description', 'Amount']

# Kazi ya kusoma data kutoka Google Sheets kupitia API Link yako
def load_data_via_api(worksheet_name, default_cols):
    try:
        response = requests.get(f"{SCRIPT_URL}?sheetName={worksheet_name}", timeout=15)
        if response.status_code == 200:
            data_json = response.json()
            # Kama hakuna data au kuna kosa, inarudisha jedwali tupu lenye vichwa vya habari
            if not data_json or "status" in str(data_json):
                return pd.DataFrame(columns=default_cols)
            
            df = pd.DataFrame(data_json)
            
            # Usafirishaji wa majina ya nguzo kuondoa mapengo au herufi zisizolingana
            clean_cols = {}
            for col in df.columns:
                clean_name = str(col).strip().replace(" ", "_")
                if clean_name.lower() == "order_id": clean_name = "Order_ID"
                if clean_name.lower() == "expense_id": clean_name = "Expense_ID"
                clean_cols[col] = clean_name
            df.rename(columns=clean_cols, inplace=True)
            
            # Kuhakikisha nguzo zote zipo hata kama hazina data
            for col in default_cols:
                if col not in df.columns:
                    df[col] = ""
                    
            return df[default_cols]
        return pd.DataFrame(columns=default_cols)
    except Exception:
        return pd.DataFrame(columns=default_cols)

# Kazi ya kutuma au ku-update data kwenye Google Sheets kupitia API Link yako
def add_row_to_sheet(worksheet_name, row_list):
    try:
        payload = {
            "sheetName": worksheet_name,
            "rowData": [str(x) for x in row_list]
        }
        response = requests.post(SCRIPT_URL, json=payload, timeout=15)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Imeshindwa kuunganisha na kanzidata ya Google: {e}")
        return False

# Kupakia data za sasa hivi moja kwa moja (Live Sync)
orders_df = load_data_via_api("Orders", ORDER_COLS)
expenses_df = load_data_via_api("Expenses", EXPENSE_COLS)

# Menu configuration
if 'dynamic_menu' not in st.session_state:
    st.session_state.dynamic_menu = pd.DataFrame({
        'Item_ID': range(1, 16),
        'Name': [
            'Ugali-msamaki', 'wali-nyama', 'wali-samaki', 'pilau-nyama',
            'pilau-samaki', 'wali-maharage', 'chipsi-kavu', 'chipsi-mayai',
            'mshikaki-kuku', 'mshikaki-ng\'ombe', 'juice', 'soda',
            'maji', 'ndizi-choma', 'chapati'
        ],
        'Category': [
            'Chakula', 'Chakula', 'Chakula', 'Chakula', 'Chakula', 'Chakula', 'Chakula', 'Chakula',
            'Vitafunio', 'Vitafunio', 'Vinywaji', 'Vinywaji', 'Vinywaji', 'Vitafunio', 'Vitafunio'
        ],
        'Price': [2000, 2500, 2000, 2500, 5000, 2000, 2000, 3000, 1000, 500, 1000, 700, 700, 1500, 500]
    })

if 'attendance_log' not in st.session_state:
    st.session_state.attendance_log = pd.DataFrame(columns=['Staff_Name', 'Action', 'Timestamp'])

# Brand Headers
st.markdown("<div class='brand-title'>⚡ 4G_fastfood System</div>", unsafe_allow_html=True)
st.markdown("<div class='brand-subtitle'>Huduma ya Haraka, Chakula Kitamu na Mifumo ya Kisasa</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🛒 Agiza Chakula", "🧑‍🍳 Staff Dashboard", "📊 Financial Admin", "📋 Staff Attendance"])

# ==============================================================================
# TAB 1: CUSTOMER ORDER VIEW
# ==============================================================================
with tab1:
    st.markdown("<div class='section-header'>Chagua Menyu Yako Safi Chini</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        cart = {}
        current_menu = st.session_state.dynamic_menu
        for category in current_menu['Category'].unique():
            st.write(f"### 🟢 **{category.upper()}**")
            sub_df = current_menu[current_menu['Category'] == category]
            for _, row in sub_df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class='menu-card'>
                        <span class='price-tag'>TZS {int(row['Price']):,}</span>
                        <strong>{row['Name']}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    qty = st.number_input(f"Idadi / Quantity:", min_value=0, max_value=50, step=1, key=f"item_{row['Item_ID']}")
                    if qty > 0:
                        cart[row['Name']] = {'qty': qty, 'price': row['Price']}
    
    with col2:
        st.subheader("Taarifa za Mteja")
        c_name = st.text_input("Jina Lako Kamili (Full Name):", placeholder="Mfn: John Doe")
        c_phone = st.text_input("Namba yako ya WhatsApp (Phone Number):", placeholder="Mfn: 255615288736")
        
        delivery = st.checkbox("Je unahitaji usafirishaji nyumbani (Delivery)?")
        address = "N/A"
        delivery_fee = 1500 if delivery else 0
        if delivery:
            address = st.text_area("Sehemu Unayokaa (Delivery Address):", placeholder="Weka maelezo ya eneo...")

        st.markdown("---")
        st.write("### 🧾 Muhtasari wa Garama")
        subtotal = sum(details['qty'] * details['price'] for details in cart.values())
        grand_total = subtotal + delivery_fee
        
        for item, details in cart.items():
            st.write(f"• {item} x {details['qty']} = TZS {details['qty']*details['price']:,}")
        if delivery: 
            st.write(f"• Delivery Fee = TZS {delivery_fee:,}")
        st.markdown(f"### **JUMLA KUU: TZS {grand_total:,}**")
        
        if st.button("Kamilisha Oda sasa", type="primary"):
            if not c_name or not c_phone or not cart:
                st.error("Tafadhali kamilisha kujaza jina, namba na uchague chakula!")
            else:
                try:
                    if not orders_df.empty and 'Order_ID' in orders_df.columns:
                        valid_ids = pd.to_numeric(orders_df['Order_ID'], errors='coerce').dropna()
                        order_id = int(valid_ids.max() + 1) if not valid_ids.empty else 1001
                    else:
                        order_id = 1001
                except Exception:
                    order_id = 1001
                    
                items_str = ", ".join([f"{k} (x{v['qty']})" for k, v in cart.items()])
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                row_data = [order_id, c_name, c_phone, items_str, grand_total, str(delivery), address, 'Pending', timestamp, 'Unassigned']
                
                with st.spinner("Inatuma oda yako jikoni..."):
                    if add_row_to_sheet("Orders", row_data):
                        st.balloons()
                        st.success(f"🎉 Imefanikiwa! Mfumo umehifadhi Oda yako. ID: #{order_id}")
                        time.sleep(1.5)
                        st.rerun()

# ==============================================================================
# TAB 2: STAFF DASHBOARD
# ==============================================================================
with tab2:
    st.markdown("<div class='section-header'>Oda Zinazosubiri Jikoni (Pending Verification)</div>", unsafe_allow_html=True)
    
    if not orders_df.empty and 'Status' in orders_df.columns:
        orders_df['Order_ID'] = orders_df['Order_ID'].astype(str)
        orders_df['Status_Clean'] = orders_df['Status'].astype(str).str.strip().str.lower()
        pending_orders = orders_df[orders_df['Status_Clean'] == 'pending']
        
        if pending_orders.empty:
            st.info("Safi sana! Hakuna oda zinazosubiri kupikwa kwa sasa.")
        else:
            st.dataframe(pending_orders[ORDER_COLS], use_container_width=True)
            
            st.subheader("⚙️ On-Screen Quick Actions")
            selected_order = st.selectbox("Chagua Order ID ya Kushughulikia:", pending_orders['Order_ID'].values)
            handler = st.text_input("Mhudumu Handler (Your Name):")
            
            if st.button("Change Status to APPROVED", type="primary"):
                if not handler:
                    st.warning("Tafadhali weka jina lako kabla ya ku-approve!")
                else:
                    approval_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    matched_row = pending_orders[pending_orders['Order_ID'] == selected_order].iloc[0]
                    
                    update_row = [
                        selected_order, matched_row['Customer_Name'], matched_row['Phone_Number'],
                        matched_row['Items_Ordered'], matched_row['Total_Amount'], matched_row['Delivery_Required'],
                        matched_row['Delivery_Address'], 'Approved', approval_timestamp, handler
                    ]
                    with st.spinner("Inabadilisha hali ya oda kuwa APPROVED..."):
                        if add_row_to_sheet("Orders", update_row):
                            st.success(f"Oda #{selected_order} imethibitishwa na kuhifadhiwa vyema!")
                            time.sleep(1.5)
                            st.rerun()
    else:
        st.info("Safi sana! Hakuna oda zinazosubiri kupikwa kwa sasa.")

    st.markdown("<div class='section-header'>Oda Zilizothibitishwa (Approved Log View)</div>", unsafe_allow_html=True)
    if not orders_df.empty and 'Status' in orders_df.columns:
        orders_df['Status_Clean'] = orders_df['Status'].astype(str).str.strip().str.lower()
        approved_orders = orders_df[orders_df['Status_Clean'] == 'approved']
        if not approved_orders.empty:
            st.dataframe(approved_orders[['Order_ID', 'Customer_Name', 'Items_Ordered', 'Total_Amount', 'Assigned_Staff', 'Timestamp']], use_container_width=True)

# ==============================================================================
# TAB 3: FINANCIAL ADMIN & LIVE PERFORMANCE PROFILE
# ==============================================================================
with tab3:
    st.markdown("<div class='section-header'>Usimamizi wa Menyu & Mizania ya Fedha</div>", unsafe_allow_html=True)
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("Orodha ya Menyu Iliyopo Sasa")
        st.dataframe(st.session_state.dynamic_menu, use_container_width=True)
    with col_m2:
        st.subheader("Muhtasari wa Faida na Hasara (Live Analysis)")
        total_approved_inc = 0
        total_pending_inc = 0
        if not orders_df.empty and 'Status' in orders_df.columns and 'Total_Amount' in orders_df.columns:
            orders_df['Status_Clean'] = orders_df['Status'].astype(str).str.strip().str.lower()
            orders_df['Numeric_Amount'] = pd.to_numeric(orders_df['Total_Amount'], errors='coerce').fillna(0)
            total_approved_inc = orders_df[orders_df['Status_Clean'] == 'approved']['Numeric_Amount'].sum()
            total_pending_inc = orders_df[orders_df['Status_Clean'] == 'pending']['Numeric_Amount'].sum()
        
        total_exp = 0
        if not expenses_df.empty and 'Amount' in expenses_df.columns:
            expenses_df['Numeric_Expense'] = pd.to_numeric(expenses_df['Amount'], errors='coerce').fillna(0)
            total_exp = expenses_df['Numeric_Expense'].sum()
            
        st.metric(label="💰 Mapato Halisi (Approved Cash)", value=f"TZS {int(total_approved_inc):,}")
        st.metric(label="⏳ Thamani ya Oda Zinazosubiri", value=f"TZS {int(total_pending_inc):,}")
        st.metric(label="📉 Jumla ya Matumizi (Total Expenses)", value=f"TZS {int(total_exp):,}")
        st.metric(label="📊 FAIDA KUU (Net Profit)", value=f"TZS {int(total_approved_inc - total_exp):,}")

# ==============================================================================
# TAB 4: STAFF ATTENDANCE TRACKER
# ==============================================================================
with tab4:
    st.markdown("<div class='section-header'>📋 Mahudhurio ya Wafanyakazi (Staff Attendance)</div>", unsafe_allow_html=True)
    staff_member = st.selectbox("Chagua Jina Lako:", ["Mhudumu 1", "Mpishi Mkuu", "Driver Delivery", "Admin Partner"])
    attendance_action = st.radio("Unachagua kufanya nini?", ["Clock In (Kuingia)", "Clock Out (Kutoka)"])
    if st.button("Hifadhi Mahudhurio"):
        st.success(f"✅ Umefanikiwa kusajili mahudhurio ya {staff_member}!")