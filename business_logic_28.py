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
    pivot_df = df.pivot_table(index=['site name', 'vendor', 'session', 'meal type', 'order type'], aggfunc='size').reset_index(name='days')
    avg_prices = df.groupby(['site name', 'vendor', 'session', 'meal type', 'order type']).agg(
        average_buying_price_ai=('buying price ai', 'mean'),
        average_selling_price=('selling price', 'mean')
    ).reset_index()
    combined_df = pivot_df.merge(avg_prices, on=['site name', 'vendor', 'session', 'meal type', 'order type'])
    return combined_df

def find_mismatches(df):
    mismatched_data = []
    for index, row in df.iterrows():
        try:
            calculated_buying_price = safe_get_value(row, 'buying price ai') / safe_get_value(row, 'gst')
            check_mismatch(row, index, 'buying price', calculated_buying_price, mismatched_data)

            calculated_buying_amt = (safe_get_value(row, 'buying price ai') * safe_get_value(row, 'buying pax') 
                                     + safe_get_value(row, 'buying transportation'))
            check_mismatch(row, index, 'buying amt ai', calculated_buying_amt, mismatched_data)

            calculated_buying_pax = safe_get_value(row, 'actual consumption')
            check_mismatch(row, index, 'buying pax', calculated_buying_pax, mismatched_data)

            calculated_selling_pax = safe_get_value(row, 'actual consumption')
            check_mismatch(row, index, 'selling pax', calculated_selling_pax, mismatched_data)
            
            calculated_selling_amount = safe_get_value(row, 'selling pax') * safe_get_value(row, 'selling price') + safe_get_value(row, 'selling transportation')
            check_mismatch(row, index, 'selling amount', calculated_selling_amount, mismatched_data)
            
            calculated_commission = (safe_get_value(row, 'selling amount') - safe_get_value(row, 'buying amt ai') 
                                     + safe_get_value(row, 'penalty on vendor') - safe_get_value(row, 'penalty on smartq')+ safe_get_value(row, 'selling management fee'))
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
    regular_orders = df[df['order type'] .isin(['regular','regular-pop-up', 'food trial'])]
    sum_buying_pax_regular = regular_orders['buying pax'].sum()
    sum_selling_pax_regular = regular_orders['selling pax'].sum()

    regular_and_adhoc_orders = df[df['order type'].isin(['regular', 'smartq-pop-up', 'food trial', 'regular-pop-up'])]
    sum_buying_amt_ai_regular= regular_and_adhoc_orders['buying amt ai'].sum()
    sum_selling_amt_regular = regular_and_adhoc_orders['selling amount'].sum()

    event_and_popup_orders = df[df['order type'].isin(['event', 'event pop-up', 'adhoc'])]
    sum_buying_amt_ai_event= event_and_popup_orders['buying amt ai'].sum()
    sum_selling_amt_event = event_and_popup_orders['selling amount'].sum()

    sum_penalty_on_vendor = df['penalty on vendor'].sum()
    sum_penalty_on_smartq = df['penalty on smartq'].sum()
    sum_commission = df['commission'].sum()
    sum_amount = df['amount'].sum()

    valid_dates_df = df[(df['buying pax'] > 0) | (df['selling pax'] > 0)]
    number_of_days = valid_dates_df['date'].nunique()

    aggregated_data = {
        'Number of Days': number_of_days,
        'Buying Pax (Regular)': sum_buying_pax_regular,
        'Selling Pax (Regular)': sum_selling_pax_regular,
        'Buying Amt AI (Regular)': sum_buying_amt_ai_regular,
        'Selling Amt (Regular)': sum_selling_amt_regular,
        'Buying Amt AI (Event)': sum_buying_amt_ai_event,
        'Selling Amt (Event)': sum_selling_amt_event,
        'Penalty on Vendor': sum_penalty_on_vendor,
        'Penalty on SmartQ': sum_penalty_on_smartq,
        'Commission': sum_commission,
        'Amount': sum_amount
    }

    return aggregated_data

def find_buying_value_issues(df):
    buying_value_issues = []
    for index, row in df.iterrows():
        if (safe_get_value(row, 'buying pax') > 0 or safe_get_value(row, 'buying price ai') > 0) and safe_get_value(row, 'buying amt ai') == 0:
            buying_value_issues.append({
                'Row': index + 3,
                'Date': row['date'],
                'Session': row['session'],
                'Mealtype': row['meal type'],
                'Ordertype': row['order type'],
                'Buying Pax': row['buying pax'],
                'Buying Price AI': row['buying price ai'],
                'Buying Amount AI': row['buying amt ai']
            })
    return buying_value_issues

def find_selling_value_issues(df):
    selling_value_issues = []
    for index, row in df.iterrows():
        if (safe_get_value(row, 'selling pax') > 0 or safe_get_value(row, 'selling price') > 0) and safe_get_value(row, 'selling amount') == 0:
            selling_value_issues.append({
                'Row': index + 3,
                'Date': row['date'],
                'Session': row['session'],
                'Mealtype': row['meal type'],
                'Ordertype': row['order type'],
                'Selling Pax': row['selling pax'],
                'Selling Price': row['selling price'],
                'Selling Amount': row['selling amount']
            })
    return selling_value_issues

def find_popup_selling_issues(df):
    popup_selling_issues = []
    for index, row in df.iterrows():
        if row['order type'] in ['smartq-pop-up', 'regular-pop-up', 'event pop-up'] and safe_get_value(row, 'selling amount') > 0:
            popup_selling_issues.append({
                'Row': index + 3,
                'Date': row['date'],
                'Session': row['session'],
                'Order Type': row['order type'],
                'Selling Pax': row['selling pax'],
                'Selling Price': row['selling price'],
                'Selling Amount': row['selling amount']
            })
    return popup_selling_issues

def format_dataframe(df):
    # Format numerical columns to one decimal place
    for column in df.select_dtypes(include=['float', 'int']).columns:
        df[column] = df[column].map(lambda x: f"{x:.1f}")
    return df

def display_dataframes(combined_df, mismatched_data, karbon_expenses_data, aggregated_data, buying_value_issues, selling_value_issues, popup_selling_issues):
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

    if buying_value_issues:
        buying_value_issues_df = pd.DataFrame(buying_value_issues)
        st.write("<span style='color:red'>Buying Value Issues</span> :heavy_exclamation_mark:", unsafe_allow_html=True)
        st.dataframe(format_dataframe(buying_value_issues_df))
        st.markdown("---")
    else:
        st.write("<span style='color:green'>No buying value issues found.</span> :white_check_mark:", unsafe_allow_html=True)
        st.markdown("---")

    if selling_value_issues:
        selling_value_issues_df = pd.DataFrame(selling_value_issues)
        st.write("<span style='color:red'>Selling Value Issues</span> :heavy_exclamation_mark:", unsafe_allow_html=True)
        st.dataframe(format_dataframe(selling_value_issues_df))
        st.markdown("---")
    else:
        st.write("<span style='color:green'>No selling value issues found.</span> :white_check_mark:", unsafe_allow_html=True)
        st.markdown("---")

    if popup_selling_issues:
        popup_selling_issues_df = pd.DataFrame(popup_selling_issues)
        st.write("<span style='color:red'>Popup Selling Issues.</span> :heavy_exclamation_mark:", unsafe_allow_html=True)
        st.dataframe(format_dataframe(popup_selling_issues_df))
        st.markdown("---")
    else:
        st.write("<span style='color:green'>No selling price found in Pop-up.</span> :white_check_mark:", unsafe_allow_html=True)
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
    

def business_logic_28(df):
    combined_df = pivot_and_average_prices(df)
    mismatched_data = find_mismatches(df)
    aggregated_data = calculate_aggregated_values(df)
    buying_value_issues = find_buying_value_issues(df)
    selling_value_issues = find_selling_value_issues(df)
    popup_selling_issues = find_popup_selling_issues(df)
    karbon_expenses_data = find_karbon_expenses(df)
    display_dataframes(combined_df, mismatched_data, karbon_expenses_data, aggregated_data, buying_value_issues, selling_value_issues, popup_selling_issues)
