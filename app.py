from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import json

app = Flask(__name__)

def load_country_mapping():
    try:
        with open('country_mapping.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading country mapping: {e}")
        return {}

COUNTRY_MAPPING = load_country_mapping()

# Load the rates data
def load_rates_data():
    try:
        csv_path = os.path.join('rates', 'rates.csv')
        df = pd.read_csv(csv_path)
        
        df['CountryName'] = df['CountryCode'].apply(lambda code: COUNTRY_MAPPING.get(code, {}).get('name', code))
        df['CountryFlag'] = df['CountryCode'].apply(lambda code: COUNTRY_MAPPING.get(code, {}).get('flag', '🏳️'))
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rates')
def get_rates():
    df = load_rates_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 500
    
    search = request.args.get('search', '').lower()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    sort_by = request.args.get('sort_by', 'CountryName')
    sort_order = request.args.get('sort_order', 'asc')
    
    if search:
        df = df[
            df['CountryCode'].str.lower().str.contains(search, na=False) |
            df['CountryName'].str.lower().str.contains(search, na=False)
        ]
    
    ascending = sort_order == 'asc'
    df = df.sort_values(by=sort_by, ascending=ascending)
    
    total_records = len(df)
    total_pages = (total_records + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_df = df.iloc[start_idx:end_idx]
    
    rates_data = paginated_df.to_dict('records')
    
    return jsonify({
        'data': rates_data,
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_records': total_records,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    })

@app.route('/api/stats')
def get_stats():
    df = load_rates_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 500
    
    stats = {
        'total_countries': len(df),
        'avg_rate': round(df['Rate'].mean(), 2),
        'min_rate': round(df['Rate'].min(), 2),
        'max_rate': round(df['Rate'].max(), 2),
        'median_rate': round(df['Rate'].median(), 2)
    }
    
    return jsonify(stats)

@app.route('/api/countries')
def get_countries():
    df = load_rates_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 500
    
    countries = []
    for _, row in df.iterrows():
        countries.append({
            'code': row['CountryCode'],
            'name': row['CountryName'],
            'flag': row['CountryFlag']
        })
    
    countries = sorted(countries, key=lambda x: x['name'])
    
    return jsonify(countries)

@app.route('/api/country/<country_code>')
def get_country_rate(country_code):
    df = load_rates_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 500
    
    country_data = df[df['CountryCode'].str.upper() == country_code.upper()]
    
    if country_data.empty:
        return jsonify({'error': 'Country not found'}), 404
    
    return jsonify(country_data.iloc[0].to_dict())

if __name__ == '__main__':
    app.run(port=8080)