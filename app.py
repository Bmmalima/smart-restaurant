import streamlit as st
import pandas as pd
import urllib.parse
import requests
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

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
    .field-label { font-size: 16px; font-weight: bold; color: #1B5E20; margin-top: 10px; margin-bottom: -5px; display: block; }
    </style>
""", unsafe_allow_html=True)

# ----------------- FLOATING WHATSAPP CUSTOMER SERVICE -----------------
SUPPORT_PHONE = "255615288736" 
encoded_support_msg = urllib.parse.quote("Hello 4G_fastfood, nahitaji msaada/huduma tafadhali.")
support_url = f"https://api.whatsapp.com/send?phone={SUPPORT_PHONE}&text={encoded_support_msg}"
st.markdown(f'<a href="{support_url}" target="_blank" class="floating-wa">💬 Chat na 4G_fastfood</a>', unsafe_allow_html=True)

# ----------------- DATABASE INITIALIZATION & LIVE SYNC -----------------
conn = st.connection("gsheets", type=GSheetsConnection)

# Explicitly defining column rules to avoid index crashes on blank spreadsheets
ORDER_COLS = ['Order_ID', 'Customer_Name', 'Phone_Number', 'Items_Ordered', 'Total_Amount', 'Delivery_Required', 'Delivery_Address', 'Status', 'Timestamp', 'Assigned_Staff']
EXPENSE_COLS = ['Expense_ID', 'Date', 'Category', 'Vendor', 'Description', 'Amount']

def load_data(worksheet_name, default_cols):
    try:
        df = conn.read(worksheet=worksheet_name, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=default_cols)
        # Drop rows where critical tracking identities are entirely missing
        df.dropna(how='all', inplace=True)
        return df
    except Exception:
        return pd.DataFrame(columns=default_cols)

# Push data to Google Sheet using Web Script API
def add_row_to_sheet(worksheet_name, row_list):
    try:
        script_url = "https://script.google.com/macros/s/AKfycbzcO5vN738web5dkDD7OYRWMlVgeZ8p0Jnmw0KQ8e6Ue3FalwkRfusfVHphzZ3BzBOMaw/exec"
        payload = {
            "sheetName": worksheet_name,
            "rowData": [str(x) for x in row_list]
        }
        response = requests.post(script_url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Failed to reach database pipeline: {e}")
        return False

# Menu Matrix
menu_df = pd.DataFrame({
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

# Initialize Operational Data Frames Live
orders_df = load_data("Orders", ORDER_COLS)
expenses_df = load_data("Expenses", EXPENSE_COLS)

# ----------------- BRAND HEADERS -----------------
st.markdown("<div class='brand-title'>⚡ 4G_fastfood System</div>", unsafe_allow_html=True)
st.markdown("<div class='brand-subtitle'>Huduma ya Haraka, Chakula Kitamu na Mifumo ya Kisasa</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 Agiza Chakula (Ordering)", "🧑‍🍳 Staff Dashboard", "📊 Financial Admin"])

# ==============================================================================
# TAB 1: CUSTOMER VIEW
# ==============================================================================
with tab1:
    st.markdown("<div class='section-header'>Chagua Menyu Yako Safi Chini</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        cart = {}
        for category in menu_df['Category'].unique():
            st.write(f"### 🟢 **{category.upper()}**")
            sub_df = menu_df[menu_df['Category'] == category]
            for _, row in sub_df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class='menu-card'>
                        <span class='price-tag'>TZS {row['Price']:,}</span>
                        <strong>{row['Name']}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    qty = st.number_input(f"Idadi / Quantity:", min_value=0, max_value=50, step=1, key=f"item_{row['Item_ID']}")
                    if qty > 0:
                        cart[row['Name']] = {'qty': qty, 'price': row['Price']}
    
    with col2:
        st.subheader("Taarifa za Mteja")
        
        st.markdown("<span class='field-label'>👤 Jina Lako Kamili (Full Name):</span>", unsafe_allow_html=True)
        c_name = st.text_input("", placeholder="Mfn: John Doe", key="customer_name_input")
        
        st.markdown("<span class='field-label'>📞 Namba yako ya WhatsApp (Phone Number):</span>", unsafe_allow_html=True)
        c_phone = st.text_input("", placeholder="Mfn: 255615288736", key="customer_phone_input")
        
        st.markdown("<br>", unsafe_allow_html=True)
        delivery = st.checkbox("Je unahitaji usafirishaji nyumbani (Delivery)?")
        
        address = "N/A (Dine-in / Pickup)"
        delivery_fee = 1500 if delivery else 0
        if delivery:
            st.markdown("<span class='field-label'>📍 Sehemu Unayokaa (Delivery Address):</span>", unsafe_allow_html=True)
            address = st.text_area("", placeholder="Weka maelezo ya eneo unalopo...", key="customer_address_input")

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
                # Calculate simple incremental IDs safely
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
                
                row_data = [
                    order_id, c_name, c_phone, items_str, grand_total, 
                    str(delivery), address, 'Pending', timestamp, 'Unassigned'
                ]
                
                with st.spinner("Inatuma oda yako jikoni..."):
                    if add_row_to_sheet("Orders", row_data):
                        st.balloons()
                        st.success(f"🎉 Imefanikiwa! Oda yako imetumwa kwenda 4G_fastfood Kitchen. ID: #{order_id}")
                        # Soft loading reset to refresh page data cleanly
                        st.info("Inapakia upya taarifa...")
                        st.rerun()
                    else:
                        st.error("Oda haikuweza kutumwa. Tafadhali angalia kama umeweka Google App Script vizuri.")

# ==============================================================================
# TAB 2: STAFF DASHBOARD
# ==============================================================================
with tab2:
    st.markdown("<div class='section-header'>Oda Zinazosubiri Jikoni (Pending Verification)</div>", unsafe_allow_html=True)
    
    if not orders_df.empty and 'Status' in orders_df.columns:
        orders_df['Order_ID'] = orders_df['Order_ID'].astype(str)
        # Handle string cleanup case variables
        orders_df['Status'] = orders_df['Status'].astype(str).str.strip()
        pending_orders = orders_df[orders_df['Status'] == 'Pending']
        
        if pending_orders.empty:
            st.info("Safi sana! Hakuna oda zinazosubiri kupikwa kwa sasa.")
        else:
            st.dataframe(pending_orders, use_container_width=True)
            st.info("💡 Badilisha hadhi ya oda yako (Mfn: kutoka 'Pending' kwenda 'Approved') moja kwa moja kwenye Google Sheet yako, na itajisasisha hapa kiotomatiki pindi ukurasa ukipakia!")
    else:
        st.info("Safi sana! Hakuna oda zinazosubiri kupikwa kwa sasa.")

    st.markdown("<div class='section-header'>Oda Zilizothibitishwa (Approved Log View)</div>", unsafe_allow_html=True)
    if not orders_df.empty and 'Status' in orders_df.columns:
        approved_orders = orders_df[orders_df['Status'].astype(str).str.strip() == 'Approved']
        if not approved_orders.empty:
            st.dataframe(approved_orders[['Order_ID', 'Customer_Name', 'Items_Ordered', 'Total_Amount', 'Assigned_Staff']], use_container_width=True)
        else:
            st.write("Hakuna oda zilizothibitishwa bado.")
    else:
        st.write("Hakuna oda zilizothibitishwa bado.")

# ==============================================================================
# TAB 3: FINANCIAL ADMIN
# ==============================================================================
with tab3:
    st.markdown("<div class='section-header'>Mizania ya Fedha & Matumizi</div>", unsafe_allow_html=True)
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        st.subheader("Weka Matumizi Mapya (Log Expense)")
        ex_cat = st.selectbox("Aina ya Matumizi:", ["COGS-Food", "Labor", "Utilities", "Other"])
        ex_vendor = st.text_input("Umejinunulia wapi / Vendor:")
        ex_desc = st.text_input("Maelezo ya Bidhaa / Description:")
        ex_amount = st.number_input("Kiasi kilicholipwa (TZS):", min_value=0)
        
        if st.button("Hifadhi Matumizi Mapya"):
            try:
                if not expenses_df.empty and 'Expense_ID' in expenses_df.columns:
                    valid_ex_ids = pd.to_numeric(expenses_df['Expense_ID'], errors='coerce').dropna()
                    ex_id = int(valid_ex_ids.max() + 1) if not valid_ex_ids.empty else 5001
                else:
                    ex_id = 5001
            except Exception:
                ex_id = 5001
                
            date_str = datetime.now().strftime("%Y-%m-%d")
            expense_row = [ex_id, date_str, ex_cat, ex_vendor, ex_desc, ex_amount]
            
            with st.spinner("Inahifadhi matumizi..."):
                if add_row_to_sheet("Expenses", expense_row):
                    st.success("Matumizi yamehifadhiwa kwenye Google Sheet!")
                    st.rerun()
            
    with col_f2:
        st.subheader("Muhtasari wa Faida na Hasara")
        total_inc = 0
        if not orders_df.empty and 'Status' in orders_df.columns and 'Total_Amount' in orders_df.columns:
            approved_only = orders_df[orders_df['Status'].astype(str).str.strip() == 'Approved']
            total_inc = pd.to_numeric(approved_only['Total_Amount'], errors='coerce').sum()
        
        total_exp = 0
        if not expenses_df.empty and 'Amount' in expenses_df.columns:
            total_exp = pd.to_numeric(expenses_df['Amount'], errors='coerce').sum()
            
        net_prof = total_inc - total_exp
        
        st.metric(label="Jumla ya Mapato kutoka Approved Orders", value=f"TZS {int(total_inc):,}")
        st.metric(label="Jumla ya Matumizi (Expenses)", value=f"TZS {int(total_exp):,}")
        
        if net_prof >= 0:
            st.metric(label="FAIDA KUU (Net Profit)", value=f"TZS {int(net_prof):,}", delta="Mwelekeo Unaridhisha ✅")
        else:
            st.metric(label="HASARA (Net Loss)", value=f"TZS {int(abs(net_prof)):,}", delta="- Hasara Kwenye Biashara")