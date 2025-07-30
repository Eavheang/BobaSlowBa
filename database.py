from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

# Get database connection string
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in .env file")

def ensure_tables_exist(conn):
    """Ensure required tables exist"""
    try:
        with conn.cursor() as cur:
            # Create sales table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    items JSONB NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    payment_method TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"Error ensuring tables exist: {str(e)}")
        conn.rollback()

def get_db_connection():
    """Get a database connection"""
    try:
        print(f"Attempting to connect to database...")
        conn = psycopg2.connect(DATABASE_URL)
        print("Database connection successful")
        ensure_tables_exist(conn)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        print(f"Database URL format: {DATABASE_URL[:10]}...") # Only show start of URL for security
        return None

async def save_order(user_id: int, username: str, items: List[Dict], total_amount: float, payment_method: str):
    """Save order to database"""
    try:
        conn = get_db_connection()
        if not conn:
            return None
            
        with conn.cursor() as cur:
            # Create sales table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    items JSONB NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    payment_method TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert the order
            cur.execute("""
                INSERT INTO sales (user_id, username, items, total_amount, payment_method)
                VALUES (%s, %s, %s::jsonb, %s, %s)
                RETURNING *
            """, (
                str(user_id),
                username,
                psycopg2.extras.Json(items),
                float(total_amount),
                payment_method
            ))
            
            result = cur.fetchone()
            conn.commit()
            return result
            
    except Exception as e:
        print(f"Error saving order: {str(e)}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

async def get_sales_summary(period: str = 'day') -> Dict[str, Any]:
    """Get sales summary for the specified period"""
    conn = None
    try:
        now = datetime.utcnow()
        
        if period == 'day':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # overall
            start_date = datetime(2024, 1, 1)
            
        print(f"Getting sales summary for period: {period}")
        print(f"Start date: {start_date.isoformat()}")
            
        conn = get_db_connection()
        if not conn:
            print("Failed to get database connection")
            return {
                'period': period,
                'total_sales': 0.0,
                'total_orders': 0,
                'items_sold': {},
                'start_date': start_date.isoformat(),
                'end_date': now.isoformat(),
                'error': 'Could not connect to database'
            }
            
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First check if the table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_name = 'sales'
                );
            """)
            table_exists = cur.fetchone()['exists']
            
            if not table_exists:
                print("Sales table does not exist")
                return {
                    'period': period,
                    'total_sales': 0.0,
                    'total_orders': 0,
                    'items_sold': {},
                    'start_date': start_date.isoformat(),
                    'end_date': now.isoformat(),
                    'error': 'Sales table does not exist'
                }
            
            # Get all orders for the period
            query = """
                SELECT * FROM sales 
                WHERE created_at >= %s
                ORDER BY created_at DESC
            """
            print(f"Executing query: {query} with start_date: {start_date}")
            cur.execute(query, (start_date,))
            
            orders = cur.fetchall()
            print(f"Found {len(orders)} orders")
            
            if not orders:
                return {
                    'period': period,
                    'total_sales': 0.0,
                    'total_orders': 0,
                    'items_sold': {},
                    'start_date': start_date.isoformat(),
                    'end_date': now.isoformat()
                }
            
            # Calculate summary
            total_sales = sum(float(order['total_amount']) for order in orders)
            total_orders = len(orders)
            print(f"Total sales: ${total_sales:.2f}, Total orders: {total_orders}")
            
            # Calculate items sold
            items_sold = {}
            for order in orders:
                for item in order['items']:
                    item_name = item.get('item')
                    if item_name:
                        items_sold[item_name] = items_sold.get(item_name, 0) + 1
            
            # Sort items by quantity sold
            items_sold = dict(sorted(items_sold.items(), key=lambda x: x[1], reverse=True))
            print(f"Items sold: {items_sold}")
            
            return {
                'period': period,
                'total_sales': total_sales,
                'total_orders': total_orders,
                'items_sold': items_sold,
                'start_date': start_date.isoformat(),
                'end_date': now.isoformat()
            }
            
    except Exception as e:
        print(f"Error getting sales summary: {str(e)}")
        return {
            'period': period,
            'total_sales': 0.0,
            'total_orders': 0,
            'items_sold': {},
            'start_date': now.isoformat(),
            'end_date': now.isoformat(),
            'error': str(e)
        }
    finally:
        if conn:
            conn.close()