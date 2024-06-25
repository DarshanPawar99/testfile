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
            calculated_total_ai = safe_get_value(row, 'wallet')
            check_mismatch(row, index, 'total sale ai', calculated_total_ai, mismatched_data)

            calculated_pg_charges = safe_get_value(row, 'total sale ai') * 0.02
            check_mismatch(row, index, 'pg charges on mrp', calculated_pg_charges, mismatched_data)

            calculated_pggst = safe_get_value(row, 'pg charges on mrp') * 1.18
            check_mismatch(row, index, 'pg+gst', calculated_pggst, mismatched_data)


            calculated_buying_amt = safe_get_value(row, 'total sale ai') - safe_get_value(row, 'pg+gst') - safe_get_value(row, 'direct payment from employee')
                                     
            check_mismatch(row, index, 'buying amt ai', calculated_buying_amt, mismatched_data)
            
            calculated_selling_amount = (safe_get_value(row, 'total sale ai') / safe_get_value(row, 'gst'))
            check_mismatch(row, index, 'selling amount', calculated_selling_amount, mismatched_data)
            
        except Exception as e:
            logging.error(f"Error processing row {index + 3}: {e}")

    return mismatched_data


def calculate_aggregated_values(df):
    sum_buying_pax_regular = df['quantity'].sum()
    sum_selling_pax_regular = df['quantity'].sum()

    sum_buying_amt_ai_regular = df['buying amt ai'].sum()
    sum_selling_amt_regular = df['selling amount'].sum()

    sum_cash_recived = df['direct payment from employee'].sum()
    

    valid_dates_df = df[(df['quantity'] > 0)]
    number_of_days = valid_dates_df['date'].nunique()

    aggregated_data = {
        'Number of Days': number_of_days,
        'Buying Pax (Regular)': sum_buying_pax_regular,
        'Selling Pax (Regular)': sum_selling_pax_regular,
        'Buying Amt AI (Regular)': sum_buying_amt_ai_regular,
        'Selling Amt (Regular)': sum_selling_amt_regular,
        'Cash Recived From Employee': sum_cash_recived,
    
    }

    return aggregated_data

def format_dataframe(df):
    # Format numerical columns to one decimal place
    for column in df.select_dtypes(include=['float', 'int']).columns:
        df[column] = df[column].map(lambda x: f"{x:.1f}")
    return df

def display_dataframes(mismatched_data, aggregated_data):
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
    

def business_logic_17(df):
    mismatched_data = find_mismatches(df)
    aggregated_data = calculate_aggregated_values(df)
    display_dataframes(mismatched_data, aggregated_data)
