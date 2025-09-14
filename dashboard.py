import requests
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def fetch_products():
    print("Fetching products from API..")
    url="https://dummyjson.com/products"
    response=requests.get(url)
    response.raise_for_status()
    data= response.json()
    print(F"successfully fetched {len(data['products'])} products!")
    return data['products']

def export_to_csv(products, filename='product_catalog.csv'):
    print(f" Generating CSV report: {filename}")
    fieldnames = ['ID', 'Title', 'Brand', 'Category', 'Price', 'Stock', 'Rating']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in products:
            row= {
                'ID': product.get('id','N/A'),
                'Title': product.get('title','N/A'),
                'Brand': product.get('brand','N/A'),
                'Category': product.get('category','N/A'),
                'Price': product.get('price','N/A'),
                'Stock': product.get('stock','N/A'),
                'Rating': product.get('rating','N/A')
            }
            writer.writerow(row)
    print(" CSV report generated successfully!")

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
    products=fetch_products()
    export_to_csv(products)    
    generate_invoice(products[0])