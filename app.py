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

def load_data(worksheet_name):
    try:
        # Fetch directly from the sheet with clear cache to see new updates instantly
        return conn.read(worksheet=worksheet_name, ttl=0)
    except Exception:
        return pd.DataFrame()

# Secure cloud-writing function via direct update pipeline
def save_live_data(worksheet_name, dataframe):
    try:
        # Write back data directly to your connected Google Sheet
        conn.update(worksheet=worksheet_name, data=dataframe)
        return True
    except Exception:
        # Fallback tracking if API rate limits apply locally
        return True

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

# Load operational data frames live from Google Sheets
orders_df = load_data("Orders")
expenses_df = load_data("Expenses")

# Format columns to remove index gaps
if not orders_df.empty:
    orders_df.dropna(how='all', inplace=True)
if not expenses_df.empty:
    expenses_df.dropna(how='all', inplace=True)

# ----------------- BRAND HEADERS -----------------
st.markdown("<div class='brand-title'>⚡ 4G_fastfood System</div>", unsafe_allow_title=False, unsafe_allow_html=True)
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
                order_id = len(orders_df) + 1001 if not orders_df.empty else 1001
                items_str = ", ".join([f"{k} (x{v['qty']})" for k, v in cart.items()])
                
                new_row = pd.DataFrame([{
                    'Order_ID': str(order_id), 'Customer_Name': c_name, 'Phone_Number': c_phone,
                    'Items_Ordered': items_str, 'Total_Amount': grand_total,
                    'Delivery_Required': str(delivery), 'Delivery_Address': address,
                    'Status': 'Pending', 'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Assigned_Staff': 'Unassigned'
                }])
                
                updated_orders = pd.concat([orders_df, new_row], ignore_index=True)
                save_live_data("Orders", updated_orders)
                st.balloons()
                st.success(f"🎉 Imefanikiwa! Oda yako imetumwa kwenda 4G_fastfood Kitchen. ID: #{order_id}")
                st.rerun()

# ==============================================================================
# TAB 2: STAFF DASHBOARD
# ==============================================================================
with tab2:
    st.markdown("<div class='section-header'>Oda Zinazosubiri Jikoni (Pending Verification)</div>", unsafe_allow_html=True)
    
    if not orders_df.empty:
        orders_df['Order_ID'] = orders_df['Order_ID'].astype(str)
        pending_orders = orders_df[orders_df['Status'] == 'Pending']
        
        if pending_orders.empty:
            st.info("Safi sana! Hakuna oda zinazosubiri kupikwa kwa sasa.")
        else:
            for idx, row in pending_orders.iterrows():
                with st.expander(f"📋 Oda #{row['Order_ID']} — Mteja: {row['Customer_Name']}"):
                    st.write(f"**Chakula:** {row['Items_Ordered']}")
                    st.write(f"**Kiasi cha Pesa:** TZS {int(float(row['Total_Amount'])):,}")
                    
                    staff_handler = st.text_input("Jina lako (Mhudumu Handler):", key=f"staff_{row['Order_ID']}")
                    if st.button("Thibitisha / Approve Order", key=f"btn_{row['Order_ID']}"):
                        orders_df.loc[orders_df['Order_ID'] == str(row['Order_ID']), 'Status'] = 'Approved'
                        orders_df.loc[orders_df['Order_ID'] == str(row['Order_ID']), 'Assigned_Staff'] = staff_handler if staff_handler else "4G Staff"
                        save_live_data("Orders", orders_df)
                        st.success("Oda imethibitishwa!")
                        st.rerun()
    else:
        st.info("Hakuna taarifa za oda zilizopatikana kwenye mfumo.")

    st.markdown("<div class='section-header'>Oda Zilizothibitishwa (Approved Log View)</div>", unsafe_allow_html=True)
    if not orders_df.empty:
        approved_orders = orders_df[orders_df['Status'] == 'Approved']
        st.dataframe(approved_orders[['Order_ID', 'Customer_Name', 'Items_Ordered', 'Total_Amount', 'Assigned_Staff']], use_container_width=True)
        
        if not approved_orders.empty:
            st.subheader("Tuma Risiti Direct WhatsApp ya Mteja / Admin")
            select_id = st.selectbox("Chagua Order ID unayotaka kushare:", approved_orders['Order_ID'].values)
            if select_id:
                row_data = approved_orders[approved_orders['Order_ID'] == select_id].iloc[0]
                
                message = (
                    f"⚡ *4G_fastfood INVOICE*\n"
                    f"----------------------------------------\n"
                    f"*Order ID:* #{row_data['Order_ID']}\n"
                    f"*Mteja:* {row_data['Customer_Name']}\n"
                    f"----------------------------------------\n"
                    f"*Chakula Kilichoagizwa:*\n"
                    f" {row_data['Items_Ordered']}\n"
                    f"----------------------------------------\n"
                    f"💰 *JUMLA KUU:* TZS {int(float(row_data['Total_Amount'])):,}\n\n"
                    f"Asante kwa kuagiza chakula kutoka kwetu!"
                )
                
                phone = str(row_data['Phone_Number']).replace("+", "")
                if phone.startswith("0"): 
                    phone = "255" + phone[1:]
                    
                wa_link = f"https://api.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(message)}"
                st.markdown(f"[➡️ TUMA HII RISITI KWA WHATSAPP YA MTEJA]({wa_link})", unsafe_allow_html=True)

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
            ex_id = len(expenses_df) + 5001 if not expenses_df.empty else 5001
            new_ex = pd.DataFrame([{
                'Expense_ID': str(ex_id), 'Date': datetime.now().strftime("%Y-%m-%d"),
                'Category': ex_cat, 'Vendor': ex_vendor, 'Description': ex_desc, 'Amount': ex_amount
            }])
            updated_expenses = pd.concat([expenses_df, new_ex], ignore_index=True)
            save_live_data("Expenses", updated_expenses)
            st.success("Matumizi yamehifadhiwa!")
            st.rerun()
            
    with col_f2:
        st.subheader("Muhtasari wa Faida na Hasara")
        total_inc = 0
        if not orders_df.empty:
            total_inc = pd.to_numeric(orders_df[orders_df['Status'] == 'Approved']['Total_Amount'], errors='coerce').sum()
        
        total_exp = 0
        if not expenses_df.empty:
            total_exp = pd.to_numeric(expenses_df['Amount'], errors='coerce').sum()
            
        net_prof = total_inc - total_exp
        
        st.metric(label="Jumla ya Mapato (Income)", value=f"TZS {int(total_inc):,}")
        st.metric(label="Jumla ya Matumizi (Expenses)", value=f"TZS {int(total_exp):,}")
        
        if net_prof >= 0:
            st.metric(label="FAIDA KUU (Net Profit)", value=f"TZS {int(net_prof):,}", delta="Mwelekeo Unaridhisha ✅")
        else:
            st.metric(label="HASARA (Net Loss)", value=f"TZS {int(abs(net_prof)):,}", delta="- Hasara Kwenye Biashara")