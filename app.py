import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# Page Configuration for modern look
st.set_page_config(page_title="Smart Restaurant", page_icon="🍲", layout="wide")

# Custom CSS to make a great "frontview" impression
st.markdown("""
    <style>
    .main-title { font-size: 38px; font-weight: bold; color: #E65100; text-align: center; margin-bottom: 20px; }
    .section-header { font-size: 24px; font-weight: bold; color: #37474F; border-bottom: 2px solid #FFE082; padding-bottom: 5px; margin-top: 20px; }
    .menu-card { background-color: #FFF8E1; padding: 15px; border-radius: 10px; border-left: 5px solid #FFA000; margin-bottom: 10px; }
    .success-text { color: #2E7D32; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ----------------- DATABASE INITIALIZATION (Session State) -----------------
if 'menu_df' not in st.session_state:
    st.session_state.menu_df = pd.DataFrame({
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

if 'orders_df' not in st.session_state:
    st.session_state.orders_df = pd.DataFrame(columns=[
        'Order_ID', 'Customer_Name', 'Phone_Number', 'Items_Ordered',
        'Total_Amount', 'Delivery_Required', 'Delivery_Address', 'Status', 'Timestamp', 'Assigned_Staff'
    ])

if 'expenses_df' not in st.session_state:
    st.session_state.expenses_df = pd.DataFrame(columns=['Expense_ID', 'Date', 'Category', 'Vendor', 'Description', 'Amount'])

# ----------------- NAVIGATION TABS -----------------
st.markdown("<div class='main-title'>🍲 Karibu Smart Restaurant System</div>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🛒 Agiza Chakula (Customer Ordering)", "🧑‍🍳 Staff Dashboard", "📊 Financial Admin"])

# ==============================================================================
# TAB 1: CUSTOMER ORDERING VIEW
# ==============================================================================
with tab1:
    st.markdown("<div class='section-header'>Weka Oda Yako Safi Hapa</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Chagua Chakula Kwenye Menu")
        cart = {}
        
        # Group menu by category dynamically
        for category in st.session_state.menu_df['Category'].unique():
            st.write(f"### **{category.upper()}**")
            sub_df = st.session_state.menu_df[st.session_state.menu_df['Category'] == category]
            
            for _, row in sub_df.iterrows():
                # Display food cards nicely
                with st.container():
                    st.markdown(f"""
                    <div class='menu-card'>
                        <strong>{row['Name']}</strong> — <span style='color:#E65100; font-weight:bold;'>TZS {row['Price']:,}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Quantity selector
                    qty = st.number_input(f"Idadi ya {row['Name']}", min_value=0, max_value=20, step=1, key=f"item_{row['Item_ID']}")
                    if qty > 0:
                        cart[row['Name']] = {'qty': qty, 'price': row['Price']}
    
    with col2:
        st.subheader("Taarifa za Usafirishaji")
        c_name = st.text_input("Jina Lako kamili:")
        c_phone = st.text_input("Namba yako ya WhatsApp (Mfano: 255712345678):")
        
        delivery = st.checkbox("Je unahitaji usafirishaji (Delivery)?")
        address = "N/A (Dine-in / Pickup)"
        delivery_fee = 0
        if delivery:
            address = st.text_area("Ingiza Sehemu Unayokaa:")
            delivery_fee = 1500
            st.info("Gharama ya delivery ni TZS 1,500")

        # Order Summary calculation box
        st.markdown("---")
        st.write("### 🧾 Muhtasari wa Oda")
        subtotal = sum(details['qty'] * details['price'] for details in cart.values())
        grand_total = subtotal + delivery_fee
        
        for item, details in cart.items():
            st.write(f"• {item} x {details['qty']} = TZS {details['qty']*details['price']:,}")
        
        if delivery:
            st.write(f"• Usafirishaji = TZS {delivery_fee:,}")
            
        st.markdown(f"### **JUMLA KUU: TZS {grand_total:,}**")
        
        if st.button("Kamilisha Oda / Submit Order", type="primary"):
            if not c_name or not c_phone:
                st.error("Tafadhali jaza Jina na Namba ya Simu kukamilisha oda yako!")
            elif not cart:
                st.error("Oda yako haina chakula chochote bado!")
            else:
                # Add to dataframe
                order_id = len(st.session_state.orders_df) + 1001
                items_str = ", ".join([f"{k} (x{v['qty']})" for k, v in cart.items()])
                
                new_row = pd.DataFrame([{
                    'Order_ID': order_id, 'Customer_Name': c_name, 'Phone_Number': c_phone,
                    'Items_Ordered': items_str, 'Total_Amount': grand_total,
                    'Delivery_Required': delivery, 'Delivery_Address': address,
                    'Status': 'Pending', 'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Assigned_Staff': 'Unassigned'
                }])
                
                st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_row], ignore_index=True)
                st.balloons()
                st.success(f"🎉 Imefanikiwa! Oda yako imepokelewa. ID ni #{order_id}")

# ==============================================================================
# TAB 2: STAFF DASHBOARD
# ==============================================================================
with tab2:
    st.markdown("<div class='section-header'>Oda Zinazosubiri Jikoni (Pending Queue)</div>", unsafe_allow_html=True)
    
    orders = st.session_state.orders_df
    pending_orders = orders[orders['Status'] == 'Pending']
    
    if pending_orders.empty:
        st.info("Hakuna oda mpya zinazosubiri kwa sasa. Kazi nzuri!")
    else:
        for idx, row in pending_orders.iterrows():
            with st.expander(f"📋 Oda #{row['Order_ID']} — Mteja: {row['Customer_Name']}"):
                st.write(f"**Chakula:** {row['Items_Ordered']}")
                st.write(f"**Namba ya Mteja:** {row['Phone_Number']}")
                st.write(f"**Kiasi:** TZS {row['Total_Amount']:,}")
                st.write(f"**Aina:** {'Delivery kwenda: ' + row['Delivery_Address'] if row['Delivery_Required'] else 'Dine-In / Pickup'}")
                
                staff_handler = st.text_input("Jina la Mhudumu:", key=f"staff_{row['Order_ID']}")
                
                if st.button("Thibitisha / Approve Order", key=f"btn_{row['Order_ID']}"):
                    st.session_state.orders_df.loc[st.session_state.orders_df['Order_ID'] == row['Order_ID'], 'Status'] = 'Approved'
                    st.session_state.orders_df.loc[st.session_state.orders_df['Order_ID'] == row['Order_ID'], 'Assigned_Staff'] = staff_handler if staff_handler else "Mhudumu"
                    st.rerun()

    # View Approved Orders with Instant WhatsApp links
    st.markdown("<div class='section-header'>Oda Zilizothibitishwa (Approved Layout)</div>", unsafe_allow_html=True)
    approved_orders = orders[orders['Status'] == 'Approved']
    st.dataframe(approved_orders[['Order_ID', 'Customer_Name', 'Items_Ordered', 'Total_Amount', 'Assigned_Staff']], use_container_width=True)
    
    if not approved_orders.empty:
        st.subheader("Tuma Risiti WhatsApp")
        select_id = st.selectbox("Chagua Order ID ya kutuma:", approved_orders['Order_ID'].values)
        if select_id:
            row_data = approved_orders[approved_orders['Order_ID'] == select_id].iloc[0]
            
            message = (
                f"🟢 *SMART RESTAURANT INVOICE*\n"
                f"----------------------------------------\n"
                f"*Order ID:* #{row_data['Order_ID']}\n"
                f"*Mteja:* {row_data['Customer_Name']}\n"
                f"----------------------------------------\n"
                f"*Vyakula Vilivyoagizwa:*\n"
                f" {row_data['Items_Ordered']}\n"
                f"----------------------------------------\n"
                f"💰 *JUMLA KUU:* TZS {row_data['Total_Amount']:,}\n\n"
                f"Asante kwa kuchagua huduma yetu!"
            )
            
            phone = str(row_data['Phone_Number']).replace("+", "")
            if phone.startswith("0"):
                phone = "255" + phone[1:]
                
            encoded_text = urllib.parse.quote(message)
            wa_link = f"https://api.whatsapp.com/send?phone={phone}&text={encoded_text}"
            
            st.markdown(f"[🔗 BONYEZA HAPA KUTUMA KWA WHATSAPP]({wa_link})", unsafe_allow_html=True)

# ==============================================================================
# TAB 3: FINANCIAL ADMIN MANAGEMENT
# ==============================================================================
with tab3:
    st.markdown("<div class='section-header'>Usimamizi wa Fedha (P&L Tracking)</div>", unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.subheader("Weka Matumizi Mapya (Log Expense)")
        ex_cat = st.selectbox("Category:", ["COGS-Food", "Labor", "Utilities", "Other"])
        ex_vendor = st.text_input("Muuzaji / Vendor:")
        ex_desc = st.text_input("Maelezo / Item details:")
        ex_amount = st.number_input("Kiasi cha Pesa (TZS):", min_value=0)
        
        if st.button("Hifadhi Matumizi"):
            ex_id = len(st.session_state.expenses_df) + 5001
            new_ex = pd.DataFrame([{
                'Expense_ID': ex_id, 'Date': datetime.now().strftime("%Y-%m-%d"),
                'Category': ex_cat, 'Vendor': ex_vendor, 'Description': ex_desc, 'Amount': ex_amount
            }])
            st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_ex], ignore_index=True)
            st.success("Matumizi yamehifadhiwa kwa usalama!")
            
    with col_f2:
        st.subheader("Ripoti ya Faida na Hasara")
        app_orders = st.session_state.orders_df[st.session_state.orders_df['Status'] == 'Approved']
        total_inc = app_orders['Total_Amount'].sum()
        total_exp = st.session_state.expenses_df['Amount'].sum()
        net_prof = total_inc - total_exp
        
        st.metric(label="Jumla ya Mapato (Income)", value=f"TZS {total_inc:,}")
        st.metric(label="Jumla ya Matumizi (Expenses)", value=f"TZS {total_exp:,}")
        
        if net_prof >= 0:
            st.metric(label="FAIDA KUU (Net Profit)", value=f"TZS {net_prof:,}", delta="Mwelekeo Chanya 📈")
        else:
            st.metric(label="HASARA YAKO (Net Loss)", value=f"TZS {abs(net_prof):,}", delta="- Hasara 📉")