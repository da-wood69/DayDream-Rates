import csv
import os

def process_ppp_data():
    """
    Process the World Bank raw data to create PPP.csv with country code and PPP values.
    Priority: Use 2024 data if available, otherwise use 2023 data. Skip if neither available.
    """
    input_file = 'data/raw data from worldbank.csv'
    output_file = 'final_data/PPP.csv'
    
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
            ppp_2023 = row[4].strip() if len(row) > 4 else ""
            ppp_2024 = row[5].strip() if len(row) > 5 else ""
            
            # Skip if country code is empty
            if not country_code:
                continue
            
            # Determine which PPP value to use
            ppp_value = None
            
            # Priority: Use 2024 if available and not ".."
            if ppp_2024 and ppp_2024 != "..":
                try:
                    ppp_value = float(ppp_2024)
                except ValueError:
                    ppp_value = None
            
            # If 2024 not available, try 2023
            if ppp_value is None and ppp_2023 and ppp_2023 != "..":
                try:
                    ppp_value = float(ppp_2023)
                except ValueError:
                    ppp_value = None
            
            # If we have a valid PPP value, add to processed data
            if ppp_value is not None:
                processed_data.append([country_code, ppp_value])
    
    # Write the processed data to output CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        csv_writer = csv.writer(outfile)
        
        # Write header
        csv_writer.writerow(['country code', 'PPP'])
        
        # Write data rows
        csv_writer.writerows(processed_data)
    
    print(f"Successfully created {output_file}")
    print(f"Processed {len(processed_data)} countries with valid PPP data")
    
    return len(processed_data)

if __name__ == "__main__":
    process_ppp_data()