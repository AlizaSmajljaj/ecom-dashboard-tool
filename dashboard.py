import sqlite3
import json
import argparse
import requests
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

import io
    
def main():
    init_database()
    
    parser= argparse.ArgumentParser(description='eCommerce Dashboars Tool: Gnerate reports and invoices from product data.')
    parser.add_argument('--fetch', action='store_true', help='Fetch latest products from the API and update the database')
    parser.add_argument('--csv', type=str, help='Generate a csv report with the given filename (e.g., "report.csv")')
    parser.add_argument('--product-id',type=int, default=1, help='The product ID to generate an invoice for (use with --invoice). Default: 1')
    parser.add_argument('--invoice',action='store_true',help='Generate an invoice pdf')
    parser.add_argument('--all',action='store_true',help='Generate both the CSV report and an invoice (Default behaviour)')
    args=parser.parse_args()
    
    products = []
    
    if args.fetch:
        print("Fetching fresh data from api")
        products=fetch_products()
        save_products_to_db(products)
    else:
        try:
            products=load_products_from_db()
            if not products:
                print("Database is empty use --fetch to get data first")
                return
        except sqlite3.Error as e:
            print("Database error: {e}, use --fetch tog et data from api")
            return
    
    if args.csv:
        export_to_csv(products, filename=args.csv)
    
    if args.invoice:
        target_product=None
        for product in products:
            if product['id'] == args.product_id:
                target_product = product
                break
        
        if target_product:
            generate_invoice(target_product, filename=f"invoice_{args.product_id}.pdf")
        else:
            print(f"Error: Product with id {args.product_id} not found!")
    
    if args.all or (not args.csv and not args.invoice):
        export_to_csv(products)
        generate_invoice(products[0])
        
def init_database():
    conn=sqlite3.connect('products.db')
    c=conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products 
              (id INTEGER PRIMARY KEY, data TEXT)''')
    conn.commit()
    conn.close()   


def save_products_to_db(products):
    conn=sqlite3.connect('products.db')
    c=conn.cursor()
    for product in products:
        product_json=json.dumps(product)
        c.execute("REPLACE INTO products (id, data) VALUES (?, ?)",
                  (product['id'],product_json))
    conn.commit()
    conn.close()
    print(f"Saved/upadted {len(products)} products in the database.")
    return products

def load_products_from_db():
    conn=sqlite3.connect('products.db')
    c=conn.cursor()
    c.execute("SELECT * FROM products")
    rows = c.fetchall()
    products =[]
    for row in rows:
        json_string=row[1]
        product_dict=json.loads(json_string)
        products.append(product_dict)
    conn.close()
    return products
    
def fetch_products():
    print("Fetching products from API..")
    url="https://dummyjson.com/products"
    response=requests.get(url)
    response.raise_for_status()
    data= response.json()
    print(F"successfully fetched {len(data['products'])} products!")
    return data['products']


def export_to_csv(products, filename=None):
    """Exports product data to a CSV file or returns CSV as string."""
    fieldnames = ['ID', 'Title', 'Brand', 'Category', 'Price', 'Stock', 'Rating']
    
    # Create a StringIO object (like a file in memory)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for product in products:
        row = {
            'ID': product.get('id', 'N/A'),
            'Title': product.get('title', 'N/A'),
            'Brand': product.get('brand', 'N/A'),
            'Category': product.get('category', 'N/A'),
            'Price': product.get('price', 'N/A'),
            'Stock': product.get('stock', 'N/A'),
            'Rating': product.get('rating', 'N/A')
        }
        writer.writerow(row)
    
    csv_data = output.getvalue()
    output.close()
    
    if filename:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.write(csv_data)
        print(f" CSV report {filename} generated successfully!")
    
    return csv_data 

def generate_invoice(product, filename='invoice.pdf'):
    print(f"Generating invoice: {filename}")
    c= canvas.Canvas(filename,pagesize=letter)
    width,height=letter
    
    c.setFont('Helvetica-Bold',20)
    c.drawString(100, height-50, "INVOICE")
    
    c.setFont("Helvetica",12)
    c.drawString(100, height-80, "Company name")
    c.drawString(100,height-95,"123 Business St., City, Country")
    
    c.drawString(350, height-80, f"Date: {datetime.today().strftime('%Y-%m-%d')}")
    c.drawString(350, height-95, f"Invoice #: {datetime.now().timestamp():.0f}")
    
    c.line(100,height-110,500,height-110)
    
    c.setFont("Helvetica-Bold",12)
    c.drawString(100,height-130,"Item Desciption")
    c.drawString(350, height-130, 'Price ($)')
    c.line(100, height-135, 500, height-135)
    
    c.setFont("Helvetica",12)
    product_title = product.get('title', 'Unknown Product')
    product_price = product.get('price', 0)
    
    c.drawString(100, height - 155, product_title)
    c.drawString(350, height - 155, f"{product_price:.2f}")

    c.line(100, height - 170, 500, height - 170)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 190, "Total:")
    c.drawString(350, height - 190, f"${product_price:.2f}")
    
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, height - 250, "This is a sample invoice for portfolio purposes.")
    c.drawString(100, height - 265, "No VAT shown (0%) - Not a real transaction.")

    c.save()
    print("Invoice generated successfully!")

if __name__ == '__main__':
    #products=fetch_products()
    #export_to_csv(products)    
    #generate_invoice(products[0])
    main()