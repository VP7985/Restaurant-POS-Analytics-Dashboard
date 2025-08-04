# utils/pdf_generator.py
from fpdf import FPDF
import datetime
import os

class PDFGenerator(FPDF):
    """Handles the creation of PDF bills."""
    def header(self):
        # Add the restaurant logo if it exists
        if os.path.exists('assets/logo.png'):
            self.image('assets/logo.png', x=10, y=8, w=30)
        
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'Restaurant Billing POS Invoice', 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Thank you for your business! | Page {self.page_no()}', 0, 0, 'C')

    def generate_bill(self, bill_data):
        """Generates a PDF bill from order data and returns it as bytes."""
        self.add_page()
        self.set_font('Arial', '', 12)
        
        # --- Order Details ---
        self.cell(0, 8, f"Order ID: #{bill_data['order_id']}", 0, 1)
        self.cell(0, 8, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
        self.cell(0, 8, f"Order Type: {bill_data['order_type']}", 0, 1)
        self.cell(0, 8, f"Payment Method: {bill_data['payment_method']}", 0, 1)
        self.ln(10)

        # --- Table Header ---
        self.set_font('Arial', 'B', 12)
        col_widths = {'item': 95, 'qty': 30, 'price': 30, 'total': 35}
        self.cell(col_widths['item'], 10, 'Item', 1, 0, 'C')
        self.cell(col_widths['qty'], 10, 'Quantity', 1, 0, 'C')
        self.cell(col_widths['price'], 10, 'Price', 1, 0, 'C')
        self.cell(col_widths['total'], 10, 'Total', 1, 1, 'C')

        # --- Table Rows ---
        self.set_font('Arial', '', 12)
        for item, details in bill_data['items'].items():
            self.cell(col_widths['item'], 10, item, 1)
            self.cell(col_widths['qty'], 10, str(details['quantity']), 1, 0, 'C')
            self.cell(col_widths['price'], 10, f"Rs.{details['price']:.2f}", 1, 0, 'R')
            self.cell(col_widths['total'], 10, f"Rs.{details['price'] * details['quantity']:.2f}", 1, 1, 'R')

        self.ln(10)

        # --- Totals Section ---
        details = bill_data['details']
        self._draw_total_line('Subtotal:', f"Rs.{details['subtotal']:.2f}")
        self._draw_total_line('Discount:', f"-Rs.{details['discount']:.2f}")
        self._draw_total_line(f'GST (5%):', f"Rs.{details['gst']:.2f}")
        
        self.set_font('Arial', 'B', 14)
        self._draw_total_line('Grand Total:', f"Rs.{details['total']:.2f}")

        # Return the PDF content as bytes
        return self.output(dest='S').encode('latin1')

    def _draw_total_line(self, label, value):
        """
        Helper function to draw a right-aligned line in the totals section.
        This method uses a dummy cell to create space, which is more robust
        for alignment than using set_x().
        """
        # Width of the empty space before the labels
        spacing_width = 125 
        
        # Width of the label and value cells
        label_width = 30
        value_width = 35
        
        self.cell(spacing_width, 8, '', 0, 0) # Dummy cell for spacing
        self.cell(label_width, 8, label, 0, 0, 'R')
        self.cell(value_width, 8, value, 0, 1, 'R')
