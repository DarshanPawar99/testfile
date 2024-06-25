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
            # Calculate Buying Price AI
            meal_type = safe_get_value(row, 'meal type (only lunch)')
            buying_mg_pax = safe_get_value(row, 'buying mg/pax')

            if meal_type == "veg":
                if buying_mg_pax <= 500:
                    buying_price_ai = 42.5
                elif buying_mg_pax <= 900:
                    buying_price_ai = 42.5
                else:
                    buying_price_ai = 42.5
            elif meal_type == "non-veg":
                if buying_mg_pax <= 500:
                    buying_price_ai = 52.5
                elif buying_mg_pax <= 900:
                    buying_price_ai = 52.5
                else:
                    buying_price_ai = 52.5
            else:
                buying_price_ai = ""

            check_mismatch(row, index, 'buying price ai', buying_price_ai, mismatched_data)

            # for delta pax
            calculated_delta_pax = max(
                safe_get_value(row, 'buying mg/pax') - (
                    safe_get_value(row, 'actual consumption/employee') +
                    safe_get_value(row, 'partners(direct cash sales)') +
                    safe_get_value(row, 'manual entry') +
                    safe_get_value(row, 'training new joining staff')), 
                safe_get_value(row, 'training new joining staff'), 
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
            buying_amount = safe_get_value(row, 'total pax buying') * safe_get_value(row, 'buying price ai') * 2
            check_mismatch(row, index, 'buying amount', buying_amount, mismatched_data)

            # for selling price
            meal_type = safe_get_value(row, 'meal type (only lunch)')
            selling_mg_pax = safe_get_value(row, 'selling mg/pax')

            if meal_type == "Veg":
                if selling_mg_pax <= 500:
                    selling_price = 55
                elif selling_mg_pax <= 900:
                    selling_price = 55
                else:
                    selling_price = 55
            elif meal_type == "Non-veg":
                if selling_mg_pax <= 500:
                    selling_price = 60
                elif selling_mg_pax <= 900:
                    selling_price = 60
                else:
                    selling_price = 60
            else:
                selling_price = ""

            check_mismatch(row, index, 'selling price', selling_price, mismatched_data)

            # for delta pax(gap between mg and consumption) BTC
            delta_pax_gap_btc = max(
                safe_get_value(row, 'selling mg/pax') - (
                    safe_get_value(row, 'actual consumption/employee') +
                    safe_get_value(row, 'manual entry')
                ),
                safe_get_value(row, 'food coupon btc'),
                0
            )

            check_mismatch(row, index, 'delta pax(gap between mg and consumption) btc', delta_pax_gap_btc, mismatched_data)

            # for total pax selling
            actual_consumption_employee = safe_get_value(row, 'actual consumption/employee')
            partners_direct_cash_sales = safe_get_value(row, 'partners(direct cash sales)')
            manual_entry = safe_get_value(row, 'manual entry')
            food_coupon_btc = safe_get_value(row, 'food coupon btc')
            selling_mg_pax = safe_get_value(row, 'selling mg/pax')

            if (actual_consumption_employee + partners_direct_cash_sales + manual_entry + food_coupon_btc) < selling_mg_pax:
                total_pax_selling = selling_mg_pax
            else:
                total_pax_selling = (actual_consumption_employee + partners_direct_cash_sales + manual_entry + food_coupon_btc)

            check_mismatch(row, index, 'total pax selling', total_pax_selling, mismatched_data)

            # for partners(direct cash sales) + employee 50%
            partners_direct_cash_sales = safe_get_value(row, 'partners(direct cash sales)')
            selling_price = safe_get_value(row, 'selling price')
            actual_consumption_employee = safe_get_value(row, 'actual consumption/employee')
            manual_entry = safe_get_value(row, 'manual entry')

            partners_employee_50_percent = (
                (partners_direct_cash_sales * selling_price * 2) + 
                ((actual_consumption_employee + manual_entry) * selling_price)
            )

            check_mismatch(row, index, 'partners(direct cash sales) +employee 50%', partners_employee_50_percent, mismatched_data)

            # for total sales
            actual_consumption_employee = safe_get_value(row, 'actual consumption/employee')
            manual_entry = safe_get_value(row, 'manual entry')
            selling_price = safe_get_value(row, 'selling price')
            total_pax_selling = safe_get_value(row, 'total pax selling')
            partners_employee_50_percent = safe_get_value(row, 'partners(direct cash sales) +employee 50%')

            total_sales = (
                (actual_consumption_employee + manual_entry) * selling_price +
                (total_pax_selling * selling_price * 2) +
                partners_employee_50_percent
            )

            check_mismatch(row, index, 'total sales', total_sales, mismatched_data)

            # for btc
            total_sales = safe_get_value(row, 'total sales')
            partners_employee_50_percent = safe_get_value(row, 'partners(direct cash sales) +employee 50%')

            btc = total_sales - partners_employee_50_percent

            check_mismatch(row, index, 'btc', btc, mismatched_data)


            # for comission
            total_sales = safe_get_value(row, 'total sales')
            buying_amount = safe_get_value(row, 'buying amount')

            comission = total_sales - buying_amount

            check_mismatch(row, index, 'comission', comission, mismatched_data)










            
        except Exception as e:
            logging.error(f"Error processing row {index + 3}: {e}")

    return mismatched_data


def calculate_aggregated_values(df):
    sum_buying_pax_regular = df['total pax buying'].sum()
    sum_selling_pax_regular = df['total pax selling'].sum()
    
    sum_buying_amt_ai_regular= df['buying amount'].sum()
    sum_selling_amt_regular = df['btc'].sum()
    sum_cash_recived = df['partners(direct cash sales) +employee 50%'].sum()
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
    

def business_logic_46(df):
    mismatched_data = find_mismatches(df)
    aggregated_data = calculate_aggregated_values(df)
    display_dataframes(mismatched_data, aggregated_data)
