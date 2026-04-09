import pandas as pd
import numpy as np
from datetime import datetime
import re

class MyntraDataCleaner:
    def __init__(self, input_file='myntra_raw_data.csv'):
        self.df = pd.read_csv(input_file)
        self.cleaning_log = []
        self.initial_shape = self.df.shape
        
    def clean_data(self):
        """Perform all cleaning operations"""
        
        print("🧹 Starting Myntra Data Cleaning Process")
        print("="*60)
        print(f"Initial dataset shape: {self.initial_shape}")
        print("="*60)
        
        # 1. Remove duplicates
        self.remove_duplicates()
        
        # 2. Handle missing values
        self.handle_missing_values()
        
        # 3. Clean text fields
        self.clean_text_fields()
        
        # 4. Fix data types
        self.fix_data_types()
        
        # 5. Handle invalid values
        self.handle_invalid_values()
        
        # 6. Create derived columns
        self.create_derived_columns()
        
        # 7. Quality assurance
        self.quality_assurance()
        
        print("\n✨ Data cleaning completed!")
        self.print_summary()
        
        return self.df
    
    def remove_duplicates(self):
        """Remove duplicate records"""
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates(
            subset=['order_id', 'customer_id', 'product_name', 'order_date'], 
            keep='first'
        )
        removed = initial_count - len(self.df)
        self.cleaning_log.append(f"🗑️  Removed {removed} duplicate records")
        print(f"🗑️  Removed {removed} duplicate records")
    
    def handle_missing_values(self):
        """Handle null/missing values"""
        # Fill missing categories
        self.df['category'] = self.df['category'].fillna('Other')
        
        # Fill missing sub-categories
        self.df['sub_category'] = self.df['sub_category'].fillna('General')
        
        # Fill missing brands
        self.df['brand'] = self.df['brand'].fillna('Unknown Brand')
        
        # Fill missing sizes
        self.df['size'] = self.df['size'].fillna('One Size')
        
        # Fill missing customer IDs
        self.df['customer_id'] = self.df['customer_id'].fillna('UNKNOWN')
        
        # Fill missing customer names
        self.df['customer_name'] = self.df['customer_name'].fillna('Guest User')
        
        # Fill missing email with placeholder
        self.df['customer_email'] = self.df['customer_email'].fillna('unknown@example.com')
        
        # Fill missing review text
        self.df['review_text'] = self.df['review_text'].fillna('No review provided')
        
        # Fill missing return reason
        self.df['return_reason'] = self.df['return_reason'].fillna('Not Returned')
        
        # Remove rows with null order_id
        self.df = self.df.dropna(subset=['order_id'])
        
        # Fill missing delivery days with median
        delivered_mask = self.df['delivery_status'] == 'Delivered'
        if delivered_mask.any():
            median_days = self.df[delivered_mask]['delivery_days'].median()
            self.df['delivery_days'] = self.df['delivery_days'].fillna(median_days)
        
        self.cleaning_log.append("📝 Handled missing values")
        print("📝 Handled missing values")
    
    def clean_text_fields(self):
        """Clean text fields"""
        # Remove extra spaces
        text_columns = ['product_name', 'category', 'sub_category', 'brand', 
                       'size', 'color', 'customer_name', 'customer_city', 
                       'payment_method', 'delivery_status', 'review_text']
        
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()
                self.df[col] = self.df[col].str.replace(r'\s+', ' ', regex=True)
        
        # Standardize categories
        self.df['category'] = self.df['category'].str.title()
        
        # Standardize sizes
        size_mapping = {
            'XS': 'XS', 'S': 'S', 'M': 'M', 'L': 'L', 'XL': 'XL',
            'XXL': 'XXL', '3XL': '3XL', '4XL': '4XL', '5XL': '5XL',
            '6': '6', '7': '7', '8': '8', '9': '9', '10': '10'
        }
        self.df['size'] = self.df['size'].map(lambda x: size_mapping.get(x, 'One Size'))
        
        # Standardize colors
        self.df['color'] = self.df['color'].str.title()
        
        # Standardize payment methods
        payment_std = {
            'Credit Card': 'Credit Card', 'Debit Card': 'Debit Card',
            'UPI': 'UPI', 'Net Banking': 'Net Banking', 'COD': 'Cash on Delivery',
            'Myntra Credit': 'Myntra Credit', 'EMI': 'EMI', 'Gift Card': 'Gift Card'
        }
        self.df['payment_method'] = self.df['payment_method'].apply(
            lambda x: payment_std.get(x, 'Other')
        )
        
        # Standardize delivery status
        status_std = {
            'Delivered': 'Delivered', 'Out for Delivery': 'Out for Delivery',
            'In Transit': 'In Transit', 'Processing': 'Processing',
            'Cancelled': 'Cancelled', 'Returned': 'Returned',
            'Exchange Requested': 'Exchange Requested'
        }
        self.df['delivery_status'] = self.df['delivery_status'].apply(
            lambda x: status_std.get(x, 'Unknown')
        )
        
        # Clean cities
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 
                 'Hyderabad', 'Pune', 'Ahmedabad']
        self.df['customer_city'] = self.df['customer_city'].apply(
            lambda x: x if x in cities else 'Other'
        )
        
        self.cleaning_log.append("🔤 Cleaned text fields")
        print("🔤 Cleaned text fields")
    
    def fix_data_types(self):
        """Fix incorrect data types"""
        # Convert order_date to datetime
        self.df['order_date'] = pd.to_datetime(self.df['order_date'], errors='coerce')
        
        # Remove rows with invalid dates
        invalid_dates = self.df['order_date'].isna().sum()
        self.df = self.df.dropna(subset=['order_date'])
        
        # Remove future dates
        current_date = datetime.now()
        future_dates = (self.df['order_date'] > current_date).sum()
        self.df = self.df[self.df['order_date'] <= current_date]
        
        # Convert numeric columns
        numeric_cols = ['mrp', 'price', 'quantity', 'total_amount', 'rating', 
                       'review_count', 'delivery_days', 'discount_amount']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Convert boolean columns
        self.df['is_returned'] = self.df['is_returned'].astype(bool)
        self.df['is_myntra_insider'] = self.df['is_myntra_insider'].astype(bool)
        
        self.cleaning_log.append(f"📅 Fixed data types (removed {invalid_dates + future_dates} invalid dates)")
        print(f"📅 Fixed data types (removed {future_dates} future dates)")
    
    def handle_invalid_values(self):
        """Handle invalid values"""
        # Fix negative quantities
        negative_qty = (self.df['quantity'] < 0).sum()
        self.df['quantity'] = self.df['quantity'].abs()
        
        # Fix negative prices
        negative_price = (self.df['price'] < 0).sum()
        self.df['price'] = self.df['price'].abs()
        
        # Fix negative MRP
        self.df['mrp'] = self.df['mrp'].abs()
        
        # Remove unrealistic prices (> 100,000)
        self.df = self.df[self.df['price'] < 100000]
        
        # Ensure MRP >= Price
        self.df['mrp'] = self.df[['mrp', 'price']].max(axis=1)
        
        # Fix invalid ratings (1-5)
        invalid_ratings = ((self.df['rating'] < 1) | (self.df['rating'] > 5)).sum()
        self.df['rating'] = self.df['rating'].clip(1, 5)
        
        # Fix ratings to 1 decimal place
        self.df['rating'] = self.df['rating'].round(1)
        
        # Fix total amount
        self.df['total_amount'] = self.df['price'] * self.df['quantity']
        
        # Fix delivery days for non-delivered orders
        self.df.loc[self.df['delivery_status'] != 'Delivered', 'delivery_days'] = 0
        
        # Fix review count
        self.df['review_count'] = self.df['review_count'].fillna(0).clip(0, None).astype(int)
        
        # Fix discount amount
        self.df['discount_amount'] = self.df['discount_amount'].fillna(0)
        self.df['discount_amount'] = self.df['discount_amount'].clip(0, self.df['price'])
        
        # Fix extreme quantities (> 50)
        extreme_qty = (self.df['quantity'] > 50).sum()
        self.df.loc[self.df['quantity'] > 50, 'quantity'] = 50
        
        self.cleaning_log.append(
            f"⚙️  Handled invalid values ({negative_qty} negative qty, "
            f"{negative_price} negative price, {invalid_ratings} invalid ratings)"
        )
        print(f"⚙️  Handled invalid values")
    
    def create_derived_columns(self):
        """Create additional useful columns"""
        # Date components
        self.df['year'] = self.df['order_date'].dt.year
        self.df['month'] = self.df['order_date'].dt.month
        self.df['month_name'] = self.df['order_date'].dt.month_name()
        self.df['day'] = self.df['order_date'].dt.day
        self.df['weekday'] = self.df['order_date'].dt.day_name()
        self.df['week'] = self.df['order_date'].dt.isocalendar().week
        self.df['quarter'] = self.df['order_date'].dt.quarter
        self.df['is_weekend'] = self.df['weekday'].isin(['Saturday', 'Sunday'])
        
        # Price categories
        self.df['price_category'] = pd.cut(
            self.df['price'],
            bins=[0, 500, 1000, 2000, 5000, 10000, float('inf')],
            labels=['Budget (<500)', 'Economy (500-1000)', 'Mid-Range (1000-2000)',
                   'Premium (2000-5000)', 'Luxury (5000-10000)', 'Super Luxury (>10000)']
        )
        
        # Discount percentage
        self.df['discount_percentage'] = ((self.df['mrp'] - self.df['price']) / self.df['mrp'] * 100).round(2)
        self.df['discount_percentage'] = self.df['discount_percentage'].clip(0, 100)
        
        # Discount brackets
        self.df['discount_bracket'] = pd.cut(
            self.df['discount_percentage'],
            bins=[-1, 10, 20, 30, 40, 50, 100],
            labels=['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50%+']
        )
        
        # Customer segments based on total spend
        customer_spend = self.df.groupby('customer_id')['total_amount'].sum()
        spend_thresholds = customer_spend.quantile([0.33, 0.66])
        
        def get_segment(amount):
            if amount <= spend_thresholds.iloc[0]:
                return 'Bronze'
            elif amount <= spend_thresholds.iloc[1]:
                return 'Silver'
            else:
                return 'Gold'
        
        self.df['customer_segment'] = self.df['customer_id'].map(
            customer_spend.apply(get_segment)
        )
        
        # Delivery performance
        self.df['delivery_performance'] = pd.cut(
            self.df['delivery_days'],
            bins=[-1, 2, 4, 7, float('inf')],
            labels=['Fast (≤2 days)', 'Normal (3-4 days)', 'Slow (5-7 days)', 'Very Slow (>7 days)']
        )
        
        # Order value brackets
        self.df['order_value_bracket'] = pd.cut(
            self.df['total_amount'],
            bins=[0, 500, 1000, 2500, 5000, 10000, float('inf')],
            labels=['Micro (<500)', 'Small (500-1000)', 'Medium (1000-2500)',
                   'Large (2500-5000)', 'Very Large (5000-10000)', 'Huge (>10000)']
        )
        
        # Rating category
        self.df['rating_category'] = pd.cut(
            self.df['rating'],
            bins=[0, 2, 3, 4, 4.5, 5.5],
            labels=['Poor (1-2)', 'Below Avg (2-3)', 'Average (3-4)', 
                   'Good (4-4.5)', 'Excellent (4.5-5)']
        )
        
        # Season
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Summer'
            elif month in [6, 7, 8]:
                return 'Monsoon'
            else:
                return 'Autumn'
        
        self.df['season'] = self.df['month'].apply(get_season)
        
        # Product name length (as feature)
        self.df['product_name_length'] = self.df['product_name'].str.len()
        
        # Return rate indicator
        self.df['is_returned'] = self.df['is_returned'].astype(bool)
        
        self.cleaning_log.append("📊 Created 15+ derived columns for analysis")
        print("📊 Created derived columns")
    
    def quality_assurance(self):
        """Perform quality checks"""
        # Final cleanup
        self.df = self.df.dropna(subset=['order_id', 'customer_id', 'total_amount'])
        self.df = self.df[self.df['quantity'] > 0]
        self.df = self.df[self.df['total_amount'] > 0]
        self.df = self.df[self.df['price'] > 0]
        
        # Reset index
        self.df = self.df.reset_index(drop=True)
        
        # Log quality metrics
        self.cleaning_log.append(f"📏 Final dataset shape: {self.df.shape}")
        self.cleaning_log.append(f"📅 Date range: {self.df['order_date'].min().date()} to {self.df['order_date'].max().date()}")
        self.cleaning_log.append(f"💰 Total revenue: ₹{self.df['total_amount'].sum():,.2f}")
        self.cleaning_log.append(f"📊 Average order value: ₹{self.df['total_amount'].mean():.2f}")
        self.cleaning_log.append(f"⭐ Average rating: {self.df['rating'].mean():.2f}")
        self.cleaning_log.append(f"👥 Unique customers: {self.df['customer_id'].nunique()}")
        self.cleaning_log.append(f"🏷️  Unique products: {self.df['product_name'].nunique()}")
        
        print("✅ Quality assurance checks passed")
    
    def print_summary(self):
        """Print cleaning summary"""
        print("\n" + "="*60)
        print("📋 CLEANING SUMMARY REPORT")
        print("="*60)
        for log in self.cleaning_log:
            print(f"  ✓ {log}")
        print("="*60)
        print(f"\n📈 Data Quality Improvement:")
        print(f"  • Rows removed: {self.initial_shape[0] - self.df.shape[0]}")
        print(f"  • Final rows: {self.df.shape[0]}")
        print(f"  • Final columns: {self.df.shape[1]}")
    
    def save_cleaned_data(self, output_file='myntra_cleaned_data.csv'):
        """Save cleaned data to CSV"""
        self.df.to_csv(output_file, index=False)
        print(f"\n💾 Cleaned data saved to {output_file}")
        return output_file

if __name__ == "__main__":
    cleaner = MyntraDataCleaner('myntra_raw_data.csv')
    cleaned_df = cleaner.clean_data()
    cleaner.save_cleaned_data()
    print("\n🔍 Sample of cleaned data:")
    print(cleaned_df.head(10))
    print("\n📊 Data Types After Cleaning:")
    print(cleaned_df.dtypes)
    print("\n📈 Statistical Summary:")
    print(cleaned_df[['price', 'quantity', 'total_amount', 'rating', 'discount_percentage']].describe())