import mysql.connector
from mysql.connector import Error
import pandas as pd
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings('ignore')

class MyntraDatabase:
    def __init__(self, host='localhost', database='myntra_db', 
                 user='root', password='SAN123'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.engine = None
        
    def create_connection(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            print("✅ Connected to MySQL server")
            return True
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return False
    
    def create_database(self):
        """Create database if not exists"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"✅ Database '{self.database}' created/verified")
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    def create_table(self):
        """Create Myntra sales table"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {self.database}")
            
            create_table_query = """
            CREATE TABLE IF NOT EXISTS myntra_sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id VARCHAR(50) NOT NULL,
                customer_id VARCHAR(50),
                customer_name VARCHAR(200),
                customer_email VARCHAR(200),
                customer_city VARCHAR(100),
                product_name VARCHAR(200),
                category VARCHAR(100),
                sub_category VARCHAR(100),
                brand VARCHAR(100),
                size VARCHAR(20),
                color VARCHAR(50),
                gender VARCHAR(20),
                mrp DECIMAL(10, 2),
                price DECIMAL(10, 2),
                quantity INT,
                total_amount DECIMAL(10, 2),
                order_date DATE,
                rating DECIMAL(3, 1),
                review_text TEXT,
                review_count INT,
                payment_method VARCHAR(50),
                delivery_status VARCHAR(50),
                delivery_days INT,
                is_returned BOOLEAN,
                return_reason VARCHAR(200),
                coupon_applied VARCHAR(50),
                discount_amount DECIMAL(10, 2),
                is_myntra_insider BOOLEAN,
                
                -- Derived columns
                year INT,
                month INT,
                month_name VARCHAR(20),
                day INT,
                weekday VARCHAR(20),
                week INT,
                quarter INT,
                is_weekend BOOLEAN,
                price_category VARCHAR(50),
                discount_percentage DECIMAL(5, 2),
                discount_bracket VARCHAR(20),
                customer_segment VARCHAR(20),
                delivery_performance VARCHAR(30),
                order_value_bracket VARCHAR(30),
                rating_category VARCHAR(30),
                season VARCHAR(10),
                product_name_length INT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Indexes for better performance
                INDEX idx_order_date (order_date),
                INDEX idx_category (category),
                INDEX idx_customer (customer_id),
                INDEX idx_delivery_status (delivery_status),
                INDEX idx_brand (brand),
                INDEX idx_city (customer_city),
                INDEX idx_price_category (price_category),
                INDEX idx_rating (rating)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            cursor.execute(create_table_query)
            print("✅ Table 'myntra_sales' created/verified")
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error creating table: {e}")
            return False
    
    def create_sqlalchemy_engine(self):
        """Create SQLAlchemy engine for pandas"""
        try:
            connection_string = f'mysql+mysqlconnector://{self.user}:{self.password}@{self.host}/{self.database}'
            self.engine = create_engine(connection_string, echo=False)
            print("✅ SQLAlchemy engine created")
            return True
        except Exception as e:
            print(f"❌ Error creating engine: {e}")
            return False
    
    def insert_data(self, df):
        """Insert cleaned data into database"""
        try:
            if not self.engine:
                self.create_sqlalchemy_engine()
            
            # Insert data
            df.to_sql('myntra_sales', con=self.engine, 
                     if_exists='replace', index=False,
                     chunksize=1000)
            print(f"✅ Successfully inserted {len(df)} records into database")
            return True
        except Exception as e:
            print(f"❌ Error inserting data: {e}")
            return False
    
    def load_data_from_db(self):
        """Load data from database to DataFrame"""
        try:
            if not self.engine:
                self.create_sqlalchemy_engine()
            
            query = "SELECT * FROM myntra_sales"
            df = pd.read_sql(query, self.engine)
            print(f"📊 Loaded {len(df)} records from database")
            return df
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    def get_summary_stats(self):
        """Get summary statistics from database"""
        try:
            with self.engine.connect() as conn:
                # Total metrics
                total_orders = pd.read_sql("SELECT COUNT(*) as count FROM myntra_sales", conn)['count'][0]
                total_revenue = pd.read_sql("SELECT SUM(total_amount) as revenue FROM myntra_sales", conn)['revenue'][0] or 0
                avg_order = pd.read_sql("SELECT AVG(total_amount) as avg FROM myntra_sales", conn)['avg'][0] or 0
                avg_rating = pd.read_sql("SELECT AVG(rating) as rating FROM myntra_sales", conn)['rating'][0] or 0
                
                # Category performance
                top_categories = pd.read_sql("""
                    SELECT category, 
                           COUNT(*) as orders, 
                           SUM(total_amount) as revenue,
                           AVG(rating) as avg_rating
                    FROM myntra_sales
                    GROUP BY category
                    ORDER BY revenue DESC
                    LIMIT 5
                """, conn)
                
                # Brand performance
                top_brands = pd.read_sql("""
                    SELECT brand, 
                           COUNT(*) as orders, 
                           SUM(total_amount) as revenue
                    FROM myntra_sales
                    GROUP BY brand
                    ORDER BY revenue DESC
                    LIMIT 5
                """, conn)
                
                # City wise sales
                city_sales = pd.read_sql("""
                    SELECT customer_city, 
                           COUNT(*) as orders, 
                           SUM(total_amount) as revenue
                    FROM myntra_sales
                    GROUP BY customer_city
                    ORDER BY revenue DESC
                    LIMIT 5
                """, conn)
                
                return {
                    'total_orders': total_orders,
                    'total_revenue': total_revenue,
                    'avg_order_value': avg_order,
                    'avg_rating': avg_rating,
                    'top_categories': top_categories,
                    'top_brands': top_brands,
                    'city_sales': city_sales
                }
        except Exception as e:
            print(f"❌ Error getting summary: {e}")
            return None
    
    def create_views(self):
        """Create useful database views"""
        try:
            with self.engine.connect() as conn:
                # Monthly sales summary view
                conn.execute(text("""
                    CREATE OR REPLACE VIEW monthly_sales_summary AS
                    SELECT 
                        year,
                        month,
                        month_name,
                        COUNT(*) as total_orders,
                        SUM(total_amount) as total_revenue,
                        AVG(total_amount) as avg_order_value,
                        AVG(rating) as avg_rating,
                        COUNT(DISTINCT customer_id) as unique_customers
                    FROM myntra_sales
                    GROUP BY year, month, month_name
                    ORDER BY year DESC, month DESC
                """))
                
                # Category performance view
                conn.execute(text("""
                    CREATE OR REPLACE VIEW category_performance AS
                    SELECT 
                        category,
                        COUNT(*) as total_orders,
                        SUM(total_amount) as total_revenue,
                        AVG(rating) as avg_rating,
                        AVG(discount_percentage) as avg_discount,
                        SUM(is_returned) as total_returns
                    FROM myntra_sales
                    GROUP BY category
                    ORDER BY total_revenue DESC
                """))
                
                print("✅ Database views created successfully")
                return True
        except Exception as e:
            print(f"⚠️  Could not create views: {e}")
            return False
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Database connection closed")

def setup_complete_database(csv_file='myntra_cleaned_data.csv'):
    """Complete database setup process"""
    print("\n" + "="*60)
    print("🚀 MYNTRA DATABASE SETUP")
    print("="*60)
    
    # Initialize database (UPDATE PASSWORD HERE!)
    db = MyntraDatabase(password='SAN123')  # Change this!
    
    # Connect and setup
    if db.create_connection():
        db.create_database()
        db.create_table()
        
        # Load cleaned data
        try:
            df = pd.read_csv(csv_file)
            print(f"📁 Loaded {len(df)} records from {csv_file}")
            
            # Insert data
            db.insert_data(df)
            
            # Create views
            db.create_views()
            
            # Get summary
            summary = db.get_summary_stats()
            if summary:
                print("\n" + "="*60)
                print("📊 DATABASE SUMMARY REPORT")
                print("="*60)
                print(f"  • Total Orders: {summary['total_orders']:,}")
                print(f"  • Total Revenue: ₹{summary['total_revenue']:,.2f}")
                print(f"  • Average Order Value: ₹{summary['avg_order_value']:.2f}")
                print(f"  • Average Rating: {summary['avg_rating']:.2f} ⭐")
                
                print("\n  🏆 Top Categories by Revenue:")
                for _, row in summary['top_categories'].iterrows():
                    print(f"    • {row['category']}: ₹{row['revenue']:,.2f} ({row['orders']} orders, {row['avg_rating']:.1f}⭐)")
                
                print("\n  🏷️  Top Brands by Revenue:")
                for _, row in summary['top_brands'].iterrows():
                    print(f"    • {row['brand']}: ₹{row['revenue']:,.2f} ({row['orders']} orders)")
                
                print("\n  🏙️  Top Cities by Revenue:")
                for _, row in summary['city_sales'].iterrows():
                    print(f"    • {row['customer_city']}: ₹{row['revenue']:,.2f} ({row['orders']} orders)")
            
            db.close_connection()
            print("\n✅ Database setup completed successfully!")
            
        except FileNotFoundError:
            print(f"❌ File {csv_file} not found!")
            print("Please run myntra_data_cleaner.py first to generate cleaned data.")
    else:
        print("\n❌ Database setup failed. Please check:")
        print("  1. MySQL is running")
        print("  2. Username and password are correct")
        print("  3. Update password in MyntraDatabase class")

if __name__ == "__main__":
    setup_complete_database()