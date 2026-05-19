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

ORDER_COLS = ['Order_ID', 'Customer_Name', 'Phone_Number', 'Items_Ordered', 'Total_Amount', 'Delivery_Required', 'Delivery_Address', 'Status', 'Timestamp', 'Assigned_Staff']
EXPENSE_COLS = ['Expense_ID', 'Date', 'Category', 'Vendor', 'Description', 'Amount']

def load_data(worksheet_name, default_cols):
    try:
        df = conn.read(worksheet=worksheet_name, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=default_cols)
        
        # Kusafisha majina ya nguzo kutoka kwenye lahajakazi (Data normalization)
        df.columns = [str(c).strip().replace(" ", "_").title().replace("Order_Id", "Order_ID").replace("Expense_Id", "Expense_ID") for c in df.columns]
        df.dropna(how='all', inplace=True)
        
        normalized_df = pd.DataFrame()
        for col in default_cols:
            if col in df.columns:
                normalized_df[col] = df[col]
            else:
                normalized_df[col] = ""
                
        if not normalized_df.empty:
            if worksheet_name == "Orders" and 'Order_ID' in normalized_df.columns:
                normalized_df['Order_ID'] = normalized_df['Order_ID'].astype(str).str.strip()
                normalized_df = normalized_df[normalized_df['Order_ID'] != ""]
                normalized_df.drop_duplicates(subset=['Order_ID'], keep='last', inplace=True)
            elif worksheet_name == "Expenses" and 'Expense_ID' in normalized_df.columns:
                normalized_df['Expense_ID'] = normalized_df['Expense_ID'].astype(str).str.strip()
                normalized_df = normalized_df[normalized_df['Expense_ID'] != ""]
                normalized_df.drop_duplicates(subset=['Expense_ID'], keep='last', inplace=True)
                
        return normalized_df
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

# Initialize Operational Data Frames Live
orders_df = load_data("Orders", ORDER_COLS)
expenses_df = load_data("Expenses", EXPENSE_COLS)

# Dynamic Menu State Tracker Setup
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

# ----------------- BRAND HEADERS -----------------
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
        
        st.markdown("<br>", unsafe_allow_html=True)
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
                
                row_data = [
                    order_id, c_name, c_phone, items_str, grand_total, 
                    str(delivery), address, 'Pending', timestamp, 'Unassigned'
                ]
                
                with st.spinner("Inatuma oda yako jikoni..."):
                    if add_row_to_sheet("Orders", row_data):
                        st.balloons()
                        st.success(f"🎉 Imefanikiwa! Oda yako imetumwa kwenda 4G_fastfood Kitchen. ID: #{order_id}")
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
                    if add_row_to_sheet("Orders", update_row):
                        st.success(f"Oda #{selected_order} imehifadhiwa ikiwa imethibitishwa!")
                        st.rerun()
    else:
        st.info("Safi sana! Hakuna oda zinazosubiri kupikwa kwa sasa.")

    st.markdown("<div class='section-header'>Oda Zilizothibitishwa (Approved Log View)</div>", unsafe_allow_html=True)
    if not orders_df.empty and 'Status' in orders_df.columns:
        orders_df['Status_Clean'] = orders_df['Status'].astype(str).str.strip().str.lower()
        approved_orders = orders_df[orders_df['Status_Clean'] == 'approved']
        if not approved_orders.empty:
            st.dataframe(approved_orders[['Order_ID', 'Customer_Name', 'Items_Ordered', 'Total_Amount', 'Assigned_Staff', 'Timestamp']], use_container_width=True)
        else:
            st.write("Hakuna oda zilizothibitishwa bado.")

# ==============================================================================
# TAB 3: FINANCIAL ADMIN & PROFILE TREND REPRESENTATION
# ==============================================================================
with tab3:
    st.markdown("<div class='section-header'>Usimamizi wa Menyu (Add New Foods & Prices)</div>", unsafe_allow_html=True)
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.subheader("Ongeza Chakula Kipya Kwenye Menyu")
        new_food_name = st.text_input("Jina la Chakula (e.g., Wali-Kuku Special):")
        new_food_cat = st.selectbox("Kundi / Category:", ["Chakula", "Vitafunio", "Vinywaji"])
        new_food_price = st.number_input("Bei yake (TZS):", min_value=0, step=100)
        
        if st.button("Hifadhi Chakula Kipya kwenye Mfumo"):
            if not new_food_name:
                st.error("Tafadhali andika jina la chakula!")
            else:
                next_id = len(st.session_state.dynamic_menu) + 1
                new_item = pd.DataFrame([{
                    'Item_ID': next_id, 'Name': new_food_name, 'Category': new_food_cat, 'Price': new_food_price
                }])
                st.session_state.dynamic_menu = pd.concat([st.session_state.dynamic_menu, new_item], ignore_index=True)
                st.success(f"🤩 Safi! {new_food_name} kimeongezwa kwenye menyu ya wateja!")
                st.rerun()
                
    with col_m2:
        st.subheader("Orodha ya Menyu Iliyopo Sasa")
        st.dataframe(st.session_state.dynamic_menu, use_container_width=True)

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
            
        net_prof = total_approved_inc - total_exp
        
        st.metric(label="💰 Jumla ya Mapato Halisi (Approved Orders)", value=f"TZS {int(total_approved_inc):,}")
        st.metric(label="⏳ Thamani ya Oda Zinazosubiri (Pending Orders Value)", value=f"TZS {int(total_pending_inc):,}")
        st.metric(label="📉 Jumla ya Matumizi (Expenses)", value=f"TZS {int(total_exp):,}")
        
        if net_prof >= 0:
            st.metric(label="📊 FAIDA KUU (Net Profit)", value=f"TZS {int(net_prof):,}", delta="Mwelekeo Unaridhisha ✅")
        else:
            st.metric(label="📊 HASARA (Net Loss)", value=f"TZS {int(abs(net_prof)):,}", delta="- Hasara Kwenye Biashara")

    # ==============================================================================
    # DYNAMIC VISUAL CHART REPRESTENTATION (FINANCIAL PROFILE TREND)
    # ==============================================================================
    st.markdown("<div class='section-header'>📈 Mwenendo wa Mapato dhidi ya Matumizi (Financial Trend Chart)</div>", unsafe_allow_html=True)
    
    try:
        timeline_frames = []
        
        if not orders_df.empty and 'Numeric_Amount' in orders_df.columns:
            app_only = orders_df[orders_df['Status_Clean'] == 'approved'].copy()
            if not app_only.empty and 'Timestamp' in app_only.columns:
                app_only['Clean_Date'] = pd.to_datetime(app_only['Timestamp'], errors='coerce').dt.strftime('%Y-%m-%d')
                inc_grouped = app_only.groupby('Clean_Date')['Numeric_Amount'].sum().reset_index()
                inc_grouped.columns = ['Date', 'Income']
                timeline_frames.append(inc_grouped)
                
        if not expenses_df.empty and 'Numeric_Expense' in expenses_df.columns:
            exp_copy = expenses_df.copy()
            if not exp_copy.empty and 'Date' in exp_copy.columns:
                exp_copy['Clean_Date'] = pd.to_datetime(exp_copy['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
                exp_grouped = exp_copy.groupby('Clean_Date')['Numeric_Expense'].sum().reset_index()
                exp_grouped.columns = ['Date', 'Expenses']
                timeline_frames.append(exp_grouped)
                
        if timeline_frames:
            merged_timeline = timeline_frames[0]
            for next_frame in timeline_frames[1:]:
                merged_timeline = pd.merge(merged_timeline, next_frame, on='Date', how='outer')
                
            merged_timeline.fillna(0, inplace=True)
            merged_timeline = merged_timeline.sort_values(by='Date')
            
            # Kumulika mwenendo kwa muda (Cumulative Sum aggregation)
            merged_timeline['Cumulative_Income'] = merged_timeline['Income'].cumsum()
            merged_timeline['Cumulative_Expenses'] = merged_timeline['Expenses'].cumsum()
            merged_timeline['Net_Profit_Trend'] = merged_timeline['Cumulative_Income'] - merged_timeline['Cumulative_Expenses']
            
            chart_output = merged_timeline[['Date', 'Cumulative_Income', 'Cumulative_Expenses', 'Net_Profit_Trend']].copy()
            chart_output.set_index('Date', inplace=True)
            
            st.write("Grafu inayochorwa hapa chini inaonyesha muhtasari wa kibiashara kwa kila tarehe husika:")
            st.area_chart(chart_output, use_container_width=True)
        else:
            st.info("Ingiza data za Oda na Matumizi ili kuona grafu ya mwenendo hapa.")
    except Exception:
        st.info("Grafu itaonekana hapa pindi muundo wa tarehe wa Google Sheets utakapokamilika kikamilifu.")

# ==============================================================================
# TAB 4: STAFF ATTENDANCE TRACKER
# ==============================================================================
with tab4:
    st.markdown("<div class='section-header'>📋 Mahudhurio ya Wafanyakazi (Staff Attendance)</div>", unsafe_allow_html=True)
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.subheader("Sajili Mahudhurio Yako")
        staff_member = st.selectbox("Chagua Jina Lako:", ["Mhudumu 1", "Mpishi Mkuu", "Driver Delivery", "Admin Partner"])
        attendance_action = st.radio("Unachagua kufanya nini?", ["Clock In (Kuingia Kazini)", "Clock Out (Kutoka Kazini)"])
        
        if st.button("Hifadhi Mahudhurio"):
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = pd.DataFrame([{
                'Staff_Name': staff_member, 'Action': attendance_action, 'Timestamp': now_time
            }])
            st.session_state.attendance_log = pd.concat([st.session_state.attendance_log, log_entry], ignore_index=True)
            st.success(f"✅ Vizuri! Umefanikiwa kuweka {attendance_action} kwa ajili ya {staff_member}!")
            st.rerun()
            
    with col_a2:
        st.subheader("Ripoti ya Leo ya Mahudhurio")
        if not st.session_state.attendance_log.empty:
            st.dataframe(st.session_state.attendance_log, use_container_width=True)
        else:
            st.info("Hakuna mfanyakazi aliyeingia au kutoka kazini bado kwa siku ya leo.")