import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('default')
sns.set_palette("husl")

def load_and_explore_data():
    """
    Load the flight delays dataset and perform initial exploration.
    
    Returns:
        pd.DataFrame: Cleaned flight delays dataset
    """
    print("Loading flight delays dataset...")
    
    # Load the dataset
    df = pd.read_csv('Flight_delays_data.csv')
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst few rows:")
    print(df.head())
    
    print("\nDataset info:")
    print(df.info())
    
    print("\nBasic statistics:")
    print(df.describe())
    
    return df

def clean_and_prepare_data(df):
    """
    Clean and prepare the dataset for analysis.
    
    Args:
        df (pd.DataFrame): Raw flight delays dataset
        
    Returns:
        pd.DataFrame: Cleaned dataset
    """
    print("\nCleaning and preparing data...")
    
    # Convert delay_time to numeric, handling any non-numeric values
    df['delay_time'] = pd.to_numeric(df['delay_time'], errors='coerce')
    
    # Fill any NaN values in delay_time with 0
    df['delay_time'] = df['delay_time'].fillna(0)
    
    # Convert date column to datetime
    df['flight_date'] = pd.to_datetime(df['flight_date'])
    
    # Extract additional features
    df['year'] = df['flight_date'].dt.year
    df['month'] = df['flight_date'].dt.month
    df['day_of_week'] = df['flight_date'].dt.dayofweek
    df['season'] = df['flight_date'].dt.month.map({
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    })
    
    # Create risk categories based on claim logic
    # High risk: delay > 3 hours OR flight cancelled
    # Low risk: delay <= 3 hours AND not cancelled
    df['is_high_risk'] = (df['delay_time'] > 3) | (df['is_claim'] == 1)
    df['risk_category'] = df['is_high_risk'].map({True: 'High Risk', False: 'Low Risk'})
    
    # Create delay categories
    df['delay_category'] = pd.cut(df['delay_time'], 
                                 bins=[-np.inf, 0, 1, 2, 3, np.inf],
                                 labels=['No Delay', '0-1h', '1-2h', '2-3h', '>3h'])
    
    print(f"Data cleaning completed. Shape: {df.shape}")
    print(f"Risk distribution:\n{df['risk_category'].value_counts()}")
    
    return df

def analyze_risk_factors(df):
    """
    Analyze various factors that contribute to flight risk.
    
    Args:
        df (pd.DataFrame): Cleaned flight delays dataset
    """
    print("\n=== RISK FACTOR ANALYSIS ===")
    
    # 1. Overall risk statistics
    print("\n1. Overall Risk Statistics:")
    risk_stats = df.groupby('risk_category').agg({
        'Z)ght_id': 'count',
        'delay_time': ['mean', 'std', 'max']
    }).round(2)
    print(risk_stats)
    
    # 2. Risk by airline
    print("\n2. Risk by Airline:")
    airline_risk = df.groupby('Airline')['is_high_risk'].agg(['count', 'mean']).round(3)
    airline_risk.columns = ['Total_Flights', 'High_Risk_Rate']
    airline_risk = airline_risk.sort_values('High_Risk_Rate', ascending=False)
    print(airline_risk.head(10))
    
    # 3. Risk by departure/arrival airports
    print("\n3. Risk by Departure Airport:")
    dept_risk = df.groupby('Departure')['is_high_risk'].agg(['count', 'mean']).round(3)
    dept_risk.columns = ['Total_Flights', 'High_Risk_Rate']
    dept_risk = dept_risk[dept_risk['Total_Flights'] >= 100].sort_values('High_Risk_Rate', ascending=False)
    print(dept_risk.head(10))
    
    print("\n4. Risk by Arrival Airport:")
    arr_risk = df.groupby('Arrival')['is_high_risk'].agg(['count', 'mean']).round(3)
    arr_risk.columns = ['Total_Flights', 'High_Risk_Rate']
    arr_risk = arr_risk[arr_risk['Total_Flights'] >= 100].sort_values('High_Risk_Rate', ascending=False)
    print(arr_risk.head(10))
    
    # 4. Risk by time factors
    print("\n5. Risk by Time Factors:")
    
    # By hour of day
    hour_risk = df.groupby('std_hour')['is_high_risk'].agg(['count', 'mean']).round(3)
    hour_risk.columns = ['Total_Flights', 'High_Risk_Rate']
    print("Risk by Hour of Day:")
    print(hour_risk)
    
    # By day of week
    dow_risk = df.groupby('day_of_week')['is_high_risk'].agg(['count', 'mean']).round(3)
    dow_risk.columns = ['Total_Flights', 'High_Risk_Rate']
    dow_risk.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    print("\nRisk by Day of Week:")
    print(dow_risk)
    
    # By season
    season_risk = df.groupby('season')['is_high_risk'].agg(['count', 'mean']).round(3)
    season_risk.columns = ['Total_Flights', 'High_Risk_Rate']
    print("\nRisk by Season:")
    print(season_risk)
    
    # By month
    month_risk = df.groupby('month')['is_high_risk'].agg(['count', 'mean']).round(3)
    month_risk.columns = ['Total_Flights', 'High_Risk_Rate']
    print("\nRisk by Month:")
    print(month_risk)
    
    return {
        'airline_risk': airline_risk,
        'dept_risk': dept_risk,
        'arr_risk': arr_risk,
        'hour_risk': hour_risk,
        'dow_risk': dow_risk,
        'season_risk': season_risk,
        'month_risk': month_risk
    }

def create_visualizations(df, risk_factors):
    """
    Create comprehensive visualizations for the business report.
    
    Args:
        df (pd.DataFrame): Cleaned flight delays dataset
        risk_factors (dict): Dictionary containing risk factor analyses
    """
    print("\nCreating visualizations...")
    
    # Set up the plotting style
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    
    # 1. Overall Risk Distribution
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Flight Risk Analysis - Key Factors', fontsize=16, fontweight='bold')
    
    # Risk distribution
    risk_counts = df['risk_category'].value_counts()
    axes[0, 0].pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%', startangle=90)
    axes[0, 0].set_title('Overall Risk Distribution')
    
    # Delay time distribution
    axes[0, 1].hist(df[df['delay_time'] <= 6]['delay_time'], bins=30, alpha=0.7, edgecolor='black')
    axes[0, 1].axvline(x=3, color='red', linestyle='--', label='3-hour threshold')
    axes[0, 1].set_xlabel('Delay Time (hours)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Delay Time Distribution')
    axes[0, 1].legend()
    
    # Risk by hour of day
    hour_data = risk_factors['hour_risk']
    axes[0, 2].bar(hour_data.index, hour_data['High_Risk_Rate'], alpha=0.7)
    axes[0, 2].set_xlabel('Hour of Day')
    axes[0, 2].set_ylabel('High Risk Rate')
    axes[0, 2].set_title('Risk by Hour of Day')
    
    # Risk by day of week
    dow_data = risk_factors['dow_risk']
    axes[1, 0].bar(range(len(dow_data)), dow_data['High_Risk_Rate'], alpha=0.7)
    axes[1, 0].set_xticks(range(len(dow_data)))
    axes[1, 0].set_xticklabels(dow_data.index, rotation=45)
    axes[1, 0].set_ylabel('High Risk Rate')
    axes[1, 0].set_title('Risk by Day of Week')
    
    # Risk by season
    season_data = risk_factors['season_risk']
    axes[1, 1].bar(season_data.index, season_data['High_Risk_Rate'], alpha=0.7)
    axes[1, 1].set_ylabel('High Risk Rate')
    axes[1, 1].set_title('Risk by Season')
    
    # Top 10 high-risk airlines
    top_airlines = risk_factors['airline_risk'].head(10)
    axes[1, 2].barh(range(len(top_airlines)), top_airlines['High_Risk_Rate'], alpha=0.7)
    axes[1, 2].set_yticks(range(len(top_airlines)))
    axes[1, 2].set_yticklabels(top_airlines.index)
    axes[1, 2].set_xlabel('High Risk Rate')
    axes[1, 2].set_title('Top 10 High-Risk Airlines')
    
    plt.tight_layout()
    plt.savefig('risk_analysis_overview.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. Detailed Airline Analysis
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Airlines with sufficient data (>= 100 flights)
    significant_airlines = risk_factors['airline_risk'][risk_factors['airline_risk']['Total_Flights'] >= 100]
    top_10_airlines = significant_airlines.head(10)
    bottom_10_airlines = significant_airlines.tail(10)
    
    # High-risk airlines
    axes[0].barh(range(len(top_10_airlines)), top_10_airlines['High_Risk_Rate'], alpha=0.7, color='red')
    axes[0].set_yticks(range(len(top_10_airlines)))
    axes[0].set_yticklabels(top_10_airlines.index)
    axes[0].set_xlabel('High Risk Rate')
    axes[0].set_title('Top 10 High-Risk Airlines (≥100 flights)')
    
    # Low-risk airlines
    axes[1].barh(range(len(bottom_10_airlines)), bottom_10_airlines['High_Risk_Rate'], alpha=0.7, color='green')
    axes[1].set_yticks(range(len(bottom_10_airlines)))
    axes[1].set_yticklabels(bottom_10_airlines.index)
    axes[1].set_xlabel('High Risk Rate')
    axes[1].set_title('Top 10 Low-Risk Airlines (≥100 flights)')
    
    plt.tight_layout()
    plt.savefig('airline_risk_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3. Airport Risk Analysis
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Top high-risk departure airports
    top_dept = risk_factors['dept_risk'].head(10)
    axes[0].barh(range(len(top_dept)), top_dept['High_Risk_Rate'], alpha=0.7, color='orange')
    axes[0].set_yticks(range(len(top_dept)))
    axes[0].set_yticklabels(top_dept.index)
    axes[0].set_xlabel('High Risk Rate')
    axes[0].set_title('Top 10 High-Risk Departure Airports')
    
    # Top high-risk arrival airports
    top_arr = risk_factors['arr_risk'].head(10)
    axes[1].barh(range(len(top_arr)), top_arr['High_Risk_Rate'], alpha=0.7, color='purple')
    axes[1].set_yticks(range(len(top_arr)))
    axes[1].set_yticklabels(top_arr.index)
    axes[1].set_xlabel('High Risk Rate')
    axes[1].set_title('Top 10 High-Risk Arrival Airports')
    
    plt.tight_layout()
    plt.savefig('airport_risk_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 4. Temporal Analysis
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Monthly trend
    month_data = risk_factors['month_risk']
    axes[0, 0].plot(month_data.index, month_data['High_Risk_Rate'], marker='o', linewidth=2)
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('High Risk Rate')
    axes[0, 0].set_title('Risk Trend by Month')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Hourly pattern
    hour_data = risk_factors['hour_risk']
    axes[0, 1].plot(hour_data.index, hour_data['High_Risk_Rate'], marker='o', linewidth=2)
    axes[0, 1].set_xlabel('Hour of Day')
    axes[0, 1].set_ylabel('High Risk Rate')
    axes[0, 1].set_title('Risk Pattern by Hour of Day')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Day of week
    dow_data = risk_factors['dow_risk']
    axes[1, 0].bar(range(len(dow_data)), dow_data['High_Risk_Rate'], alpha=0.7)
    axes[1, 0].set_xticks(range(len(dow_data)))
    axes[1, 0].set_xticklabels(dow_data.index, rotation=45)
    axes[1, 0].set_ylabel('High Risk Rate')
    axes[1, 0].set_title('Risk by Day of Week')
    
    # Season
    season_data = risk_factors['season_risk']
    axes[1, 1].bar(season_data.index, season_data['High_Risk_Rate'], alpha=0.7)
    axes[1, 1].set_ylabel('High Risk Rate')
    axes[1, 1].set_title('Risk by Season')
    
    plt.tight_layout()
    plt.savefig('temporal_risk_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def suggest_pricing_model(df, risk_factors):
    """
    Suggest a pricing model based on the risk analysis.
    
    Args:
        df (pd.DataFrame): Cleaned flight delays dataset
        risk_factors (dict): Dictionary containing risk factor analyses
    """
    print("\n=== PRICING MODEL SUGGESTION ===")
    
    # Calculate base risk rates
    overall_high_risk_rate = df['is_high_risk'].mean()
    base_premium = 800 * overall_high_risk_rate  # Expected claim amount
    
    print(f"Overall high-risk rate: {overall_high_risk_rate:.3f}")
    print(f"Base premium (expected claim): ${base_premium:.2f}")
    
    # Risk multipliers for different factors
    print("\nRisk Multipliers by Factor:")
    
    # Airline risk multiplier
    airline_multipliers = risk_factors['airline_risk']['High_Risk_Rate'] / overall_high_risk_rate
    print(f"Airline risk multipliers range: {airline_multipliers.min():.2f} - {airline_multipliers.max():.2f}")
    
    # Time-based multipliers
    hour_multipliers = risk_factors['hour_risk']['High_Risk_Rate'] / overall_high_risk_rate
    print(f"Hour-based multipliers range: {hour_multipliers.min():.2f} - {hour_multipliers.max():.2f}")
    
    season_multipliers = risk_factors['season_risk']['High_Risk_Rate'] / overall_high_risk_rate
    print(f"Season-based multipliers range: {season_multipliers.min():.2f} - {season_multipliers.max():.2f}")
    
    # Suggested pricing model
    print("\n=== SUGGESTED PRICING MODEL ===")
    print("Premium = Base Premium × Airline Multiplier × Time Multiplier × Season Multiplier")
    print(f"Base Premium: ${base_premium:.2f}")
    print("\nMultiplier Categories:")
    print("Airline: Low-risk (0.5-0.8), Medium-risk (0.8-1.2), High-risk (1.2-2.0)")
    print("Time: Off-peak (0.8-1.0), Peak (1.0-1.3)")
    print("Season: Low-season (0.8-1.0), High-season (1.0-1.4)")
    
    return {
        'base_premium': base_premium,
        'airline_multipliers': airline_multipliers,
        'hour_multipliers': hour_multipliers,
        'season_multipliers': season_multipliers
    }

def generate_business_report(df, risk_factors, pricing_model):
    """
    Generate a comprehensive business report.
    
    Args:
        df (pd.DataFrame): Cleaned flight delays dataset
        risk_factors (dict): Dictionary containing risk factor analyses
        pricing_model (dict): Dictionary containing pricing model components
    """
    print("\n" + "="*80)
    print("FLIGHT DELAY RISK ANALYSIS - BUSINESS REPORT")
    print("="*80)
    
    print("\nEXECUTIVE SUMMARY")
    print("-" * 40)
    total_flights = len(df)
    high_risk_flights = df['is_high_risk'].sum()
    high_risk_rate = high_risk_flights / total_flights
    
    print(f"• Analyzed {total_flights:,} flights from 2013-2016")
    print(f"• {high_risk_flights:,} flights ({high_risk_rate:.1%}) qualify for $800 claim")
    print(f"• Expected claim cost per flight: ${pricing_model['base_premium']:.2f}")
    
    print("\nKEY FINDINGS")
    print("-" * 40)
    
    # Top risk factors
    print("1. AIRLINE RISK:")
    top_airlines = risk_factors['airline_risk'][risk_factors['airline_risk']['Total_Flights'] >= 100].head(3)
    for airline, row in top_airlines.iterrows():
        print(f"   • {airline}: {row['High_Risk_Rate']:.1%} high-risk rate")
    
    print("\n2. TEMPORAL RISK:")
    worst_hour = risk_factors['hour_risk'].loc[risk_factors['hour_risk']['High_Risk_Rate'].idxmax()]
    worst_day = risk_factors['dow_risk'].loc[risk_factors['dow_risk']['High_Risk_Rate'].idxmax()]
    worst_season = risk_factors['season_risk'].loc[risk_factors['season_risk']['High_Risk_Rate'].idxmax()]
    
    print(f"   • Highest risk hour: {worst_hour.name}:00 ({worst_hour['High_Risk_Rate']:.1%})")
    print(f"   • Highest risk day: {worst_day.name} ({worst_day['High_Risk_Rate']:.1%})")
    print(f"   • Highest risk season: {worst_season.name} ({worst_season['High_Risk_Rate']:.1%})")
    
    print("\n3. AIRPORT RISK:")
    top_dept = risk_factors['dept_risk'].head(3)
    for airport, row in top_dept.iterrows():
        print(f"   • Departure: {airport} ({row['High_Risk_Rate']:.1%} high-risk rate)")
    
    print("\nPRICING MODEL RECOMMENDATION")
    print("-" * 40)
    print("Implement dynamic pricing based on:")
    print("1. Airline risk profile (0.5x - 2.0x multiplier)")
    print("2. Time of day and day of week (0.8x - 1.3x multiplier)")
    print("3. Seasonal patterns (0.8x - 1.4x multiplier)")
    print("4. Route-specific risk (departure/arrival airport combination)")
    
    print("\nEXPECTED BENEFITS")
    print("-" * 40)
    print("• Better risk segmentation and pricing accuracy")
    print("• Increased customer acquisition for low-risk flights")
    print("• Natural screening of high-risk customers")
    print("• Improved profitability through risk-based pricing")
    
    print("\n" + "="*80)

def main():
    """
    Main function to execute the complete analysis.
    """
    print("FLIGHT DELAY RISK ANALYSIS FOR TRAVEL INSURANCE PRICING")
    print("=" * 60)
    
    # Load and explore data
    df = load_and_explore_data()
    
    # Clean and prepare data
    df = clean_and_prepare_data(df)
    
    # Analyze risk factors
    risk_factors = analyze_risk_factors(df)
    
    # Create visualizations
    create_visualizations(df, risk_factors)
    
    # Suggest pricing model
    pricing_model = suggest_pricing_model(df, risk_factors)
    
    # Generate business report
    generate_business_report(df, risk_factors, pricing_model)
    
    # Save processed data for further analysis
    df.to_csv('processed_flight_data.csv', index=False)
    print("\nProcessed data saved to 'processed_flight_data.csv'")
    
    print("\nAnalysis completed! Check the generated visualizations and business report above.")

if __name__ == "__main__":
    main() 