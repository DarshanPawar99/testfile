import pandas as pd
import streamlit as st
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def safe_get_value(row, col):
    return row[col] if col in row and pd.notna(row[col]) else 0

def check_mismatch(row, index, column_name, expected_value, mismatched_data):
    actual_value = safe_get_value(row, column_name)
    if actual_value != expected_value:
        mismatched_data.append({
            'Row': index + 3,
            'Date': row['date'],
            'Column': column_name,
            'Expected': expected_value,
            'Actual': actual_value
        })


def find_mismatches(df):
    mismatched_data = []
    for index, row in df.iterrows():
        try:
            # for buying price ai
            meal_type = safe_get_value(row, 'meal type (only lunch)')
            buying_mg_pax = safe_get_value(row, 'buying mg/pax')

            if meal_type == "breakfast":
                if buying_mg_pax <= 500:
                    buying_price_ai = 62
                elif buying_mg_pax <= 900:
                    buying_price_ai = 60
                else:
                    buying_price_ai = 58
            elif meal_type == "lunch":
                if buying_mg_pax <= 500:
                    buying_price_ai = 43.05
                elif buying_mg_pax <= 900:
                    buying_price_ai = 42
                else:
                    buying_price_ai = 41
            elif meal_type == "dinner":
                if buying_mg_pax <= 500:
                    buying_price_ai = 43.05
                elif buying_mg_pax <= 900:  # I noticed this was incorrect in the provided formula
                    buying_price_ai = 42
                else:
                    buying_price_ai = 41
            else:
                buying_price_ai = ""

            check_mismatch(row, index, 'buying price ai', buying_price_ai, mismatched_data)

          # for delta pax(gap between mg and consumption)
            buying_mg_pax = safe_get_value(row, 'buying mg/pax')
            actual_consumption = safe_get_value(row, 'actual consumption/employee')
            partners_sales = safe_get_value(row, 'partners(direct cash sales)')
            manual_entry = safe_get_value(row, 'manual entry')
            training_staff = safe_get_value(row, 'training new joining staff')
            gym_traine = safe_get_value(row, 'gym trainer') 

            calculated_delta_pax = max(
                buying_mg_pax - (actual_consumption + partners_sales + manual_entry + training_staff + gym_traine),
                training_staff,
                0
            )

            check_mismatch(row, index, 'delta pax(gap between mg and consumption)', calculated_delta_pax, mismatched_data)

            # for total pax buying
            total_pax_buying = (
                safe_get_value(row, 'actual consumption/employee') +
                safe_get_value(row, 'partners(direct cash sales)') +
                safe_get_value(row, 'manual entry') +
                safe_get_value(row, 'delta pax(gap between mg and consumption)')
            )

            check_mismatch(row, index, 'total pax buying', total_pax_buying, mismatched_data)

            # for buying amount
            buying_amount = safe_get_value(row, 'total pax buying') * safe_get_value(row, 'buying price ai')  
            check_mismatch(row, index, 'buying amount', buying_amount, mismatched_data)

            # for selling price
            meal_type = safe_get_value(row, 'meal type (only lunch)')
            selling_mg_pax = safe_get_value(row, 'selling mg/pax')

            if meal_type == "breakfast":
                if selling_mg_pax <= 500:
                    selling_price = 65
                elif selling_mg_pax <= 900:
                    selling_price = 65
                else:
                    selling_price = 65
            elif meal_type == "lunch":
                if selling_mg_pax <= 500:
                    selling_price = 51.5
                elif selling_mg_pax <= 900:
                    selling_price = 50.5
                else:
                    selling_price = 49.5
            elif meal_type == "dinner":
                if selling_mg_pax <= 500:
                    selling_price = 51.5
                elif selling_mg_pax <= 900:
                    selling_price = 50.5
                else:
                    selling_price = 49.5
            else:
                selling_price = ""

            check_mismatch(row, index, 'selling price', selling_price, mismatched_data)

            # for delta pax(gap between mg and consumption) BTC
            selling_mg_pax = safe_get_value(row, 'selling mg/pax')  # Assuming S234 corresponds to 'selling mg/pax'
            actual_consumption = safe_get_value(row, 'actual consumption/employee')  # Assuming J234 corresponds to 'actual consumption/employee'
            manual_entry = safe_get_value(row, 'manual entry')  # Assuming M234 corresponds to 'manual entry'
            training_staff = safe_get_value(row, 'gym trainer  btc')  # Assuming T234 corresponds to 'training new joining staff'

            calculated_delta_pax_btc = max(
                selling_mg_pax - (actual_consumption + manual_entry),
                training_staff,
                0
            )

            check_mismatch(row, index, 'delta pax(gap between mg and consumption) btc', calculated_delta_pax_btc, mismatched_data)

            # for total sales
            actual_consumption = safe_get_value(row, 'actual consumption/employee')  
            manual_entry = safe_get_value(row, 'manual entry')
            selling_price = safe_get_value(row, 'selling price')  
            partners_sales = safe_get_value(row, 'delta pax(gap between mg and consumption) btc')  
            partners_sales_amount = safe_get_value(row, 'partners(direct cash sales) amount')  

            total_sales = ((actual_consumption + manual_entry) * selling_price) + (partners_sales * selling_price) + partners_sales_amount

            check_mismatch(row, index, 'total sales', total_sales, mismatched_data)


            # for total pax selling
            actual_consumption = safe_get_value(row, 'actual consumption/employee') 
            partners_sales = safe_get_value(row, 'partners(direct cash sales)')  
            manual_entry = safe_get_value(row, 'manual entry') 
            training_staff = safe_get_value(row, 'gym trainer  btc')  
            selling_mg_pax = safe_get_value(row, 'selling mg/pax')  

            total_pax_selling = (
                selling_mg_pax if (actual_consumption + partners_sales + manual_entry + training_staff) < selling_mg_pax 
                else (actual_consumption + partners_sales + manual_entry + training_staff)
            )

            check_mismatch(row, index, 'total pax selling', total_pax_selling, mismatched_data)








            # for BTC
            actual_consumption = safe_get_value(row, 'actual consumption/employee')  
            manual_entry = safe_get_value(row, 'manual entry')  
            selling_price = safe_get_value(row, 'selling price')  
            partners_sales = safe_get_value(row, 'delta pax(gap between mg and consumption) btc') 

            btc = ((actual_consumption + manual_entry) * selling_price) + (partners_sales * selling_price)

            check_mismatch(row, index, 'btc', btc, mismatched_data)

            # for comission
            comission_amount = safe_get_value(row, 'total sales') - safe_get_value(row, 'buying amount')
            check_mismatch(row, index, 'comission', comission_amount, mismatched_data)

            
        except Exception as e:
            logging.error(f"Error processing row {index + 3}: {e}")

    return mismatched_data


def calculate_aggregated_values(df):
    sum_buying_pax_regular = df['total pax buying'].sum()
    sum_selling_pax_regular = df['total pax selling'].sum()
    
    sum_buying_amt_ai_regular= df['buying amount'].sum()
    sum_selling_amt_regular = df['btc'].sum()
    sum_cash_recived = df['partners(direct cash sales) amount'].sum()
    sum_commission = df['comission'].sum()
    

    valid_dates_df = df[(df['total pax buying'] > 0) | (df['total pax selling'] > 0)]
    number_of_days = valid_dates_df['date'].nunique()

    aggregated_data = {
        'Number of Days': number_of_days,
        'Buying Pax (Regular)': sum_buying_pax_regular,
        'Selling Pax (Regular)': sum_selling_pax_regular,
        'Buying Amt AI (Regular)': sum_buying_amt_ai_regular,
        'Selling Amt (Regular)': sum_selling_amt_regular,
        'Cash Recived from Employee': sum_cash_recived,
        'Commission': sum_commission,
    }

    return aggregated_data

def format_dataframe(df):
    # Format numerical columns to one decimal place
    for column in df.select_dtypes(include=['float', 'int']).columns:
        df[column] = df[column].map(lambda x: f"{x:.1f}")
    return df

def display_dataframes( mismatched_data, aggregated_data):
    st.subheader("")
    
    if mismatched_data:
        mismatched_df = pd.DataFrame(mismatched_data)
        st.write("<span style='color:red'>Mismatched Data:heavy_exclamation_mark:</span>", unsafe_allow_html=True)
        st.table(format_dataframe(mismatched_df))
        st.markdown("---")
    else:
        st.write("<span style='color:green'>No mismatch found.</span> :white_check_mark:", unsafe_allow_html=True)
        st.markdown("---")

   
    aggregated_df = pd.DataFrame(list(aggregated_data.items()), columns=['Parameter', 'Value'])
    st.subheader("Aggregated Values")
    st.table(format_dataframe(aggregated_df))
    

def business_logic_47(df):
    mismatched_data = find_mismatches(df)
    aggregated_data = calculate_aggregated_values(df)
    display_dataframes(mismatched_data, aggregated_data)
