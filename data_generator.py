import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_messy_myntra_data(n_records=2000):
    """Generate messy Myntra sales data simulating real-world scenarios"""
    
    # Myntra product categories
    categories = [
        'Men\'s Clothing', 'Women\'s Clothing', 'Kids\' Wear', 
        'Footwear', 'Accessories', 'Sports Wear', 'Ethnic Wear',
        'Western Wear', 'Lingerie', 'Beauty & Personal Care'
    ]
    
    # Sub-categories
    sub_categories = {
        'Men\'s Clothing': ['T-Shirts', 'Shirts', 'Jeans', 'Trousers', 'Jackets', 'Sweaters'],
        'Women\'s Clothing': ['Dresses', 'Tops', 'Jeans', 'Skirts', 'Blouses', 'Sarees'],
        'Kids\' Wear': ['Boys Clothing', 'Girls Clothing', 'Infant Wear', 'School Uniforms'],
        'Footwear': ['Sports Shoes', 'Casual Shoes', 'Formal Shoes', 'Sandals', 'Flip Flops'],
        'Accessories': ['Watches', 'Bags', 'Belts', 'Sunglasses', 'Jewelry', 'Hats'],
        'Sports Wear': ['Track Pants', 'Sports Bra', 'Gym T-Shirts', 'Shorts', 'Leggings'],
        'Ethnic Wear': ['Kurtas', 'Lehengas', 'Sherwanis', 'Salwar Suits', 'Dhotis'],
        'Western Wear': ['Jeans', 'Trousers', 'Shorts', 'Skirts', 'Jackets'],
        'Lingerie': ['Bras', 'Panties', 'Shapewear', 'Loungewear'],
        'Beauty & Personal Care': ['Makeup', 'Skincare', 'Haircare', 'Fragrances']
    }
    
    # Products with their prices (Myntra style)
    products = {
        # Men's Clothing
        'Roadster T-Shirt': 799, 'HRX Graphic Tee': 699, 'U.S. Polo Shirt': 1299,
        'Levis Jeans': 2499, 'Wrangler Jeans': 2299, 'Jack & Jones Shirt': 1899,
        'Peter England Jacket': 3999, 'Allen Solly Sweater': 2799,
        
        # Women's Clothing
        'Sassafras Dress': 1599, 'Here&Now Top': 899, 'Mast & Harbour Jeans': 1899,
        'Anouk Saree': 3499, 'W for Women Skirt': 1299, 'Vero Moda Blouse': 1799,
        
        # Footwear
        'Puma Sports Shoes': 3999, 'Nike Running Shoes': 5999, 'Adidas Casual': 4499,
        'Bata Sandals': 1299, 'Metro Formal Shoes': 3499, 'Woodland Boots': 5999,
        
        # Accessories
        'Fastrack Watch': 2499, 'Titan Watch': 5999, 'American Tourister Bag': 3999,
        'Ray-Ban Sunglasses': 7999, 'Voylla Jewelry Set': 1499,
        
        # Sports Wear
        'HRX Track Pants': 1299, 'Puma Gym T-Shirt': 999, 'Decathlon Shorts': 799,
        'Nike Leggings': 2499, 'Adidas Sports Bra': 1899,
        
        # Ethnic Wear
        'Biba Kurta': 2499, 'Manyavar Sherwani': 14999, 'W Kurti': 1299,
        'Libas Lehenga': 8999, 'Global Desi Suit': 3999,
        
        # Beauty
        'Nykaa Lipstick': 599, 'Maybelline Foundation': 799, 'Lakme Eye Shadow': 499,
        'Forest Essentials Cream': 2499, 'Plum Skincare Set': 1499
    }
    
    # Brands
    brands = ['Roadster', 'HRX', 'Puma', 'Nike', 'Adidas', 'Levis', 'Wrangler', 
              'Sassafras', 'Anouk', 'Biba', 'Manyavar', 'Fastrack', 'Titan', 
              'Nykaa', 'Maybelline', 'Lakme', 'Vero Moda', 'Jack & Jones']
    
    # Sizes
    sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL', '4XL', '5XL', '6', '7', '8', '9', '10']
    
    # Colors
    colors = ['Red', 'Blue', 'Black', 'White', 'Green', 'Yellow', 'Pink', 'Purple', 
              'Orange', 'Brown', 'Grey', 'Navy Blue', 'Maroon', 'Teal']
    
    # Payment methods
    payment_methods = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'COD', 
                       'Myntra Credit', 'EMI', 'Gift Card']
    
    # Delivery status
    delivery_status = ['Delivered', 'Out for Delivery', 'In Transit', 'Processing', 
                      'Cancelled', 'Returned', 'Exchange Requested']
    
    # Coupons
    coupons = ['MYNTRA10', 'WELCOME20', 'FLAT50', 'FREESHIP', 'SUMMER30', 
               'FESTIVE40', None, None, None, None]  # 50% no coupon
    
    # Generate data
    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1 year of data
    
    for i in range(n_records):
        # Order ID with intentional duplicates (5% chance)
        order_id = f"MY{np.random.randint(100000, 999999)}"
        if i > 0 and np.random.random() < 0.05:
            order_id = data[-1]['order_id']
        
        # Product selection
        product = np.random.choice(list(products.keys()))
        
        # Determine category based on product
        category = np.random.choice(categories)
        sub_category = np.random.choice(sub_categories.get(category, ['General']))
        
        base_price = products[product]
        
        # Add price variations (some wrong prices)
        price = base_price
        if np.random.random() < 0.04:  # 4% wrong prices
            price = base_price * np.random.uniform(0.2, 3.0)
        elif np.random.random() < 0.1:  # 10% discounted prices
            discount = np.random.choice([10, 20, 30, 40, 50, 60, 70, 80])
            price = base_price * (100 - discount) / 100
        
        # MRP (Maximum Retail Price)
        mrp = base_price * np.random.uniform(1.1, 2.0)
        
        quantity = np.random.randint(1, 6)
        
        # Add negative quantities (2% chance)
        if np.random.random() < 0.02:
            quantity = -quantity
        
        # Generate date with some future dates (2% chance)
        random_days = np.random.randint(0, 365)
        order_date = start_date + timedelta(days=random_days)
        if np.random.random() < 0.02:
            order_date = end_date + timedelta(days=np.random.randint(1, 30))
        
        # Brand
        brand = np.random.choice(brands)
        
        # Size and color
        size = np.random.choice(sizes)
        color = np.random.choice(colors)
        
        # Add null values
        if np.random.random() < 0.03:
            brand = None
        if np.random.random() < 0.03:
            category = None
        if np.random.random() < 0.02:
            size = None
        
        # Customer info
        customer_id = f"CUST{np.random.randint(10000, 99999)}"
        customer_name = f"Customer_{np.random.choice(['A','B','C','D','E'])}{np.random.randint(1, 1000)}"
        customer_email = f"user{np.random.randint(1, 10000)}@example.com"
        customer_city = np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 
                                          'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad'])
        
        # Add invalid customer IDs
        if np.random.random() < 0.02:
            customer_id = None
        
        # Rating (1-5) with skew towards higher ratings
        rating = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.08, 0.15, 0.32, 0.4])
        
        # Add invalid ratings
        if np.random.random() < 0.03:
            rating = np.random.choice([0, 6, 10, -1, 100, 3.7, 4.2])
        
        # Reviews
        review_text = np.random.choice([
            "Great product!", "Good quality", "Average", "Not satisfied",
            "Excellent!", "Worth the money", "Delivery was late", "Perfect fit"
        ])
        review_count = np.random.randint(0, 500)
        
        # Payment method
        payment = np.random.choice(payment_methods)
        if np.random.random() < 0.02:
            payment = 'Invalid Method'
        
        # Delivery status
        status = np.random.choice(delivery_status, p=[0.65, 0.1, 0.08, 0.05, 0.05, 0.05, 0.02])
        
        # Delivery days (0-20)
        delivery_days = np.random.randint(0, 21)
        if status == 'Delivered' and delivery_days == 0:
            delivery_days = np.random.randint(1, 10)
        
        # Return/Refund
        is_returned = np.random.random() < 0.1 if status == 'Delivered' else False
        return_reason = np.random.choice([
            'Size issue', 'Quality issue', 'Wrong product', 'Damaged', 
            'Not as described', 'Late delivery'
        ]) if is_returned else None
        
        # Coupon applied
        coupon = np.random.choice(coupons)
        discount_amount = np.random.uniform(0, price * 0.3) if coupon else 0
        
        # Myntra Insider (loyalty program)
        is_insider = np.random.random() < 0.25
        
        # Gender preference
        gender = np.random.choice(['Male', 'Female', 'Unisex'])
        
        # Add extra spaces in product names
        if np.random.random() < 0.05:
            product = ' ' + product + ' '
        
        data.append({
            'order_id': order_id,
            'customer_id': customer_id,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_city': customer_city,
            'product_name': product,
            'category': category,
            'sub_category': sub_category,
            'brand': brand,
            'size': size,
            'color': color,
            'gender': gender,
            'mrp': round(mrp, 2),
            'price': round(price, 2),
            'quantity': quantity,
            'total_amount': round(price * quantity, 2) if quantity > 0 else 0,
            'order_date': order_date,
            'rating': rating,
            'review_text': review_text if np.random.random() < 0.3 else None,
            'review_count': review_count,
            'payment_method': payment,
            'delivery_status': status,
            'delivery_days': delivery_days,
            'is_returned': is_returned,
            'return_reason': return_reason,
            'coupon_applied': coupon,
            'discount_amount': discount_amount,
            'is_myntra_insider': is_insider
        })
    
    df = pd.DataFrame(data)
    
    # Add inconsistent date formats
    df['order_date_str'] = df['order_date'].apply(
        lambda x: x.strftime('%d/%m/%Y') if np.random.random() < 0.05 
        else x.strftime('%Y-%m-%d')
    )
    
    # Add some extra messy data
    # Negative prices (very rare)
    mask = np.random.random(len(df)) < 0.01
    df.loc[mask, 'price'] = -df.loc[mask, 'price']
    
    # Extremely high quantities
    mask = np.random.random(len(df)) < 0.01
    df.loc[mask, 'quantity'] = df.loc[mask, 'quantity'] * 100
    
    return df

def save_to_csv(df, filename='myntra_raw_data.csv'):
    """Save dataframe to CSV"""
    df.to_csv(filename, index=False)
    print(f"✅ Data saved to {filename}")
    return filename

if __name__ == "__main__":
    # Generate 2500 records
    df = generate_messy_myntra_data(2500)
    save_to_csv(df)
    print(f"\n📊 Generated {len(df)} records with messy data")
    print("\n🔍 Sample of messy data:")
    print(df.head(10))
    print("\n📋 Data Info:")
    print(df.info())
    print("\n⚠️ Data Quality Issues:")
    print(f"  • Null values: {df.isnull().sum().sum()}")
    print(f"  • Duplicate orders: {df.duplicated(subset=['order_id']).sum()}")
    print(f"  • Negative quantities: {(df['quantity'] < 0).sum()}")
    print(f"  • Negative prices: {(df['price'] < 0).sum()}")
    print(f"  • Invalid ratings: {((df['rating'] < 1) | (df['rating'] > 5)).sum()}")
    print(f"  • Future dates: {(df['order_date'] > datetime.now()).sum()}")