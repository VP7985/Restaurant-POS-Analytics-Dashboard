from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from app.models.models import MenuItem, Customer
import os
from flask import current_app

def generate_invoice(order):
    """Generates a PDF invoice for a given order."""
    # This is the corrected, more reliable way to get the instance path
    instance_path = current_app.instance_path
    
    # Ensure the directory for invoices exists within the instance folder
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        
    bill_path = os.path.join(instance_path, f'invoice_{order.id}.pdf')
    c = canvas.Canvas(bill_path, pagesize=letter)
    width, height = letter

    # --- Header ---
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1 * inch, height - 1 * inch, "DineEase POS")
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, height - 1.3 * inch, f"Invoice: #{order.id}")
    c.drawString(1 * inch, height - 1.5 * inch, f"Date: {order.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # --- Customer Details ---
    customer = Customer.query.get(order.customer_id)
    c.drawString(1 * inch, height - 1.9 * inch, "Billed To:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 2.1 * inch, customer.name)
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, height - 2.3 * inch, f"Phone: {customer.phone}")
    c.drawString(1 * inch, height - 2.5 * inch, f"Order Type: {order.order_type}")

    # --- Item Table Header ---
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(1 * inch, height - 2.8 * inch, width - 1 * inch, height - 2.8 * inch)
    c.setFont("Helvetica-Bold", 12)
    y_pos = height - 3.0 * inch
    c.drawString(1.1 * inch, y_pos, "Item")
    c.drawString(4.0 * inch, y_pos, "Quantity")
    c.drawString(5.0 * inch, y_pos, "Price")
    c.drawString(6.5 * inch, y_pos, "Total")
    c.line(1 * inch, y_pos - 0.2 * inch, width - 1 * inch, y_pos - 0.2 * inch)

    # --- Item Table Body ---
    y_pos -= 0.5 * inch
    subtotal = 0
    c.setFont("Helvetica", 11)
    for item in order.items:
        menu_item = MenuItem.query.get(item.menu_item_id)
        item_total = item.quantity * item.price_at_purchase
        subtotal += item_total
        
        c.drawString(1.1 * inch, y_pos, menu_item.name)
        c.drawString(4.3 * inch, y_pos, str(item.quantity))
        c.drawString(5.0 * inch, y_pos, f"₹{item.price_at_purchase:.2f}")
        c.drawString(6.5 * inch, y_pos, f"₹{item_total:.2f}")
        y_pos -= 0.3 * inch

    # --- Totals Section ---
    c.line(4.5 * inch, y_pos, width - 1 * inch, y_pos)
    y_pos -= 0.3 * inch
    gst = subtotal * 0.05
    total = subtotal + gst

    c.setFont("Helvetica", 12)
    c.drawString(5.0 * inch, y_pos, "Subtotal:")
    c.drawString(6.5 * inch, y_pos, f"₹{subtotal:.2f}")
    y_pos -= 0.3 * inch
    
    c.drawString(5.0 * inch, y_pos, "GST (5%):")
    c.drawString(6.5 * inch, y_pos, f"₹{gst:.2f}")
    y_pos -= 0.3 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(5.0 * inch, y_pos, "Total:")
    c.drawString(6.5 * inch, y_pos, f"₹{total:.2f}")

    # --- Footer ---
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2.0, 0.75 * inch, "Thank you for your business!")

    c.save()