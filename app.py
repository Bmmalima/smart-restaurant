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
    
    /* Payslip Receipt Style */
    .receipt-box { background-color: #FFFFFF; border: 2px dashed #333333; padding: 20px; max-width: 450px; margin: 20px auto; font-family: 'Courier New', Courier, monospace; color: #000000; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 4px; }
    .receipt-header { text-align: center; font-weight: bold; border-bottom: 1px dashed #333333; padding-bottom: 10px; margin-bottom: 10px; }
    
    /* Official WhatsApp Icon Button - 'Mhudumu' Styling */
    .floating-wa { position: fixed; bottom: 25px; right: 25px; background-color: #25D366; color: white !important; padding: 14px 22px; border-radius: 50px; font-weight: bold; font-size: 16px; box-shadow: 0px 5px 15px rgba(0,0,0,0.3); z-index: 999999; text-decoration: none !important; display: flex; align-items: center; gap: 8px; }
    .floating-wa:hover { background-color: #128C7E; transform: scale(1.05); transition: 0.3s; }
    </style>
""", unsafe_allow_html=True)

# ----------------- LIVE WHATSAPP WAITER SUPPORT (Mhudumu) -----------------
SUPPORT_PHONE = "255615288736" 
encoded_support_msg = urllib.parse.quote("Habari, nahitaji msaada kutoka kwa Mhudumu wa 4G Fastfood.")
support_url = f"https://api.whatsapp.com/send?phone={SUPPORT_PHONE}&text={encoded_support_msg}"

# Muundo mpya wenye Icon rasmi ya WhatsApp na neno "Mhudumu"
st.markdown(f'''
    <a href="{support_url}" target="_blank" class="floating-wa">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16" style="margin-right:2px;">
            <path d="M13.601 2.326A7.85 7.85 0 0 0 8 0a7.86 7.86 0 0 0-6.691 11.834L0 16l4.24-.1.353.21A7.89 7.89 0 0 0 8 16c4.329 0 7.86-3.523 7.86-7.853 0-2.103-.819-4.08-2.322-5.58H13.6zM8 14.423c-1.954 0-3.87-.52-5.544-1.503l-.398-.235-2.5 1.135.58-2.33-.266-.424A6.53 6.53 0 0 1 1.41 8c0-3.605 2.943-6.533 6.54-6.533 1.748 0 3.393.68 4.631 1.916 1.237 1.237 1.919 2.885 1.919 4.617 0 3.605-2.943 6.533-6.54 6.533m3.608-4.991c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.346.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.73.73 0 0 0-.529.247c-.182.198-.691.677-.691 1.654s.71 1.916.81 2.049c.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232"/>
        </svg>
        Mhudumu
    </a>
''', unsafe_allow_html=True)

# ----------------- GOOGLE APPS SCRIPT CONNECTIVITY VIA API -----------------
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzo5PUYDG9tOHJ_r8IzlUEtJGEQ5kojJAfI6sKm__td6RwbdOEiQaqNEqVZbNJxXeNksg/exec"

ORDER_COLS = ['Order_ID', 'Customer_Name', 'Phone_Number', 'Items_Ordered', 'Total_Amount', 'Delivery_Required', 'Delivery_Address', 'Status', 'Timestamp', 'Assigned_Staff']
EXPENSE_COLS = ['Expense_ID', 'Date', 'Category', 'Vendor', 'Description', 'Amount']
ATTENDANCE_COLS = ['Staff_Name', 'Role', 'Action', 'Timestamp']

def load_data_via_api(worksheet_name, default_cols):
    try:
        response = requests.get(f"{SCRIPT_URL}?sheetName={worksheet_name}", timeout=15)
        if response.status_code == 200:
            data_json = response.json()
            if not data_json or "status" in str(data_json):
                return pd.DataFrame(columns=default_cols)
            df = pd.DataFrame(data_json)
            df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
            df.columns = [c.replace("Order_Id", "Order_ID").replace("Expense_Id", "Expense_ID") for c in df.columns]
            for col in default_cols:
                if col not in df.columns: df[col] = ""
            return df[default_cols]
        return pd.DataFrame(columns=default_cols)
    except Exception:
        return pd.DataFrame(columns=default_cols)

def add_row_to_sheet(worksheet_name, row_list):
    try:
        payload = {"sheetName": worksheet_name, "rowData": [str(x) for x in row_list]}
        response = requests.post(SCRIPT_URL, json=payload, timeout=15)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Imeshindwa kuunganisha na kanzidata: {e}")
        return False

# Kupatia data zote kutoka Google Sheets Live
orders_df = load_data_via_api("Orders", ORDER_COLS)
expenses_df = load_data_via_api("Expenses", EXPENSE_COLS)
attendance_df = load_data_via_api("Attendance", ATTENDANCE_COLS)

# Menu Management (Session State)
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

if 'last_receipt' not in st.session_state:
    st.session_state.last_receipt = None

# Brand Typography
st.markdown("<div class='brand-title'>⚡ 4G_fastfood System</div>", unsafe_allow_html=True)
st.markdown("<div class='brand-subtitle'>Huduma ya Haraka, Chakula Kitamu na Mifumo ya Kisasa</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🛒 Agiza Chakula", "🧑‍🍳 Staff Dashboard", "📊 Financial Admin", "📋 Mahudhurio (Attendance)"])

# ==============================================================================
# TAB 1: CUSTOMER VIEW & PAYSLIP INVOICE GENERATOR
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
                    st.markdown(f"<div class='menu-card'><span class='price-tag'>TZS {int(row['Price']):,}</span><strong>{row['Name']}</strong></div>", unsafe_allow_html=True)
                    qty = st.number_input(f"Idadi / Quantity:", min_value=0, max_value=50, step=1, key=f"item_{row['Item_ID']}")
                    if qty > 0:
                        cart[row['Name']] = {'qty': qty, 'price': row['Price']}
    
    with col2:
        st.subheader("Taarifa za Mteja")
        c_name = st.text_input("Jina Lako Kamili (Full Name):", placeholder="Mfn: John Doe")
        c_phone = st.text_input("Namba yako ya WhatsApp:", placeholder="Mfn: 0615288736")
        
        delivery = st.checkbox("Je unahitaji kusafirishwa nyumbani (Delivery)?")
        address = "N/A"
        delivery_fee = 1500 if delivery else 0
        if delivery:
            address = st.text_area("Sehemu Unayokaa (Delivery Address):")

        st.markdown("---")
        st.write("### 🧾 Muhtasari wa Gharama")
        subtotal = sum(details['qty'] * details['price'] for details in cart.values())
        grand_total = subtotal + delivery_fee
        
        for item, details in cart.items():
            st.write(f"• {item} x {details['qty']} = TZS {details['qty']*details['price']:,}")
        if delivery: st.write(f"• Delivery Fee = TZS {delivery_fee:,}")
        st.markdown(f"### **JUMLA KUU: TZS {grand_total:,}**")
        
        if st.button("Kamilisha Oda sasa", type="primary"):
            if not c_name or not c_phone or not cart:
                st.error("Tafadhali hakikisha umejaza jina, namba na kuchagua chakula kabla ya kutuma!")
            else:
                order_id = int(pd.to_numeric(orders_df['Order_ID'], errors='coerce').max() + 1) if not orders_df.empty else 1001
                items_str = ", ".join([f"{k} (x{v['qty']})" for k, v in cart.items()])
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                row_data = [order_id, c_name, c_phone, items_str, grand_total, str(delivery), address, 'Pending', timestamp, 'Unassigned']
                
                with st.spinner("Inatuma oda yako jikoni..."):
                    if add_row_to_sheet("Orders", row_data):
                        st.balloons()
                        st.session_state.last_receipt = {
                            "id": order_id, "name": c_name, "phone": c_phone,
                            "items": cart, "delivery": delivery_fee, "total": grand_total, "time": timestamp
                        }
                        st.success(f"🎉 Imefanikiwa! Oda yako imetumwa. ID: #{order_id}")
                        time.sleep(1)
                        st.rerun()

        if st.session_state.last_receipt:
            rc = st.session_state.last_receipt
            st.markdown("---")
            st.markdown(f"""
            <div class='receipt-box'>
                <div class='receipt-header'>
                    <h3 style='margin:0;'>4G FASTFOOD</h3>
                    <p style='margin:5px 0; font-size:14px;'>OFFICIAL SALES PAYSLIP</p>
                    <p style='margin:0; font-size:12px;'>Oda ID: #{rc['id']}<br>Tarehe: {rc['time']}</p>
                </div>
                <p style='margin:5px 0;'><b>Mteja:</b> {rc['name']}</p>
                <p style='margin:5px 0;'><b>Simu:</b> {rc['phone']}</p>
                <p style='margin:5px 0;'>----------------------------------</p>
                {"".join([f"<p style='margin:4px 0;'>{k} x{v['qty']} <span style='float:right;'>{v['qty']*v['price']:,}</span></p>" for k, v in rc['items'].items()])}
                {f"<p style='margin:4px 0;'>Delivery Fee <span style='float:right;'>{rc['delivery']:,}</span></p>" if rc['delivery'] > 0 else ""}
                <p style='margin:5px 0;'>----------------------------------</p>
                <h4 style='text-align:right; margin:10px 0 0 0;'>JUMLA KUU: TZS {rc['total']:,}</h4>
                <p style='text-align:center; font-size:11px; margin-top:15px; color:#555;'>Asante kwa kuungana nasi! Chakula chenye viwango. 🍔</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Funga Risiti Hii"):
                st.session_state.last_receipt = None
                st.rerun()

# ==============================================================================
# TAB 2: STAFF KITCHEN MONITOR (APPROVED ORDERS LIVE FIXED)
# ==============================================================================
with tab2:
    st.markdown("<div class='section-header'>Oda Zinazosubiri Jikoni (Pending Verification)</div>", unsafe_allow_html=True)
    if not orders_df.empty and 'Status' in orders_df.columns:
        orders_df['Status_Clean'] = orders_df['Status'].astype(str).str.strip().str.lower()
        pending_orders = orders_df[orders_df['Status_Clean'] == 'pending']
        
        if pending_orders.empty:
            st.info("Safi sana! Hakuna oda zinazosubiri kupikwa kwa sasa.")
        else:
            st.dataframe(pending_orders[ORDER_COLS], use_container_width=True)
            selected_order = st.selectbox("Chagua Order ID ya Kushughulikia:", pending_orders['Order_ID'].astype(str).values)
            handler = st.text_input("Jina la Mhudumu anayeidhinisha (Your Name):")
            
            if st.button("Change Status to APPROVED", type="primary"):
                if not handler: 
                    st.warning("Tafadhali weka jina lako kabla ya kuidhinisha!")
                else:
                    matched_row = pending_orders[pending_orders['Order_ID'].astype(str) == selected_order].iloc[0]
                    
                    # SULUHISHO: Order_ID inalazimishwa kuwa herufi (String) safi bila nafasi ili kulandana na Sheet ya Google
                    update_row = [
                        str(selected_order).strip(), 
                        str(matched_row['Customer_Name']), 
                        str(matched_row['Phone_Number']), 
                        str(matched_row['Items_Ordered']), 
                        str(matched_row['Total_Amount']), 
                        str(matched_row['Delivery_Required']), 
                        str(matched_row['Delivery_Address']), 
                        'Approved', 
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                        str(handler)
                    ]
                    with st.spinner("Inabadilisha na kusave hali ya oda Google Sheet..."):
                        if add_row_to_sheet("Orders", update_row):
                            st.success(f"Oda #{selected_order} imethibitishwa na kurekodiwa vyema!")
                            time.sleep(1)
                            st.rerun()
    else:
        st.info("Hakuna kumbukumbu za oda kwenye mfumo.")

    st.markdown("<div class='section-header'>Oda Zilizothibitishwa Leo (Approved Orders Log)</div>", unsafe_allow_html=True)
    if not orders_df.empty and 'Status' in orders_df.columns:
        approved_orders = orders_df[orders_df['Status'].astype(str).str.strip().str.lower() == 'approved']
        if not approved_orders.empty:
            st.dataframe(approved_orders[ORDER_COLS], use_container_width=True)
        else:
            st.info("Bado hakuna oda zilizoidhinishwa kwa sasa.")

# ==============================================================================
# TAB 3: FINANCIAL ADMIN & ADMIN MENU MANAGER
# ==============================================================================
with tab3:
    st.markdown("<div class='section-header'>🔧 Usimamizi wa Menyu (Admin Access Control)</div>", unsafe_allow_html=True)
    col_adm1, col_adm2 = st.columns(2)
    
    with col_adm1:
        st.subheader("➕ Ongeza Chakula Kipya kwenye Menyu")
        new_name = st.text_input("Jina la Chakula/Kinywaji Kipya:")
        new_cat = st.selectbox("Kundi la Bidhaa:", ["Chakula", "Vitafunio", "Vinywaji"])
        new_price = st.number_input("Bei ya Kuuza kwa TZS:", min_value=0, step=100)
        if st.button("Hifadhi na Uwasilishe Chakula"):
            if new_name:
                nxt_id = len(st.session_state.dynamic_menu) + 1
                new_item = pd.DataFrame([{'Item_ID': nxt_id, 'Name': new_name, 'Category': new_cat, 'Price': new_price}])
                st.session_state.dynamic_menu = pd.concat([st.session_state.dynamic_menu, new_item], ignore_index=True)
                st.success(f"✅ {new_name} kimeongezwa kwenye menyu ya wateja kikamilifu!"); time.sleep(1); st.rerun()
            else: st.error("Weka jina la bidhaa tafadhali!")
            
    with col_adm2:
        st.subheader("❌ Ondoa Chakula Kilichokwisha (Delete/Remove)")
        food_to_delete = st.selectbox("Chagua Bidhaa ya Kuondoa kabisa kwenye Orodha:", st.session_state.dynamic_menu['Name'].values)
        if st.button("Ondoa Kwenye Mfumo Sasa", type="primary"):
            st.session_state.dynamic_menu = st.session_state.dynamic_menu[st.session_state.dynamic_menu['Name'] != food_to_delete]
            st.success(f"🗑️ {food_to_delete} kimeondolewa vizuri kwenye mfumo!"); time.sleep(1); st.rerun()

    st.markdown("<div class='section-header'>💰 Mizania ya Fedha, Faida na Matumizi</div>", unsafe_allow_html=True)
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.subheader("Weka Matumizi Mapya (Log Expense)")
        ex_cat = st.selectbox("Aina ya Matumizi:", ["COGS-Food", "Labor", "Utilities", "Other"])
        ex_vendor = st.text_input("Umenunua wapi / Vendor:")
        ex_desc = st.text_input("Maelezo mafupi ya matumizi:")
        ex_amount = st.number_input("Kiasi kilicholipwa (TZS):", min_value=0)
        if st.button("Hifadhi Matumizi"):
            ex_id = int(pd.to_numeric(expenses_df['Expense_ID'], errors='coerce').max() + 1) if not expenses_df.empty else 5001
            expense_row = [ex_id, datetime.now().strftime("%Y-%m-%d"), ex_cat, ex_vendor, ex_desc, ex_amount]
            if add_row_to_sheet("Expenses", expense_row):
                st.success("Matumizi yamehifadhiwa vyema kwenye mfumo!"); time.sleep(1.5); st.rerun()
    with col_f2:
        st.subheader("Mizania Kuu")
        inc = pd.to_numeric(orders_df[orders_df['Status'].astype(str).str.lower() == 'approved']['Total_Amount'], errors='coerce').sum() if not orders_df.empty else 0
        exp = pd.to_numeric(expenses_df['Amount'], errors='coerce').sum() if not expenses_df.empty else 0
        st.metric("💰 Mapato Halisi (Approved Cash)", f"TZS {int(inc):,}")
        st.metric("📉 Jumla ya Matumizi (Expenses)", f"TZS {int(exp):,}")
        st.metric("📊 FAIDA KUU (Net Profit)", f"TZS {int(inc - exp):,}")

# ==============================================================================
# TAB 4: MAHUDHURIO (ATTENDANCE LOG)
# ==============================================================================
with tab4:
    st.markdown("<div class='section-header'>📋 Mahudhurio ya Wafanyakazi (Live Data Tracking)</div>", unsafe_allow_html=True)
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.subheader("Sajili Mahudhurio")
        staff_name = st.text_input("Andika Jina Lako Kamili (Full Name):", placeholder="Mfn: Amina Juma")
        staff_role = st.selectbox("Chagua Jukumu Lako la Kazi (Role):", ["Mhudumu (Waitress/Waiter)", "Mpishi (Chef)", "Dereva Delivery", "Msimamizi (Admin/Manager)"])
        attendance_action = st.radio("Chagua Kitendo (Action):", ["Clock In (Kuingia Kazini)", "Clock Out (Kutoka Kazini)"])
        
        if st.button("Tuma Mahudhurio Google Sheet", type="primary"):
            if not staff_name:
                st.error("Tafadhali andika jina lako kwanza!")
            else:
                now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                attendance_row = [staff_name, staff_role, attendance_action, now_time]
                with st.spinner("Inatuma mahudhurio..."):
                    if add_row_to_sheet("Attendance", attendance_row):
                        st.success(f"✅ Mahudhurio ya {staff_name} yamehifadhiwa."); time.sleep(1); st.rerun()
                        
    with col_a2:
        st.subheader("Ripoti ya Mahudhurio ya Leo")
        if not attendance_df.empty:
            st.dataframe(attendance_df, use_container_width=True)
        else:
            st.info("Bado hakuna mfanyakazi aliyejisajili leo.")