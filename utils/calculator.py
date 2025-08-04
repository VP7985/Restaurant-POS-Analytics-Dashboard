# utils/calculator.py

GST_RATE = 5.0  # 5% GST

def calculate_bill_details(order_items, discount_amount=0.0):
    """
    Calculates subtotal, GST, and total based on items and a fixed discount amount.
    """
    if not order_items:
        return {"subtotal": 0.0, "discount": 0.0, "gst": 0.0, "total": 0.0}

    subtotal = sum(details['price'] * details['quantity'] for _, details in order_items.items())
    
    taxable_amount = subtotal - discount_amount
    gst = taxable_amount * (GST_RATE / 100) if taxable_amount > 0 else 0
    
    total = taxable_amount + gst
    
    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount_amount, 2),
        "gst": round(gst, 2),
        "total": round(total, 2)
    }

