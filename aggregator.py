import pandas as pd
import os
from COLI_aggregation import cost_of_living_index

def process_coli_data():
    """
    Process raw COLI data and generate aggregated COLI values for each country.
    Saves the result as ISO Code, COLI format in final_data/COLI.csv
    """
    
    # Input and output file paths
    input_file = os.path.join('data', 'COLI Numbeo Raw data.csv')
    output_dir = 'final_data'
    output_file = os.path.join(output_dir, 'COLI.csv')
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    try:
        # Read the raw COLI data
        df = pd.read_csv(input_file)
        print(f"Successfully read CSV file with {len(df)} rows.")
        
        # Display the columns to verify data structure
        print(f"Columns in the data: {list(df.columns)}")
        
        # Calculate reference averages for normalization
        # Using the mean of all countries for each index
        mu_GI = df['Groceries Index'].mean()
        mu_RI = df['Restaurant Price Index'].mean() 
        mu_PPI = df['Local Purchasing Power Index'].mean()
        
        print(f"Reference averages - Groceries: {mu_GI:.2f}, Restaurant: {mu_RI:.2f}, Purchasing Power: {mu_PPI:.2f}")
        
        # Prepare output data
        results = []
        
        # Process each country
        for index, row in df.iterrows():
            iso_code = row['Country']
            groceries_index = row['Groceries Index']
            restaurant_index = row['Restaurant Price Index']
            purchasing_power_index = row['Local Purchasing Power Index']
            
            # Calculate aggregated COLI using the function from COLI_aggregation.py
            aggregated_coli = cost_of_living_index(
                GI=groceries_index,
                RI=restaurant_index,
                PPI=purchasing_power_index,
                mu_GI=mu_GI,
                mu_RI=mu_RI,
                mu_PPI=mu_PPI,
                mu_COLI=1.0,  # No rescaling for baseline
                w_GI=0.4,     # 40% weight for groceries
                w_RI=0.3,     # 30% weight for restaurant prices
                w_PPI=0.3,    # 30% weight for purchasing power
                alpha=0.7     # Sensitivity factor for purchasing power adjustment
            )
            
            results.append({
                'ISO_Code': iso_code,
                'COLI': round(aggregated_coli, 2)
            })
        
        # Create DataFrame with results
        output_df = pd.DataFrame(results)
        
        # Sort by COLI in descending order (highest cost of living first)
        output_df = output_df.sort_values('COLI', ascending=False)
        
        # Save to CSV
        output_df.to_csv(output_file, index=False)
        print(f"Successfully saved aggregated COLI data to: {output_file}")
        print(f"Processed {len(output_df)} countries.")
        
        # Display first few results
        print("\nFirst 10 countries by aggregated COLI:")
        print(output_df.head(10).to_string(index=False))
        
        print("\nLast 10 countries by aggregated COLI:")
        print(output_df.tail(10).to_string(index=False))
        
    except Exception as e:
        print(f"Error processing data: {e}")
        return

def main():
    """Main function to run the COLI aggregation process."""
    print("Starting COLI aggregation process...")
    process_coli_data()
    print("COLI aggregation process completed.")

if __name__ == "__main__":
    main()
