import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Myntra Sales Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #FF3E6C 0%, #FF5277 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .myntra-pink {
        color: #FF3E6C;
    }
    </style>
""", unsafe_allow_html=True)

class MyntraDashboard:
    def __init__(self):
        self.df = None
        self.engine = None
        
    def connect_to_database(self):
        """Connect to MySQL database"""
        try:
            # Update with your MySQL credentials
            connection_string = 'mysql+mysqlconnector://root:SAN123@localhost/myntra_db'
            self.engine = create_engine(connection_string)
            self.df = pd.read_sql("SELECT * FROM myntra_sales", self.engine)
            return True
        except Exception as e:
            st.error(f"Error connecting to database: {e}")
            return False
    
    def load_local_data(self):
        """Load data from local CSV"""
        try:
            self.df = pd.read_csv('myntra_cleaned_data.csv')
            return True
        except:
            return False
    
    def load_data(self):
        """Load data from database or local"""
        with st.spinner("Loading Myntra sales data..."):
            if not self.connect_to_database():
                if self.load_local_data():
                    st.success("✅ Loaded data from local CSV file")
                    return True
                else:
                    st.error("❌ Could not load data from any source")
                    return False
            else:
                st.success("✅ Connected to MySQL database successfully!")
                return True
    
    def display_metrics(self):
        """Display key metrics"""
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        total_revenue = self.df['total_amount'].sum()
        total_orders = len(self.df)
        avg_order = total_revenue / total_orders if total_orders > 0 else 0
        avg_rating = self.df['rating'].mean()
        unique_customers = self.df['customer_id'].nunique()
        unique_products = self.df['product_name'].nunique()
        
        metrics = [
            ("Total Revenue", f"₹{total_revenue:,.2f}"),
            ("Total Orders", f"{total_orders:,}"),
            ("Avg Order Value", f"₹{avg_order:.2f}"),
            ("Avg Rating", f"{avg_rating:.2f} ⭐"),
            ("Unique Customers", f"{unique_customers:,}"),
            ("Products Sold", f"{unique_products:,}")
        ]
        
        cols = [col1, col2, col3, col4, col5, col6]
        for col, (label, value) in zip(cols, metrics):
            with col:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(label, value)
                st.markdown('</div>', unsafe_allow_html=True)
    
    def plot_revenue_analysis(self):
        """Plot revenue analysis"""
        st.subheader("📈 Revenue & Sales Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily revenue trend
            daily_revenue = self.df.groupby('order_date')['total_amount'].sum().reset_index()
            fig = px.line(daily_revenue, x='order_date', y='total_amount',
                         title='Daily Revenue Trend',
                         labels={'order_date': 'Date', 'total_amount': 'Revenue (₹)'},
                         line_shape='spline')
            fig.update_traces(line_color='#FF3E6C', line_width=3)
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Monthly revenue
            monthly_revenue = self.df.groupby('month_name')['total_amount'].sum().reset_index()
            month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            monthly_revenue['month_name'] = pd.Categorical(monthly_revenue['month_name'], 
                                                           categories=month_order, ordered=True)
            monthly_revenue = monthly_revenue.sort_values('month_name')
            
            fig = px.bar(monthly_revenue, x='month_name', y='total_amount',
                        title='Monthly Revenue Performance',
                        labels={'month_name': 'Month', 'total_amount': 'Revenue (₹)'},
                        color='total_amount', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
    
    def plot_category_analysis(self):
        """Plot category analysis"""
        st.subheader("📊 Category & Product Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Category revenue
            category_revenue = self.df.groupby('category')['total_amount'].sum().sort_values(ascending=True)
            fig = px.bar(category_revenue.tail(10), 
                        x='total_amount', y=category_revenue.tail(10).index,
                        orientation='h', title='Top 10 Categories by Revenue',
                        color='total_amount', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sub-category analysis
            subcat_revenue = self.df.groupby('sub_category')['total_amount'].sum().nlargest(10)
            fig = px.pie(values=subcat_revenue.values, names=subcat_revenue.index,
                        title='Top 10 Sub-Categories Revenue Share',
                        hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
    
    def plot_brand_analysis(self):
        """Plot brand analysis"""
        st.subheader("🏷️ Brand Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top brands by revenue
            brand_revenue = self.df.groupby('brand')['total_amount'].sum().nlargest(10)
            fig = px.bar(brand_revenue, x=brand_revenue.values, y=brand_revenue.index,
                        orientation='h', title='Top 10 Brands by Revenue',
                        color=brand_revenue.values, color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Brand rating comparison
            brand_rating = self.df.groupby('brand').agg({
                'total_amount': 'sum',
                'rating': 'mean'
            }).nlargest(10, 'total_amount').reset_index()
            
            fig = px.scatter(brand_rating, x='brand', y='rating', 
                            size='total_amount', title='Brand Performance Matrix',
                            labels={'brand': 'Brand', 'rating': 'Average Rating'},
                            color='rating', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
    
    def plot_rating_analysis(self):
        """Plot rating analysis"""
        st.subheader("⭐ Customer Ratings & Reviews")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Rating distribution
            rating_dist = self.df['rating'].value_counts().sort_index()
            fig = px.bar(rating_dist, x=rating_dist.index, y=rating_dist.values,
                        title='Rating Distribution',
                        labels={'x': 'Rating', 'y': 'Number of Reviews'},
                        color=rating_dist.values, color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Rating by category
            rating_by_cat = self.df.groupby('category')['rating'].mean().sort_values(ascending=True)
            fig = px.bar(rating_by_cat, x=rating_by_cat.values, y=rating_by_cat.index,
                        orientation='h', title='Average Rating by Category',
                        color=rating_by_cat.values, color_continuous_scale='YlOrRd')
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Rating category distribution
            rating_cat_dist = self.df['rating_category'].value_counts()
            fig = px.pie(rating_cat_dist, values=rating_cat_dist.values,
                        names=rating_cat_dist.index, title='Rating Category Distribution')
            st.plotly_chart(fig, use_container_width=True)
    
    def plot_delivery_analysis(self):
        """Plot delivery analysis"""
        st.subheader("🚚 Delivery & Logistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Delivery status
            delivery_status = self.df['delivery_status'].value_counts()
            fig = px.bar(delivery_status, x=delivery_status.index, 
                        y=delivery_status.values, title='Order Delivery Status',
                        color=delivery_status.values, color_continuous_scale='Teal')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Delivery performance
            delivery_perf = self.df['delivery_performance'].value_counts()
            fig = px.pie(delivery_perf, values=delivery_perf.values,
                        names=delivery_perf.index, title='Delivery Performance',
                        hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        
        # Delivery days distribution
        delivered_df = self.df[self.df['delivery_status'] == 'Delivered']
        fig = px.histogram(delivered_df, x='delivery_days', 
                          title='Delivery Days Distribution (Delivered Orders)',
                          labels={'delivery_days': 'Delivery Days'},
                          nbins=15, color_discrete_sequence=['#FF3E6C'])
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_customer_insights(self):
        """Plot customer insights"""
        st.subheader("👥 Customer Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Customer segments
            segments = self.df['customer_segment'].value_counts()
            fig = px.pie(segments, values=segments.values, names=segments.index,
                        title='Customer Segments Distribution',
                        hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # City wise sales
            city_sales = self.df.groupby('customer_city')['total_amount'].sum().nlargest(8)
            fig = px.bar(city_sales, x=city_sales.index, y=city_sales.values,
                        title='Top Cities by Revenue',
                        color=city_sales.values, color_continuous_scale='Oranges')
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Myntra Insider vs Non-Insider
            insider = self.df['is_myntra_insider'].value_counts()
            fig = px.pie(insider, values=insider.values,
                        names=['Non-Insider', 'Myntra Insider'],
                        title='Myntra Insider Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        # Customer spending distribution
        customer_spending = self.df.groupby('customer_id')['total_amount'].sum().reset_index()
        fig = px.box(customer_spending, y='total_amount', 
                    title='Customer Spending Distribution',
                    labels={'total_amount': 'Total Spending (₹)'})
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_discount_analysis(self):
        """Plot discount analysis"""
        st.subheader("💰 Discount & Pricing Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Discount bracket distribution
            discount_dist = self.df['discount_bracket'].value_counts()
            fig = px.bar(discount_dist, x=discount_dist.index, y=discount_dist.values,
                        title='Discount Distribution',
                        color=discount_dist.values, color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Average discount by category
            cat_discount = self.df.groupby('category')['discount_percentage'].mean().sort_values(ascending=True)
            fig = px.bar(cat_discount, x=cat_discount.values, y=cat_discount.index,
                        orientation='h', title='Average Discount by Category',
                        color=cat_discount.values, color_continuous_scale='Purples')
            st.plotly_chart(fig, use_container_width=True)
        
        # Price vs Discount scatter
        fig = px.scatter(self.df.sample(min(1000, len(self.df))), 
                        x='price', y='discount_percentage',
                        color='category', title='Price vs Discount Analysis',
                        labels={'price': 'Price (₹)', 'discount_percentage': 'Discount (%)'},
                        hover_data=['product_name', 'brand'])
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_seasonal_analysis(self):
        """Plot seasonal analysis"""
        st.subheader("🌤️ Seasonal Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Seasonal revenue
            seasonal_revenue = self.df.groupby('season')['total_amount'].sum()
            fig = px.bar(seasonal_revenue, x=seasonal_revenue.index, y=seasonal_revenue.values,
                        title='Revenue by Season',
                        color=seasonal_revenue.values, color_continuous_scale='RdYlBu')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Weekday vs Weekend
            weekend_analysis = self.df.groupby('is_weekend')['total_amount'].sum().reset_index()
            weekend_analysis['is_weekend'] = weekend_analysis['is_weekend'].map({True: 'Weekend', False: 'Weekday'})
            fig = px.pie(weekend_analysis, values='total_amount', names='is_weekend',
                        title='Weekday vs Weekend Sales')
            st.plotly_chart(fig, use_container_width=True)
        
        # Weekly pattern
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_sales = self.df.groupby('weekday')['total_amount'].sum().reindex(weekday_order)
        fig = px.line(x=weekday_sales.index, y=weekday_sales.values,
                     title='Sales Pattern by Day of Week',
                     labels={'x': 'Day', 'y': 'Revenue (₹)'},
                     markers=True)
        fig.update_traces(line_color='#FF3E6C', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_return_analysis(self):
        """Plot return analysis"""
        st.subheader("🔄 Returns Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Return rate by category
            return_rate = self.df.groupby('category')['is_returned'].mean() * 100
            fig = px.bar(return_rate, x=return_rate.index, y=return_rate.values,
                        title='Return Rate by Category (%)',
                        color=return_rate.values, color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Return reasons
            return_reasons = self.df[self.df['is_returned']]['return_reason'].value_counts()
            fig = px.pie(return_reasons, values=return_reasons.values, names=return_reasons.index,
                        title='Return Reasons Distribution')
            st.plotly_chart(fig, use_container_width=True)
    
    def display_data_table(self):
        """Display data table with filters"""
        st.subheader("📋 Sales Data Explorer")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            date_range = st.date_input("Date Range",
                                       [self.df['order_date'].min(), self.df['order_date'].max()])
        
        with col2:
            categories = ['All'] + list(self.df['category'].unique())
            selected_category = st.selectbox("Category", categories)
        
        with col3:
            brands = ['All'] + list(self.df['brand'].unique())
            selected_brand = st.selectbox("Brand", brands)
        
        with col4:
            min_rating = st.slider("Minimum Rating", 1.0, 5.0, 1.0, 0.5)
        
        # Apply filters
        filtered_df = self.df.copy()
        filtered_df['order_date'] = pd.to_datetime(filtered_df['order_date'])
        
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['order_date'] >= pd.to_datetime(date_range[0])) &
                (filtered_df['order_date'] <= pd.to_datetime(date_range[1]))
            ]
        
        if selected_category != 'All':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
        if selected_brand != 'All':
            filtered_df = filtered_df[filtered_df['brand'] == selected_brand]
        
        filtered_df = filtered_df[filtered_df['rating'] >= min_rating]
        
        # Display table
        display_cols = ['order_id', 'customer_name', 'customer_city', 'product_name', 
                       'brand', 'category', 'price', 'quantity', 'total_amount', 
                       'order_date', 'delivery_status', 'rating', 'payment_method']
        
        st.dataframe(filtered_df[display_cols].head(100), use_container_width=True)
        st.caption(f"Showing {len(filtered_df)} records")
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button("📥 Download Filtered Data as CSV", csv, 
                          "myntra_sales_filtered.csv", "text/csv")
    
    def run(self):
        """Main dashboard function"""
        st.markdown('<h1 class="main-header">🛍️ Myntra Sales Analytics Dashboard</h1>', 
                   unsafe_allow_html=True)
        
        # Load data
        if not self.load_data():
            st.stop()
        
        # Sidebar filters
        st.sidebar.header("🎛️ Dashboard Filters")
        
        # Date range filter
        min_date = self.df['order_date'].min()
        max_date = self.df['order_date'].max()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        # Category filter
        categories = ['All'] + list(self.df['category'].unique())
        selected_categories = st.sidebar.multiselect(
            "Select Categories", 
            categories, 
            default=['All']
        )
        
        # Brand filter
        top_brands = self.df.groupby('brand')['total_amount'].sum().nlargest(10).index.tolist()
        selected_brands = st.sidebar.multiselect(
            "Select Brands (Top 10 shown)", 
            ['All'] + top_brands,
            default=['All']
        )
        
        # Apply filters
        filtered_df = self.df.copy()
        filtered_df['order_date'] = pd.to_datetime(filtered_df['order_date'])
        
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['order_date'] >= pd.to_datetime(date_range[0])) &
                (filtered_df['order_date'] <= pd.to_datetime(date_range[1]))
            ]
        
        if 'All' not in selected_categories:
            filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
        
        if 'All' not in selected_brands:
            filtered_df = filtered_df[filtered_df['brand'].isin(selected_brands)]
        
        self.df = filtered_df
        
        # Display metrics
        self.display_metrics()
        
        # Create tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📈 Sales", "🛍️ Products", "⭐ Ratings", 
            "🚚 Delivery", "👥 Customers", "💰 Pricing", "📋 Data"
        ])
        
        with tab1:
            self.plot_revenue_analysis()
            self.plot_category_analysis()
            self.plot_seasonal_analysis()
        
        with tab2:
            self.plot_brand_analysis()
            self.plot_return_analysis()
        
        with tab3:
            self.plot_rating_analysis()
        
        with tab4:
            self.plot_delivery_analysis()
        
        with tab5:
            self.plot_customer_insights()
        
        with tab6:
            self.plot_discount_analysis()
        
        with tab7:
            self.display_data_table()
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: gray;'>Myntra Sales Analytics Dashboard | Powered by Streamlit | Data-driven insights for fashion e-commerce</p>",
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    dashboard = MyntraDashboard()
    dashboard.run()