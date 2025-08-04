# ui/main_ui.py
# This file contains the complete Streamlit UI, adapted from the new dark-theme design.

import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import base64

# Add project root to Python path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import utility functions
try:
    from utils.db_utils import get_menu_from_db, save_order_to_db, get_sales_report_from_db, update_menu_from_csv
    from utils.calculator import calculate_bill_details
    from utils.pdf_generator import PDFGenerator # Corrected import
except ImportError:
    st.error("FATAL ERROR: Could not import utility modules. Make sure all required files exist in the 'utils' folder.")
    st.stop()

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Restaurant Billing POS",
    page_icon="🍔",
    layout="wide"
)

# --- HELPER FUNCTION TO ENCODE IMAGES ---
def get_image_as_base64(path):
    """Encodes a local image to a base64 string."""
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# --- CSS STYLING (NEW DARK THEME) ---
def load_css():
    """Injects custom CSS from the new Stitch design into the Streamlit app."""
    return """
    <style>
        /* --- NEW DARK THEME VARIABLES --- */
        :root {
            --primary-blue: #699bcd;
            --text-main: #ffffff;
            --text-subtle: #9dadbe;
            --bg-main: #141a1f;
            --bg-secondary: #1f262e;
            --border-color: #3d4d5c;
        }
        
        /* Apply font and background */
        body { font-family: 'Inter', 'Noto Sans', sans-serif; }
        .stApp { background-color: var(--bg-main); color: var(--text-main); }
        
        /* Remove Streamlit Header/Footer */
        [data-testid="stHeader"], [data-testid="stFooter"] { display: none; }
        
        /* General text color */
        h1, h2, h3, h4, h5, p, .stMarkdown, .stDataFrame, .stSelectbox, .stNumberInput, .stRadio > label { 
            color: var(--text-main) !important; 
        }
        
        /* Button Styling */
        .stButton>button {
            background-color: var(--bg-secondary);
            color: var(--text-main);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem; /* Rounded corners for square button */
            font-weight: 700;
            width: 158px; /* Fixed width for square shape */
            height: 158px; /* Fixed height for square shape */
            padding: 0.5rem; /* Reduced padding to fit content */
            transition: all 0.2s ease-in-out;
            display: flex;
            flex-direction: column; /* Stack image and text vertically */
            align-items: center;
            justify-content: center;
            gap: 0.5rem; /* Space between image and text */
            text-align: center;
            font-size: 0.9rem; /* Slightly smaller font for better fit */
            line-height: 1.2; /* Ensure text wraps nicely */
        }
        .stButton>button:hover {
            border-color: var(--primary-blue);
            color: var(--primary-blue);
        }
        .stForm [data-testid="stFormSubmitButton"] button {
            background-color: var(--primary-blue);
            color: var(--bg-main);
            border-radius: 9999px;
            font-weight: 700;
        }
        
        /* Metric cards styling */
        [data-testid="stMetric"] {
            background-color: var(--bg-secondary);
            border-radius: 0.5rem;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
        }
        [data-testid="stMetricLabel"] { color: var(--text-subtle); }
        
        /* Custom card for menu items (retained for reference, not used directly) */
        .menu-card {
            display: flex; align-items: center; gap: 1rem; padding: 1rem;
            border-radius: 0.75rem; border: 1px solid var(--border-color);
            background-color: var(--bg-secondary); cursor: pointer;
            transition: all 0.2s ease-in-out;
            width: 100%;
        }
        .menu-card:hover { border-color: var(--primary-blue); }
        .menu-card img { width: 40px; height: 40px; border-radius: 0.5rem; object-fit: cover; }
        .menu-card h2 { font-weight: 700; color: var(--text-main); font-size: 1rem; }

        /* Dataframes and Tables */
        .stTable, .stDataFrame {
            background-color: var(--bg-secondary);
            border-radius: 0.75rem;
            border: 1px solid var(--border-color);
        }
        thead, th { background-color: var(--bg-secondary) !important; color: var(--text-main) !important; }
        td { color: var(--text-subtle); }
        
        /* Tabs */
        .stTabs [data-baseweb="tab"] { background-color: transparent; }
        .stTabs [data-baseweb="tab-list"] { border-bottom-color: var(--border-color); }
        .stTabs [aria-selected="true"] { border-bottom: 3px solid var(--primary-blue); color: var(--primary-blue); }
        
        /* Form Inputs */
        .stNumberInput input, .stSelectbox select {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            color: var(--text-main);
            padding: 0.75rem;
        }
        .stRadio > label > div:first-child {
            background-color: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 0.75rem;
        }
        .stRadio > label > div:first-child:hover {
            border-color: var(--primary-blue);
        }
    </style>
    """

# --- UI HELPER FUNCTIONS ---
def custom_header():
    """Creates the custom header from the design."""
    st.markdown(f"""
        <header style="display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 2.5rem; border-bottom: 1px solid var(--border-color);">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <svg viewBox="0 0 48 48" fill="var(--text-main)" style="width: 1rem; height: 1rem;"><path d="M42.4379 44C42.4379 44 36.0744 33.9038 41.1692 24C46.8624 12.9336 42.2078 4 42.2078 4L7.01134 4C7.01134 4 11.6577 12.932 5.96912 23.9969C0.876273 33.9029 7.27094 44 7.27094 44L42.4379 44Z"></path></svg>
                <h2 style="color: var(--text-main); font-size: 1.125rem; font-weight: 700;">Restaurant Billing POS</h2>
            </div>
        </header>
    """, unsafe_allow_html=True)

# --- UI PAGE FUNCTIONS ---
def order_page():
    """Renders the 'Place Order' page."""
    menu_col, bill_col = st.columns([1, 1])

    with menu_col:
        st.markdown('<h2 style="font-size: 1.375rem; font-weight: 700; padding: 1.25rem 1rem 0.75rem;">Menu</h2>', unsafe_allow_html=True)
        menu_data = get_menu_from_db()
        if menu_data.empty:
            st.warning("Menu is empty. Please add items via the Admin Panel.")
            return

        categories = menu_data['category'].unique()
        menu_tabs = st.tabs(categories.tolist())
        
        for i, category in enumerate(categories):
            with menu_tabs[i]:
                items_in_category = menu_data[menu_data['category'] == category]
                st.markdown('<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(158px, 1fr)); gap: 0.75rem; padding: 1rem;">', unsafe_allow_html=True)
                for _, item in items_in_category.iterrows():
                    image_b64 = get_image_as_base64(item['image_path'])
                    image_html = f'<img src="data:image/jpeg;base64,{image_b64}" style="width: 40px; height: 40px; border-radius: 0.5rem; object-fit: cover;">' if image_b64 else '<div style="width: 40px; height: 40px; border-radius: 0.5rem; background-color: var(--border-color);"></div>'
                    
                    if st.button(
                        f'![{item["name"]}](data:image/jpeg;base64,{image_b64}) {item["name"]}' if image_b64 else f'{item["name"]}',
                        key=f"add_{item['id']}",
                        use_container_width=True,
                        help=f"Add {item['name']} to order"
                    ):
                        if item['name'] in st.session_state.current_order:
                            st.session_state.current_order[item['name']]['quantity'] += 1
                        else:
                            st.session_state.current_order[item['name']] = {'quantity': 1, 'price': item['price']}
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    with bill_col:
        st.markdown('<h2 style="font-size: 1.375rem; font-weight: 700; padding: 1.25rem 1rem 0.75rem;">Current Bill</h2>', unsafe_allow_html=True)
        
        if not st.session_state.current_order:
            st.info("Your order is empty.")
        else:
            order_list = []
            for name, details in list(st.session_state.current_order.items()):
                total = details['price'] * details['quantity']
                order_list.append([name, details['quantity'], f"₹{total:.2f}"])
            
            bill_df = pd.DataFrame(order_list, columns=["Item", "Qty", "Total"])
            st.table(bill_df)

        st.markdown('<h2 style="font-size: 1.375rem; font-weight: 700; padding: 1.25rem 1rem 0.75rem;">Finalize Order</h2>', unsafe_allow_html=True)

        # CORRECTED LOGIC: Get discount value BEFORE calculating and displaying the bill
        discount = st.number_input("Discount (₹)", min_value=0.0, step=5.0, format="%.2f", key="discount_input")
        
        bill_details = calculate_bill_details(st.session_state.current_order, discount)
        
        st.markdown(f"""
        <div style="padding: 1rem;">
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;"><p style="color: var(--text-subtle);">Subtotal</p><p>₹{bill_details['subtotal']:.2f}</p></div>
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;"><p style="color: var(--text-subtle);">Discount</p><p>-₹{bill_details['discount']:.2f}</p></div>
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;"><p style="color: var(--text-subtle);">GST (5%)</p><p>₹{bill_details['gst']:.2f}</p></div>
            <hr style="border-color: var(--border-color); margin: 0.5rem 0;" />
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; font-weight: 700; font-size: 1.125rem;"><p>Grand Total</p><p>₹{bill_details['total']:.2f}</p></div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("order_form"):
            order_type = st.radio("Order Type", ["Dine-In", "Takeaway"], horizontal=True)
            payment_method = st.selectbox("Payment Method", ["Cash", "Card", "UPI"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Place Order & Generate Bill", use_container_width=True):
                    if not st.session_state.current_order:
                        st.warning("Cannot place an empty order.")
                    else:
                        # The bill_details are already calculated with the correct discount
                        order_to_save = {
                            'items': st.session_state.current_order, 'details': bill_details,
                            'order_type': order_type, 'payment_method': payment_method
                        }
                        order_id = save_order_to_db(order_to_save)
                        st.success(f"Order #{order_id} placed successfully!")
                        st.session_state.last_bill = {**order_to_save, 'order_id': order_id}
                        st.session_state.current_order = {}
                        st.rerun()
            with col2:
                if st.form_submit_button("Clear Order", use_container_width=True, type="secondary"):
                    st.session_state.current_order = {}
                    st.session_state.pop('last_bill', None)
                    st.rerun()

        if st.session_state.get("last_bill"):
            st.markdown("---")
            last_bill = st.session_state.last_bill
            st.subheader(f"Download Bill for Order #{last_bill['order_id']}")
            pdf = PDFGenerator()
            pdf_bytes = pdf.generate_bill(last_bill)
            st.download_button("Download Bill (PDF)", pdf_bytes, f"bill_{last_bill['order_id']}.pdf", "application/pdf", use_container_width=True)


def admin_page():
    """Renders the 'Admin Panel' page."""
    st.markdown('<h2 style="font-size: 2rem; font-weight: 700; padding: 1.25rem 0;">Dashboard</h2>', unsafe_allow_html=True)
    
    summary, top_items, by_cat, by_pay = get_sales_report_from_db("Monthly")
    total_sales = summary['Total Sales'].sum() if not summary.empty else 0
    total_orders = summary['Total Orders'].sum() if not summary.empty else 0
    avg_sale = total_sales / total_orders if total_orders > 0 else 0

    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Total Sales (This Month)", f"₹{total_sales:,.2f}")
    kpi_cols[1].metric("Total Orders (This Month)", f"{total_orders}")
    kpi_cols[2].metric("Average Sale Value", f"₹{avg_sale:,.2f}")
    
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📊 Visual Analytics", "📈 Detailed Reports", "📋 Menu Management"])

    with tab1:
        st.subheader("Visual Analytics")
        col1, col2 = st.columns(2)
        with col1:
            if not by_cat.empty:
                fig_cat = px.pie(by_cat, names='Category', values='Total Quantity', title='Sales by Category', hole=0.4)
                fig_cat.update_layout(template="plotly_dark", legend_orientation="h")
                st.plotly_chart(fig_cat, use_container_width=True)
        with col2:
            if not by_pay.empty:
                fig_pay = px.pie(by_pay, names='Payment Method', values='Transaction Count', title='Sales by Payment Method', hole=0.4)
                fig_pay.update_layout(template="plotly_dark", legend_orientation="h")
                st.plotly_chart(fig_pay, use_container_width=True)

    with tab2:
        st.subheader("Detailed Sales Reports")
        period = st.selectbox("Report Period", ["Daily", "Weekly", "Monthly"])
        summary, top_items, _, _ = get_sales_report_from_db(period)
        
        st.markdown(f"##### {period} Sales Summary")
        if not summary.empty:
            st.dataframe(summary, use_container_width=True, hide_index=True)
            fig_trend = px.line(summary, x='Period', y='Total Sales', title=f'{period} Sales Trend', markers=True)
            fig_trend.update_layout(template="plotly_dark")
            st.plotly_chart(fig_trend, use_container_width=True)
        
        st.markdown("##### Top 10 Most Sold Items")
        st.dataframe(top_items, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Menu Management")
        uploaded_file = st.file_uploader("Upload new menu.csv", type=["csv"])
        if uploaded_file:
            success, message = update_menu_from_csv(uploaded_file)
            st.toast(message, icon="✅" if success else "❌")
        
        st.markdown("##### Current Menu")
        st.dataframe(get_menu_from_db(), use_container_width=True, hide_index=True)

# --- MAIN APP ROUTING ---
def main():
    """Main function to control the app's navigation and state."""
    st.markdown(load_css(), unsafe_allow_html=True)
    custom_header()

    if 'current_order' not in st.session_state: st.session_state.current_order = {}
    if 'active_page' not in st.session_state: st.session_state.active_page = "New Order"

    pages = {"New Order": order_page, "Admin Panel & Overview": admin_page}
    
    st.session_state.active_page = st.radio(
        "Navigation", list(pages.keys()), horizontal=True, 
        label_visibility="collapsed", key="nav_radio"
    )

    pages[st.session_state.active_page]()

if __name__ == "__main__":
    main()
