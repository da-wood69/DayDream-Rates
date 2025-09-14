import pandas as pd
import os

# Country name to ISO code mapping
country_to_iso = {
    'Cayman Islands': 'KY',
    'Switzerland': 'CH',
    'Iceland': 'IS',
    'Bahamas': 'BS',
    'Singapore': 'SG',
    'Norway': 'NO',
    'Denmark': 'DK',
    'Luxembourg': 'LU',
    'Hong Kong (China)': 'HK',
    'Guernsey': 'GG',
    'Israel': 'IL',
    'Isle Of Man': 'IM',
    'Netherlands': 'NL',
    'Austria': 'AT',
    'Ireland': 'IE',
    'Papua New Guinea': 'PG',
    'United States': 'US',
    'Germany': 'DE',
    'Finland': 'FI',
    'France': 'FR',
    'United Kingdom': 'GB',
    'Belgium': 'BE',
    'Australia': 'AU',
    'Sweden': 'SE',
    'South Korea': 'KR',
    'Canada': 'CA',
    'Puerto Rico': 'PR',
    'New Zealand': 'NZ',
    'Italy': 'IT',
    'Macao (China)': 'MO',
    'Estonia': 'EE',
    'Cyprus': 'CY',
    'United Arab Emirates': 'AE',
    'Malta': 'MT',
    'Uruguay': 'UY',
    'Greece': 'GR',
    'Slovenia': 'SI',
    'Costa Rica': 'CR',
    'Jamaica': 'JM',
    'Yemen': 'YE',
    'Taiwan': 'TW',
    'Trinidad And Tobago': 'TT',
    'Latvia': 'LV',
    'Japan': 'JP',
    'Croatia': 'HR',
    'Spain': 'ES',
    'Lithuania': 'LT',
    'Czech Republic': 'CZ',
    'Guyana': 'GY',
    'Qatar': 'QA',
    'Slovakia': 'SK',
    'Democratic Republic of the Congo': 'CD',
    'Bahrain': 'BH',
    'Brunei': 'BN',
    'Maldives': 'MV',
    'Portugal': 'PT',
    'Senegal': 'SN',
    'Albania': 'AL',
    'Poland': 'PL',
    'Panama': 'PA',
    'Palestine': 'PS',
    'Ivory Coast': 'CI',
    'Hungary': 'HU',
    'Belize': 'BZ',
    'Botswana': 'BW',
    'Ethiopia': 'ET',
    'Saudi Arabia': 'SA',
    'Serbia': 'RS',
    'Armenia': 'AM',
    'Lebanon': 'LB',
    'Kuwait': 'KW',
    'Cuba': 'CU',
    'Montenegro': 'ME',
    'Cameroon': 'CM',
    'Bulgaria': 'BG',
    'Oman': 'OM',
    'Argentina': 'AR',
    'Romania': 'RO',
    'Turkey': 'TR',
    'Guatemala': 'GT',
    'Mexico': 'MX',
    'El Salvador': 'SV',
    'Mauritius': 'MU',
    'Jordan': 'JO',
    'Russia': 'RU',
    'Chile': 'CL',
    'Bosnia And Herzegovina': 'BA',
    'Mozambique': 'MZ',
    'Venezuela': 'VE',
    'Thailand': 'TH',
    'Dominican Republic': 'DO',
    'Honduras': 'HN',
    'North Macedonia': 'MK',
    'Moldova': 'MD',
    'Zambia': 'ZM',
    'Zimbabwe': 'ZW',
    'Fiji': 'FJ',
    'Cambodia': 'KH',
    'Sri Lanka': 'LK',
    'Nicaragua': 'NI',
    'South Africa': 'ZA',
    'Namibia': 'NA',
    'Georgia': 'GE',
    'Malaysia': 'MY',
    'Ghana': 'GH',
    'Mongolia': 'MN',
    'Morocco': 'MA',
    'Peru': 'PE',
    'Rwanda': 'RW',
    'Philippines': 'PH',
    'China': 'CN',
    'Azerbaijan': 'AZ',
    'Ecuador': 'EC',
    'Brazil': 'BR',
    'Kenya': 'KE',
    'Colombia': 'CO',
    'Kosovo (Disputed Territory)': 'XK',
    'Tunisia': 'TN',
    'Iraq': 'IQ',
    'Algeria': 'DZ',
    'Kazakhstan': 'KZ',
    'Tajikistan': 'TJ',
    'Ukraine': 'UA',
    'Vietnam': 'VN',
    'Nigeria': 'NG',
    'Kyrgyzstan': 'KG',
    'Bolivia': 'BO',
    'Uganda': 'UG',
    'Belarus': 'BY',
    'Uzbekistan': 'UZ',
    'Indonesia': 'ID',
    'Tanzania': 'TZ',
    'Syria': 'SY',
    'Paraguay': 'PY',
    'Iran': 'IR',
    'Nepal': 'NP',
    'Madagascar': 'MG',
    'Bangladesh': 'BD',
    'Egypt': 'EG',
    'Afghanistan': 'AF',
    'India': 'IN',
    'Pakistan': 'PK',
    'Libya': 'LY'
}

def convert_csv_country_names_to_iso():
    """
    Read the CSV file, replace country names with ISO codes,
    and save the result to data/COLI Numbeo Raw data.csv
    """
    # Read the original CSV file
    input_file = '3b01c9af-8832-43b9-b420-6bb216e68ca5.csv'
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    # Read the CSV file
    try:
        df = pd.read_csv(input_file)
        print(f"Successfully read CSV file with {len(df)} rows.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Create data directory if it doesn't exist
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
    
    # Replace country names with ISO codes
    countries_not_found = []
    for index, row in df.iterrows():
        country_name = row['Country']
        if country_name in country_to_iso:
            df.at[index, 'Country'] = country_to_iso[country_name]
        else:
            countries_not_found.append(country_name)
    
    # Report any countries not found in mapping
    if countries_not_found:
        print(f"Warning: The following countries were not found in the ISO mapping:")
        for country in countries_not_found:
            print(f"  - {country}")
    
    # Save the modified DataFrame to new CSV file
    output_file = os.path.join(data_dir, 'COLI Numbeo Raw data.csv')
    try:
        df.to_csv(output_file, index=False)
        print(f"Successfully saved converted data to: {output_file}")
        print(f"Converted {len(df) - len(countries_not_found)} country names to ISO codes.")
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        return

if __name__ == "__main__":
    convert_csv_country_names_to_iso()