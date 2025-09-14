import csv
import os

def process_inflation_data():
    """
    Process the World Bank raw inflation data to create INFLATION.csv with country code and inflation values.
    Priority: Use 2024 data if available, otherwise use 2023 data. Skip if neither available.
    """
    input_file = 'data/raw inflation data from world bank.csv'
    output_file = 'final_data/INFLATION.csv'
    
    # Ensure output directory exists
    os.makedirs('final_data', exist_ok=True)
    
    processed_data = []
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        csv_reader = csv.reader(infile)
        
        # Skip the header row
        next(csv_reader)
        
        for row in csv_reader:
            # Skip empty rows or rows without proper data
            if len(row) < 6 or not row[3].strip():  # Country Code is at index 3
                continue
            
            country_code = row[3].strip()
            inflation_2023 = row[4].strip() if len(row) > 4 else ""
            inflation_2024 = row[5].strip() if len(row) > 5 else ""
            
            # Skip if country code is empty
            if not country_code:
                continue
            
            # Determine which inflation value to use
            inflation_value = None
            
            # Priority: Use 2024 if available and not ".."
            if inflation_2024 and inflation_2024 != "..":
                try:
                    inflation_value = float(inflation_2024)
                except ValueError:
                    inflation_value = None
            
            # If 2024 not available, try 2023
            if inflation_value is None and inflation_2023 and inflation_2023 != "..":
                try:
                    inflation_value = float(inflation_2023)
                except ValueError:
                    inflation_value = None
            
            # If we have a valid inflation value, add to processed data
            if inflation_value is not None:
                processed_data.append([country_code, inflation_value])
    
    # Write the processed data to output CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        csv_writer = csv.writer(outfile)
        
        # Write header
        csv_writer.writerow(['country code', 'inflation'])
        
        # Write data rows
        csv_writer.writerows(processed_data)
    
    print(f"Successfully created {output_file}")
    print(f"Processed {len(processed_data)} countries with valid inflation data")
    
    return len(processed_data)

if __name__ == "__main__":
    process_inflation_data()