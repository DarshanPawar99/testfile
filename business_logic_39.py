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
            calculated_selling_management = safe_get_value(row, 'total sales') * 0.1
            check_mismatch(row, index, 'selling management fee', calculated_selling_management, mismatched_data)

            calculated_buying_amt = (safe_get_value(row, 'total sales') - (safe_get_value(row, 'discount%') 
                                     * safe_get_value(row, 'total sales')))
            check_mismatch(row, index, 'buying amt ai', calculated_buying_amt, mismatched_data)


            calculated_selling_amount = (safe_get_value(row, 'total sales') + safe_get_value(row, 'selling management fee') 
                                     - safe_get_value(row, 'direct payment from employee'))  
            check_mismatch(row, index, 'selling amount', calculated_selling_amount, mismatched_data)

            
            calculated_commission = (safe_get_value(row, 'selling amount') - safe_get_value(row, 'buying amt ai') 
                                     + safe_get_value(row, 'direct payment from employee'))
            check_mismatch(row, index, 'commission', calculated_commission, mismatched_data)
        except Exception as e:
            logging.error(f"Error processing row {index + 3}: {e}")

    return mismatched_data


def calculate_aggregated_values(df):
    regular_orders = df[df['order type'] .isin(['regular','regular-pop-up', 'food trial'])]
    sum_buying_pax_regular = regular_orders['quantity'].sum()
    sum_selling_pax_regular = regular_orders['quantity'].sum()

    
    regular_and_adhoc_orders = df[df['order type'].isin(['regular', 'smartq-pop-up', 'food trial', 'regular-pop-up','tuckshop','live'])]
    sum_buying_amt_ai_regular= regular_and_adhoc_orders['buying amt ai'].sum()
    sum_selling_amt_regular = regular_and_adhoc_orders['selling amount'].sum()

    event_and_popup_orders = df[df['order type'].isin(['event', 'event pop-up', 'adhoc'])]
    sum_buying_amt_ai_event= event_and_popup_orders['buying amt ai'].sum()
    sum_selling_amt_event = event_and_popup_orders['selling amount'].sum()

    sum_direct_cash = df['direct payment from employee'].sum()
    sum_commission = df['commission'].sum()
    

    valid_dates_df = df[(df['quantity'] > 0)]
    number_of_days = valid_dates_df['date'].nunique()

    aggregated_data = {
        'Number of Days': number_of_days,
        'Buying Pax (Regular)': sum_buying_pax_regular,
        'Selling Pax (Regular)': sum_selling_pax_regular,
        'Buying Amt AI (Regular)': sum_buying_amt_ai_regular,
        'Selling Amt (Regular)': sum_selling_amt_regular,
        'Buying Amt AI (Event)': sum_buying_amt_ai_event,
        'Selling Amt (Event)': sum_selling_amt_event,
        'Direct cash Recived': sum_direct_cash,
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
    

def business_logic_39(df):
    mismatched_data = find_mismatches(df)
    aggregated_data = calculate_aggregated_values(df)
    display_dataframes( mismatched_data, aggregated_data)
