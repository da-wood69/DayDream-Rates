"""
Sophisticated Hackathon Grant Rate Calculator

This algorithm calculates fair grant rates for different countries based on their economic indicators:
- PPP (Purchasing Power Parity): Measures relative purchasing power
- Inflation: Economic stability indicator 
- COLI (Cost of Living Index): Living cost comparison

The algorithm uses weighted economic theory to ensure fair distribution based on economic conditions.
"""

import pandas as pd
import numpy as np
import json
import os
import logging
from typing import Dict, Tuple, Optional
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore', category=FutureWarning)

class EconomicRateCalculator:
    """
    Sophisticated rate calculator using multiple economic indicators
    """
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the calculator with configuration"""
        self.config_path = config_path
        self.base_rate = self._load_config()
        
        # USA reference values (normalized to 1.0 for calculations)
        self.usa_ppp = 1.0
        self.usa_inflation = 2.95  # USA inflation rate
        self.usa_coli = 128.03     # USA COLI
        
        # Algorithm weights (tuned for optimal fairness)
        self.weights = {
            'ppp': 0.5,        # 50% - Primary purchasing power consideration
            'inflation': 0.25,  # 25% - Economic stability factor
            'coli': 0.25       # 25% - Living cost adjustment
        }
        
        # Data containers
        self.ppp_data = None
        self.inflation_data = None  
        self.coli_data = None
        self.merged_data = None
        
    def _load_config(self) -> float:
        """Load base rate from configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                base_rate = config.get('base_rate', 7.5)
                logger.info(f"Loaded base rate: ${base_rate}")
                return base_rate
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found, using default rate $7.50")
            return 7.5
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}")
            return 7.5
            
    def load_economic_data(self) -> None:
        """Load all economic indicator CSV files"""
        logger.info("Loading economic data files...")
        
        try:
            # Load PPP data
            self.ppp_data = pd.read_csv('final_data/PPP.csv')
            self.ppp_data.columns = ['country_code', 'ppp']
            logger.info(f"Loaded PPP data: {len(self.ppp_data)} countries")
            
            # Load Inflation data  
            self.inflation_data = pd.read_csv('final_data/INFLATION.csv')
            self.inflation_data.columns = ['country_code', 'inflation']
            logger.info(f"Loaded Inflation data: {len(self.inflation_data)} countries")
            
            # Load COLI data
            self.coli_data = pd.read_csv('final_data/COLI.csv')
            self.coli_data.columns = ['country_code', 'coli']
            logger.info(f"Loaded COLI data: {len(self.coli_data)} countries")
            
            # Validate data ranges
            self._validate_data_ranges()
            
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            raise
        except pd.errors.EmptyDataError as e:
            logger.error(f"Empty data file encountered: {e}")
            raise
            
    def _validate_data_ranges(self) -> None:
        """Validate data ranges and log statistics"""
        logger.info("Data validation summary:")
        
        # PPP validation
        ppp_min, ppp_max = self.ppp_data['ppp'].min(), self.ppp_data['ppp'].max()
        logger.info(f"PPP range: {ppp_min:.3f} - {ppp_max:.3f}")
        
        # Inflation validation  
        inf_min, inf_max = self.inflation_data['inflation'].min(), self.inflation_data['inflation'].max()
        logger.info(f"Inflation range: {inf_min:.2f}% - {inf_max:.2f}%")
        
        # COLI validation
        coli_min, coli_max = self.coli_data['coli'].min(), self.coli_data['coli'].max()
        logger.info(f"COLI range: {coli_min:.2f} - {coli_max:.2f}")
        
        # Check for extreme outliers
        if inf_max > 50:
            logger.warning(f"Extreme inflation detected: {inf_max:.2f}%")
        if ppp_min < 0.1:
            logger.warning(f"Very low PPP detected: {ppp_min:.3f}")
            
    def merge_datasets(self) -> pd.DataFrame:
        """Merge all economic datasets on country codes"""
        logger.info("Merging economic datasets...")
        
        # Start with PPP as base (most complete dataset)
        merged = self.ppp_data.copy()
        
        # Left join with inflation data
        merged = merged.merge(self.inflation_data, on='country_code', how='left')
        
        # Left join with COLI data
        merged = merged.merge(self.coli_data, on='country_code', how='left')
        
        # Log merge statistics
        total_countries = len(merged)
        complete_data = len(merged.dropna())
        missing_inflation = merged['inflation'].isna().sum()
        missing_coli = merged['coli'].isna().sum()
        
        logger.info(f"Merged dataset: {total_countries} total countries")
        logger.info(f"Complete data: {complete_data} countries")
        logger.info(f"Missing inflation: {missing_inflation} countries")
        logger.info(f"Missing COLI: {missing_coli} countries")
        
        self.merged_data = merged
        return merged
        
    def _handle_missing_data(self, row: pd.Series) -> pd.Series:
        """Handle missing data using intelligent defaults"""
        country_code = row['country_code']
        
        # Handle missing inflation (use global median for stability)
        if pd.isna(row['inflation']):
            row['inflation'] = self.merged_data['inflation'].median()
            logger.debug(f"Using median inflation for {country_code}")
            
        # Handle missing COLI (estimate from PPP relationship)
        if pd.isna(row['coli']):
            # Countries with higher PPP typically have higher COLI
            # Use regression-based estimation
            estimated_coli = self.usa_coli * (row['ppp'] ** 0.7)  # Power relationship
            row['coli'] = max(50, min(200, estimated_coli))  # Bound between reasonable limits
            logger.debug(f"Estimated COLI for {country_code}: {row['coli']:.2f}")
            
        return row
        
    def calculate_economic_adjustment_factor(self, ppp: float, inflation: float, coli: float) -> float:
        """
        CORRECTED VERSION:
        - Lower PPP = LOWER dollar amount (but equal purchasing power)
        - Lower COLI = LOWER dollar amount (but equal purchasing power)
        - Higher inflation = SMALL buffer increase
        """
        
        # PPP Factor: DIRECT relationship now
        # Pakistan PPP=0.3 → factor=0.3 → $50 * 0.3 = $15
        ppp_factor = ppp / self.usa_ppp  # This gives us the right scaling
        
        # Inflation Factor: Small buffer for volatile economies
        # But don't overdo it - maybe 10% max boost for high inflation
        inflation_ratio = inflation / self.usa_inflation
        inflation_factor = 1.0 + min((inflation_ratio - 1.0) * 0.1, 0.1)  # Max 10% boost
        
        # COLI Factor: DIRECT relationship  
        # Lower COLI = lower costs = lower grant needed
        coli_factor = coli / self.usa_coli
        
        # Weighted combination - ALL factors now reduce the rate for developing economies
        combined_factor = (
            self.weights['ppp'] * ppp_factor +
            self.weights['inflation'] * inflation_factor +
            self.weights['coli'] * coli_factor
        )
        
        # Final adjustment - this should be LESS than 1 for developing countries
        adjustment_factor = combined_factor
        
        # Apply reasonable bounds (don't go below 20% of US rate)
        adjustment_factor = max(0.2, min(1.2, adjustment_factor))
        
        return adjustment_factor
        
    def calculate_country_rate(self, country_data: pd.Series) -> float:
        """Calculate the final grant rate for a specific country"""
        country_code = country_data['country_code']
        
        # Handle missing data
        country_data = self._handle_missing_data(country_data)
        
        # Special case: USA gets exact base rate
        if country_code == 'USA':
            return self.base_rate
            
        # Extract economic indicators
        ppp = country_data['ppp']
        inflation = country_data['inflation']
        coli = country_data['coli']
        
        # Calculate adjustment factor
        adjustment_factor = self.calculate_economic_adjustment_factor(ppp, inflation, coli)
        
        # Apply to base rate
        adjusted_rate = self.base_rate * adjustment_factor
        
        # Round to 2 decimal places for currency
        adjusted_rate = round(adjusted_rate, 2)
        
        logger.debug(f"{country_code}: PPP={ppp:.3f}, Inflation={inflation:.2f}%, "
                    f"COLI={coli:.2f}, Factor={adjustment_factor:.3f}, Rate=${adjusted_rate}")
        
        return adjusted_rate
        
    def generate_all_rates(self) -> pd.DataFrame:
        """Generate rates for all countries with available data"""
        logger.info("Calculating rates for all countries...")
        
        if self.merged_data is None:
            raise ValueError("No merged data available. Call merge_datasets() first.")
            
        # Calculate rates for each country
        rates_data = []
        
        for _, row in self.merged_data.iterrows():
            country_code = row['country_code']
            try:
                rate = self.calculate_country_rate(row)
                rates_data.append({
                    'CountryCode': country_code,
                    'Rate': rate
                })
            except Exception as e:
                logger.error(f"Error calculating rate for {country_code}: {e}")
                # Use base rate as fallback
                rates_data.append({
                    'CountryCode': country_code,  
                    'Rate': self.base_rate
                })
                
        rates_df = pd.DataFrame(rates_data)
        logger.info(f"Generated rates for {len(rates_df)} countries")
        
        return rates_df
        
    def save_rates(self, rates_df: pd.DataFrame, output_path: str = "rates/rates.csv") -> None:
        """Save the calculated rates to CSV file"""
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Sort by country code for consistency
        rates_df_sorted = rates_df.sort_values('CountryCode')
        
        # Save to CSV
        rates_df_sorted.to_csv(output_path, index=False)
        logger.info(f"Rates saved to {output_path}")
        
        # Log statistics
        min_rate = rates_df['Rate'].min()
        max_rate = rates_df['Rate'].max()
        mean_rate = rates_df['Rate'].mean()
        usa_rate = rates_df[rates_df['CountryCode'] == 'USA']['Rate'].iloc[0] if 'USA' in rates_df['CountryCode'].values else None
        
        logger.info(f"Rate statistics:")
        logger.info(f"  Range: ${min_rate:.2f} - ${max_rate:.2f}")
        logger.info(f"  Mean: ${mean_rate:.2f}")
        if usa_rate:
            logger.info(f"  USA rate: ${usa_rate:.2f} (should be ${self.base_rate:.2f})")
            
    def run_complete_calculation(self) -> pd.DataFrame:
        """Execute the complete rate calculation pipeline"""
        logger.info("Starting complete rate calculation pipeline...")
        
        # Load data
        self.load_economic_data()
        
        # Merge datasets
        self.merge_datasets()
        
        # Generate rates
        rates_df = self.generate_all_rates()
        
        # Save results
        self.save_rates(rates_df)
        
        logger.info("Rate calculation pipeline completed successfully!")
        return rates_df


def main():
    try:
        calculator = EconomicRateCalculator()
        
        rates_df = calculator.run_complete_calculation()
        
        print(f"\n✅ Successfully generated rates for {len(rates_df)} countries")
        print(f"📁 Output saved to: rates/rates.csv")
        
        print(f"\n📊 Sample rates:")
        sample_countries = ['USA', 'DEU', 'IND', 'BRA', 'JPN']
        for country in sample_countries:
            if country in rates_df['CountryCode'].values:
                rate = rates_df[rates_df['CountryCode'] == country]['Rate'].iloc[0]
                print(f"  {country}: ${rate:.2f}")
                
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    main()
