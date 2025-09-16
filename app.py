import streamlit as st 
import pandas as pd

from dashboard import fetch_products, load_products_from_db, generate_invoice, export_to_csv

def main():
    st.set_page_config(page_title="eCommerce Dashboard", page_icon="📊")
    st.title("📊 Your eCommerce Dashboard")
    
    if st.button("Fetch Fresh Products"):
        with st.spinner('Fetching products from API..'):
            products=fetch_products()
            st.success(f"Fetched {len(products)} products!")
    
    try:
        products=load_products_from_db()
        if not products:
            st.warning("Database is empty. Fetch products first!")
            return
    except:
        st.error("Could not load from database")
        return
    
    st.header("Product Catalog")
    df= pd.DataFrame(products) #convert products list to a pandas dataframe
    st.dataframe(df)
    
    st.header("Export Tools")
    
    csv_data= export_to_csv(products) #how can we create csv data from out prods
    st.download_button("Download csv",csv_data,"products.csv","text/csv")
    
    st.subheader("Generate invoice")
    selected_product=st.selectbox("Select a product:",products, format_func=lambda x: x['title'])
    
    if st.button("Generate Invoice"):
        with st.spinner("Generating invoice.."):
            generate_invoice(selected_product,"invoice.pdf")
        with open("invoice.pdf","rb") as file:
            st.download_button("Download Invoice",file,"invoice.pdf","application/pdf")
            
if __name__ == "__main__":
    main()

    