import streamlit as st
import pandas as pd
import requests

URL = "https://bill-maker-rd.herokuapp.com/bill"

def main():
    st.title("RD Industries :tada:")
    menu = ["Billmaker", "Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "Billmaker":
        num_items = st.sidebar.number_input("Number of items", min_value=1, max_value=10)
        def bill_maker():
            st.subheader("Bill Maker")
            items = ""
            prices = ""
            quantities = ""
            with st.form(key="form1"):
                name = st.text_input("Name", "", key="name")
                address = st.text_area("Address", "", key="address")
                textsplit = [name]
                if address is not None:
                    textsplit.extend(address.splitlines())
                address = "\n".join(textsplit)

                st.write("Enter Item Descriptions:")
                for i in range(1, num_items+1):
                    col1, col2, col3 = st.columns(3)
                    item_name = col1.text_input(f"{i}. Item Name", "", key=f"item_name_{i}")
                    item_price = col2.number_input("Item Price", 1.0, 1.0e10, step=1.0, key=f"item_price_{i}")
                    item_qty = int(col3.number_input("Item Quantity", 1, 100, 1, key=f"item_qty_{i}"))
                    
                    items+=item_name+"\n"
                    prices+=str(item_price)+" "
                    quantities+=str(item_qty)+" "

                date = st.date_input("Date", key="date")
                invoice = st.number_input("invoice", 1, 1000000, 1, key="invoice")
                
                date = date.strftime("%d.%m.%Y")
                items = items.strip()
                prices = prices.strip()
                quantities = quantities.strip()

                submit_button = st.form_submit_button("Submit")

            if submit_button:
                st.success(f"You have succesfully created a bill template for {name}")
                payload = {"name": name, "address": address, "items": items, "quantities": quantities, "rates": prices, "date": date, "invoice": str(invoice)}
                # print(payload)
                r = requests.post(URL,data=payload)
                # print(r)
                filename = str(invoice) + "dt." + str(date) + "." + name + ".pdf"
                st.download_button('Download bill', r.content, file_name=filename)
        bill_maker()
    else:
        st.subheader("Dashboard")

if __name__ == "__main__":
    main()