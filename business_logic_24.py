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

def pivot_and_average_prices(df):
    pivot_df = df.pivot_table(index=['site name', 'vendor', 'whole fruits'], aggfunc='size').reset_index(name='days')
    avg_prices = df.groupby(['site name', 'vendor', 'whole fruits']).agg(
        average_price=('unit price', 'mean')
    ).reset_index()
    combined_df = pivot_df.merge(avg_prices, on=['site name', 'vendor', 'whole fruits'])
    return combined_df

def find_mismatches(df):
    mismatched_data = []
    for index, row in df.iterrows():
        try:
            
            calculated_buying_amt = safe_get_value(row, 'unit price') * safe_get_value(row, 'fruit qty') 
            check_mismatch(row, index, 'buying amt ai', calculated_buying_amt, mismatched_data)

            calculated_buying_pax = safe_get_value(row, 'ordered pax/vendor mg')
            check_mismatch(row, index, 'buying pax', calculated_buying_pax, mismatched_data)

            calculated_selling_pax = max(safe_get_value(row, 'client mg/pre order'), safe_get_value(row, 'actual consumption'))
            check_mismatch(row, index, 'selling pax', calculated_selling_pax, mismatched_data)
            
            calculated_selling_amount = safe_get_value(row, 'buying amt ai') * 1.1
            check_mismatch(row, index, 'selling amount', calculated_selling_amount, mismatched_data)
            
            calculated_commission = safe_get_value(row, 'selling amount') - safe_get_value(row, 'buying amt ai')
            check_mismatch(row, index, 'commission', calculated_commission, mismatched_data)
        except Exception as e:
            logging.error(f"Error processing row {index + 3}: {e}")

    return mismatched_data

def find_karbon_expenses(df):
    karbon_expenses_data = []
    columns_to_check = ['date(karbon)','expense item', 'reason for expense', 'expense type', 'price', 'pax', 'amount', 'mode of payment','bill to','requested by','approved by']
    for index, row in df.iterrows():
        if any(pd.notna(row[col]) and row[col] != 0 for col in columns_to_check):
            karbon_expenses_data.append({
                'Row': index + 3,
                'Buying Amount': row['buying amt ai'],
                'Date': row['date(karbon)'],
                'Expense Item': row['expense item'],
                'Reason for Expense': row['reason for expense'],
                'Expense Type': row['expense type'],
                'Price': row['price'],
                'Pax': row['pax'],
                'Amount': row['amount'],
                'Mode Of Payment': row['mode of payment'],
                'Bill to': row['bill to'],
                'Requested By': row['requested by'],
                'Approved By': row['approved by']
            })

    return karbon_expenses_data

def calculate_aggregated_values(df):
    
    sum_buying_pax_regular = df['fruit qty'].sum()
    sum_selling_pax_regular = df['fruit qty'].sum()

    sum_buying_amt_ai_regular= df['buying amt ai'].sum()
    sum_selling_amt_regular = df['selling amount'].sum()


    sum_commission = df['commission'].sum()
    sum_amount = df['amount'].sum()

    valid_dates_df = df[(df['fruit qty'] > 0)]
    number_of_days = valid_dates_df['date'].nunique()

    aggregated_data = {
        'Number of Days': number_of_days,
        'Buying Pax (Regular)': sum_buying_pax_regular,
        'Selling Pax (Regular)': sum_selling_pax_regular,
        'Buying Amt AI (Regular)': sum_buying_amt_ai_regular,
        'Selling Amt (Regular)': sum_selling_amt_regular,
        'Commission': sum_commission,
        'Amount': sum_amount
    }

    return aggregated_data

def format_dataframe(df):
    # Format numerical columns to one decimal place
    for column in df.select_dtypes(include=['float', 'int']).columns:
        df[column] = df[column].map(lambda x: f"{x:.1f}")
    return df

def display_dataframes(combined_df, mismatched_data, karbon_expenses_data, aggregated_data):
    st.subheader("")
    st.subheader("Average Buying Price and Selling Price")
    st.table(format_dataframe(combined_df))
    st.markdown("---")

    if mismatched_data:
        mismatched_df = pd.DataFrame(mismatched_data)
        st.write("<span style='color:red'>Mismatched Data:heavy_exclamation_mark:</span>", unsafe_allow_html=True)
        st.table(format_dataframe(mismatched_df))
        st.markdown("---")
    else:
        st.write("<span style='color:green'>No mismatch found.</span> :white_check_mark:", unsafe_allow_html=True)
        st.markdown("---")

    if karbon_expenses_data:
        karbon_expenses_df = pd.DataFrame(karbon_expenses_data)
        st.subheader("Karbon Expenses")
        st.table(format_dataframe(karbon_expenses_df))
        st.markdown("---")
    else:
        st.write("No Karbon expenses found.")
        st.markdown("---")

    aggregated_df = pd.DataFrame(list(aggregated_data.items()), columns=['Parameter', 'Value'])
    st.subheader("Aggregated Values")
    st.table(format_dataframe(aggregated_df))
    

def business_logic_24(df):
    combined_df = pivot_and_average_prices(df)
    mismatched_data = find_mismatches(df)
    aggregated_data = calculate_aggregated_values(df)
    karbon_expenses_data = find_karbon_expenses(df)
    display_dataframes(combined_df, mismatched_data, karbon_expenses_data, aggregated_data)
