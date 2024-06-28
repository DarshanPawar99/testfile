import pandas as pd
import logging
import streamlit as st
import importlib

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    st.set_page_config(page_title="Monthly MIS Checker", layout="wide")  # Set page title and layout
    st.title("MIS Reviewer 	:chart_with_upwards_trend:")
    
    # Allow user to upload an Excel file
    uploaded_file = st.sidebar.file_uploader('Upload Excel file', type=['xlsx', 'xls'])

    if uploaded_file:
        try:
            # The uploaded file is in memory as a file-like object
            excel_file = pd.ExcelFile(uploaded_file)
            logging.info("Excel file uploaded successfully.")
        except ValueError as e:
            st.error(f"Error reading the Excel file: {e}")
            logging.error(f"ValueError reading the Excel file: {e}")
            return
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            logging.error(f"Unexpected error reading the Excel file: {e}")
            return

        # Get the list of sheet names
        sheet_names = excel_file.sheet_names

        # Allow the user to select a sheet to display
        selected_sheet = st.sidebar.selectbox('Select a sheet to display', sheet_names)

        try:
            # Read the selected sheet into a dataframe, specifying header row
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet, header=1)
            logging.info(f"Sheet '{selected_sheet}' loaded successfully.")
        except ValueError as e:
            st.error(f"ValueError reading the sheet '{selected_sheet}': {e}")
            logging.error(f"ValueError reading the sheet '{selected_sheet}': {e}")
            return
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            logging.error(f"Unexpected error reading the sheet '{selected_sheet}': {e}")
            return

        try:
            # Convert all column names to lower case
            df.columns = df.columns.str.lower().str.strip()

            # Exclude the 'date' column from being converted to lower case
            columns_to_convert = df.columns.difference(['date'])
            df[columns_to_convert] = df[columns_to_convert].apply(
                lambda col: col.str.lower().str.strip() if col.dtype == 'object' else col
            )
            logging.info("Columns converted to lower case successfully.")
        except Exception as e:
            st.error(f"Error processing the data: {e}")
            logging.error(f"Error processing the data: {e}")
            return

        # Check if 'month' column exists
        if 'month' not in df.columns:
            st.write("No 'month' column found in this sheet.")
            logging.warning("No 'month' column found in the sheet.")
            return

        try:
            # Get user input for the month
            month = st.sidebar.selectbox("Select the month for review", df['month'].unique())

            # Filter the DataFrame for the specified month
            df_filtered = df[df['month'] == month]
            logging.info(f"Data filtered by month '{month}' successfully.")
        except KeyError as e:
            st.error(f"KeyError filtering data by month: {e}")
            logging.error(f"KeyError filtering data by month: {e}")
            return
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            logging.error(f"Unexpected error filtering data by month: {e}")
            return

        # Define sheet name lists for each business logic
        business_logic_sheets = {
            "business_logic_1": ["Postman"],
            "business_logic_2": ["Pratilipi"],
            "business_logic_3": ["Quzizz","Synergy","Amadeus","Awfis"],
            "business_logic_4": ["Medtrix","Odessa","MG Eli Lilly","Scaler-Prequin"],
            "business_logic_5": ["Gojek","Microchip Main Meal"],
            "business_logic_6": ["HD Works"],
            "business_logic_7": ["MPL"],
            "business_logic_8": ["Tonbo","Tadano Escorts","Siemens - Tuckshop","Dynasty","Citrix Driver's Lunch & Dinner","sharefile"],
            "business_logic_9": ["Rippling","Tessolve"],
            "business_logic_10": ["MPL -  Infinity Plates","Tekion.","Groww Koramangala","Groww VTP","Groww Mumbai","Ather Mumbai","Epam"],
            "business_logic_11": ["Telstra MainMeal(Cash & Carry)"],
            "business_logic_12": ["Eli Lilly Wallet", "Sheet1"], # get this clarified
            "business_logic_13": ["Sinch","O9 Solutions"],
            "business_logic_14": ["RAKUTEN-2","Clario"],
            "business_logic_15": ["Waters Main Meal"], # used BL6 and might be same for seminens
            "business_logic_16": ["Quest Company Paid"],
            "business_logic_17": ["Waters Tuck Shop"],
            "business_logic_18": ["H&M"],
            "business_logic_19": ["Lam Research","Corning","PhonePe"],
            "business_logic_20": ["Micochip Juice Junction"],
            "business_logic_21": ["Ather BLR"],
            "business_logic_22": ["Ather Plant 1.","Ather Plant 2.","SAEL Delhi","Gojek."],  #gojek is ncr
            "business_logic_23": ["STRIPE MIS","TEA-Breakfast"],
            "business_logic_24": ["FRUIT N JUICE MIS"],
            "business_logic_25": ["Siemens","Toasttab","Gartner"],
            "business_logic_26": ["DTCC Wallet"],
            "business_logic_27": ["Siemens_Pune"],
            "business_logic_28": ["CSG-Pune"],
            "business_logic_29": ["Salesforce-GGN"],
            "business_logic_30": ["Salesforce - Jaipur"],
            "business_logic_31": ["Ather - Main Meal"],
            "business_logic_32": ["Siemens."], # NCR
            "business_logic_33": ["Postman.","Citrix-Tuckshop"],
            "business_logic_34": ["Sinch Lunch"],
            "business_logic_35": ["Sinch Dinner"],
            "business_logic_36": ["STRYKER MIS - '2024"],
            "business_logic_37": ["EGL"],
            "business_logic_38": ["Truecaller"],
            "business_logic_39": ["Sharefile Wallet"],
            "business_logic_40": ["Gold Hill-Main Meal","Goldhill Juice Junction.","Healthineer International","Priteck - Main meal","Pritech park Juice junction"],
            "business_logic_41": ["Siemens-BLR","Siemens Juice Counter"],
            "business_logic_42": ["Heathineer Factory"],
            "business_logic_43": ["Airtel Center","Airtel  Plot 5","Airtel NOC Non veg","Airtel international"],
            "business_logic_44": ["Tekion"],
            "business_logic_45": ["HD Works(HYD)"],
            "business_logic_46": ["Airtel Noida"],
            "business_logic_47": ["Airtel NOC"],
            "business_logic_48": ["Airtel-Jaya"],
            "business_logic_49": ["MIQ"],
            "business_logic_50": ["MIQ MRP"],


            "event_logic_1": ["Telstra Event.","Telstra Event","Events"],
            "event_logic_2": ["Eli Lilly Event"],
            "event_logic_3": ["Waters Event"],
            "event_logic_4": ["Icon-event-Bangalore","Sinch Event sheet","infosys Event+ Additional Sales","Other Events.","Telstra Event sheet","MPL-Delhi","Grow event"],
            "event_logic_5": ["Other Events"],
            "event_logic_6": ["Lam Research Event"],
            "event_logic_7": ["ICON CHN EVENT"],
            "event_logic_8": ["other Event MIS"],
            "event_logic_9": ["Amazon  PNQ Events -"],


            "other_revenues": [""]
            # Add more mappings as needed
        }

        # Determine which business logic to apply based on the selected sheet name
        business_logic_module = None
        for module_name, sheets in business_logic_sheets.items():
            if selected_sheet in sheets:
                business_logic_module = module_name
                break

        if business_logic_module:
            try:
                # Dynamically import the business logic module
                module = importlib.import_module(business_logic_module)
                # Call the appropriate business logic function
                business_logic_function = getattr(module, business_logic_module)
                business_logic_function(df_filtered)
                logging.info(f"Business logic '{business_logic_module}' applied successfully.")
            except ModuleNotFoundError:
                st.error(f"Business logic module '{business_logic_module}' not found.")
                logging.error(f"Business logic module '{business_logic_module}' not found.")
            except AttributeError:
                st.error(f"Function '{business_logic_module}' not found in the module.")
                logging.error(f"Function '{business_logic_module}' not found in the module.")
            except Exception as e:
                st.error(f"Error applying business logic: {e}")
                logging.error(f"Error applying business logic: {e}")
        else:
            st.write("No business logic defined for this sheet.")
            logging.warning("No business logic defined for the selected sheet.")
    else:
        st.write("Please upload an Excel file to proceed.")

if __name__ == "__main__":
    main()
