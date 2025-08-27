import pandas as pd
import numpy as np
from datetime import datetime

class FlightInsurancePricingModel:
    """
    Dynamic pricing model for flight delay insurance based on risk factors.
    
    This model implements risk-based pricing to:
    1. Charge lower premiums for low-risk flights to expand the risk pool
    2. Charge higher premiums for high-risk flights to screen out risky customers
    3. Improve profitability through accurate risk segmentation
    """
    
    def __init__(self):
        """Initialize the pricing model with base parameters."""
        # Base premium calculation
        self.base_premium = 11.86  # Expected claim cost per flight
        self.claim_amount = 800    # Claim amount for delays > 3 hours or cancellations
        
        # Risk multipliers based on actual data analysis
        self._initialize_multipliers()
    
    def _initialize_multipliers(self):
        """Initialize risk multipliers based on statistical analysis."""
        
        # Airline risk multipliers (based on actual high-risk rates)
        self.airline_multipliers = {
            # High-risk airlines (risk rate > 5%)
            'SV': 44.99, 'PK': 16.67, 'E8': 4.73, '9C': 4.13, 'KC': 3.60,
            
            # Medium-high risk airlines (risk rate 2-5%)
            '2P': 3.27, 'OM': 3.27, 'LV': 3.00, 'BG': 2.93, 'FM': 2.93,
            'MU': 2.80, 'CZ': 2.67, 'HU': 2.53, '3U': 2.40, 'CA': 2.27,
            
            # Medium risk airlines (risk rate 1-2%)
            'MF': 1.87, 'ZH': 1.73, 'GS': 1.60, 'PN': 1.47, 'EU': 1.33,
            'JD': 1.20, 'NS': 1.07, 'GJ': 0.93, 'KY': 0.80, '8L': 0.67,
            
            # Low-risk airlines (risk rate < 1%)
            'default': 0.67  # Default for airlines not in the list
        }
        
        # Time-based multipliers
        self.hour_multipliers = {
            # High-risk hours (risk rate > 2%)
            3: 3.64,   # 3 AM - highest risk
            0: 1.87,   # Midnight
            6: 1.93,   # 6 AM
            
            # Medium-risk hours (risk rate 1.5-2%)
            11: 1.20, 12: 1.13, 13: 1.27, 15: 1.27, 17: 1.27, 18: 1.20, 19: 1.07, 20: 1.20, 21: 1.07,
            
            # Low-risk hours (risk rate < 1.5%)
            'default': 0.80  # Default for other hours
        }
        
        # Day of week multipliers
        self.day_multipliers = {
            6: 1.20,  # Sunday - highest risk
            4: 1.07,  # Friday
            5: 1.00,  # Saturday
            0: 0.93,  # Monday
            1: 0.93,  # Tuesday
            2: 1.00,  # Wednesday
            3: 0.73,  # Thursday - lowest risk
        }
        
        # Seasonal multipliers
        self.season_multipliers = {
            'Summer': 1.35,   # Highest risk
            'Winter': 1.07,   # Medium-high risk
            'Spring': 1.00,   # Medium risk
            'Fall': 0.60,     # Lowest risk
        }
        
        # Airport risk multipliers (top high-risk airports)
        self.airport_multipliers = {
            # High-risk arrival airports
            'SUB': 7.80, 'DOH': 3.87, 'ALA': 3.47, 'LYA': 3.33, 'SJW': 3.33,
            'PVG': 3.07, 'ULN': 2.87, 'TNA': 2.47, 'YNT': 2.40, 'WUS': 2.20,
            
            # Default multiplier for other airports
            'default': 1.00
        }
    
    def get_airline_multiplier(self, airline_code):
        """Get risk multiplier for a specific airline."""
        return self.airline_multipliers.get(airline_code, self.airline_multipliers['default'])
    
    def get_hour_multiplier(self, hour):
        """Get risk multiplier for a specific hour of day."""
        return self.hour_multipliers.get(hour, self.hour_multipliers['default'])
    
    def get_day_multiplier(self, day_of_week):
        """Get risk multiplier for a specific day of week (0=Monday, 6=Sunday)."""
        return self.day_multipliers.get(day_of_week, 1.00)
    
    def get_season_multiplier(self, month):
        """Get risk multiplier for a specific month."""
        season_map = {
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Fall', 10: 'Fall', 11: 'Fall'
        }
        season = season_map.get(month, 'Spring')
        return self.season_multipliers.get(season, 1.00)
    
    def get_airport_multiplier(self, airport_code):
        """Get risk multiplier for a specific airport."""
        return self.airport_multipliers.get(airport_code, self.airport_multipliers['default'])
    
    def calculate_premium(self, airline_code, departure_airport, arrival_airport, 
                         flight_date, flight_hour, base_premium=None):
        """
        Calculate insurance premium for a specific flight.
        
        Args:
            airline_code (str): Airline code
            departure_airport (str): Departure airport code
            arrival_airport (str): Arrival airport code
            flight_date (str or datetime): Flight date
            flight_hour (int): Hour of departure (0-23)
            base_premium (float, optional): Override base premium
            
        Returns:
            dict: Premium calculation details
        """
        # Convert date to datetime if string
        if isinstance(flight_date, str):
            flight_date = pd.to_datetime(flight_date)
        
        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = flight_date.weekday()
        month = flight_date.month
        
        # Get individual multipliers
        airline_mult = self.get_airline_multiplier(airline_code)
        hour_mult = self.get_hour_multiplier(flight_hour)
        day_mult = self.get_day_multiplier(day_of_week)
        season_mult = self.get_season_multiplier(month)
        dept_mult = self.get_airport_multiplier(departure_airport)
        arr_mult = self.get_airport_multiplier(arrival_airport)
        
        # Calculate combined multiplier (geometric mean for balance)
        combined_multiplier = np.power(
            airline_mult * hour_mult * day_mult * season_mult * dept_mult * arr_mult, 
            1/6
        )
        
        # Use provided base premium or default
        premium_base = base_premium if base_premium is not None else self.base_premium
        
        # Calculate final premium
        final_premium = premium_base * combined_multiplier
        
        # Risk category based on combined multiplier
        if combined_multiplier < 0.8:
            risk_category = "Low Risk"
        elif combined_multiplier < 1.2:
            risk_category = "Medium Risk"
        else:
            risk_category = "High Risk"
        
        return {
            'premium': round(final_premium, 2),
            'base_premium': round(premium_base, 2),
            'combined_multiplier': round(combined_multiplier, 3),
            'risk_category': risk_category,
            'multipliers': {
                'airline': round(airline_mult, 3),
                'hour': round(hour_mult, 3),
                'day': round(day_mult, 3),
                'season': round(season_mult, 3),
                'departure_airport': round(dept_mult, 3),
                'arrival_airport': round(arr_mult, 3)
            },
            'flight_details': {
                'airline': airline_code,
                'departure': departure_airport,
                'arrival': arrival_airport,
                'date': flight_date.strftime('%Y-%m-%d'),
                'hour': flight_hour,
                'day_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_of_week]
            }
        }
    
    def get_pricing_recommendations(self):
        """Get strategic pricing recommendations."""
        return {
            'base_premium': self.base_premium,
            'claim_amount': self.claim_amount,
            'risk_thresholds': {
                'low_risk': '< 0.8x multiplier',
                'medium_risk': '0.8x - 1.2x multiplier',
                'high_risk': '> 1.2x multiplier'
            },
            'key_factors': {
                'most_important': 'Airline (up to 45x multiplier)',
                'second_important': 'Arrival Airport (up to 8x multiplier)',
                'third_important': 'Season (0.6x - 1.35x multiplier)',
                'fourth_important': 'Time of Day (0.8x - 3.6x multiplier)',
                'fifth_important': 'Day of Week (0.7x - 1.2x multiplier)'
            },
            'business_strategy': {
                'low_risk_flights': 'Offer discounts to expand customer base',
                'medium_risk_flights': 'Standard pricing with slight adjustments',
                'high_risk_flights': 'Higher pricing to screen out risky customers'
            }
        }

def demonstrate_pricing_model():
    """Demonstrate the pricing model with example flights."""
    
    model = FlightInsurancePricingModel()
    
    print("FLIGHT INSURANCE PRICING MODEL DEMONSTRATION")
    print("=" * 60)
    
    # Example flights with different risk profiles
    example_flights = [
        {
            'name': 'Low-Risk Flight',
            'airline': 'default',
            'departure': 'HKG',
            'arrival': 'default',
            'date': '2024-01-15',  # Monday in Fall
            'hour': 14  # Afternoon
        },
        {
            'name': 'Medium-Risk Flight',
            'airline': 'FM',
            'departure': 'HKG',
            'arrival': 'PVG',
            'date': '2024-07-15',  # Monday in Summer
            'hour': 11  # Morning
        },
        {
            'name': 'High-Risk Flight',
            'airline': 'SV',
            'departure': 'HKG',
            'arrival': 'SUB',
            'date': '2024-07-21',  # Sunday in Summer
            'hour': 3   # Early morning
        }
    ]
    
    print("\nPremium Calculations for Different Flight Types:")
    print("-" * 60)
    
    for flight in example_flights:
        result = model.calculate_premium(
            airline_code=flight['airline'],
            departure_airport=flight['departure'],
            arrival_airport=flight['arrival'],
            flight_date=flight['date'],
            flight_hour=flight['hour']
        )
        
        print(f"\n{flight['name']}:")
        print(f"  Route: {result['flight_details']['departure']} → {result['flight_details']['arrival']}")
        print(f"  Airline: {result['flight_details']['airline']}")
        print(f"  Date: {result['flight_details']['date']} ({result['flight_details']['day_of_week']})")
        print(f"  Time: {result['flight_details']['hour']}:00")
        print(f"  Risk Category: {result['risk_category']}")
        print(f"  Premium: ${result['premium']:.2f}")
        print(f"  Combined Multiplier: {result['combined_multiplier']}x")
    
    # Get pricing recommendations
    recommendations = model.get_pricing_recommendations()
    
    print("\n" + "=" * 60)
    print("PRICING MODEL RECOMMENDATIONS")
    print("=" * 60)
    
    print(f"\nBase Premium: ${recommendations['base_premium']:.2f}")
    print(f"Claim Amount: ${recommendations['claim_amount']}")
    
    print("\nRisk Thresholds:")
    for risk_level, threshold in recommendations['risk_thresholds'].items():
        print(f"  {risk_level.replace('_', ' ').title()}: {threshold}")
    
    print("\nKey Risk Factors (by importance):")
    for factor, description in recommendations['key_factors'].items():
        print(f"  {factor.replace('_', ' ').title()}: {description}")
    
    print("\nBusiness Strategy:")
    for strategy, description in recommendations['business_strategy'].items():
        print(f"  {strategy.replace('_', ' ').title()}: {description}")
    
    print("\n" + "=" * 60)
    print("IMPLEMENTATION GUIDELINES")
    print("=" * 60)
    
    print("""
1. AIRLINE RISK SEGMENTATION:
   • High-risk airlines (SV, PK, E8, 9C, KC): Apply 2.0x - 45.0x multipliers
   • Medium-risk airlines (FM, MU, CZ, HU): Apply 1.0x - 3.0x multipliers  
   • Low-risk airlines (default): Apply 0.5x - 0.8x multipliers

2. TEMPORAL RISK ADJUSTMENTS:
   • Peak hours (3 AM, 6 AM): Apply 1.5x - 3.6x multipliers
   • Off-peak hours (8 AM, 2 PM): Apply 0.8x - 1.0x multipliers
   • Weekend flights: Apply 1.0x - 1.2x multipliers
   • Summer season: Apply 1.35x multiplier

3. AIRPORT RISK FACTORS:
   • High-risk arrival airports (SUB, DOH, ALA): Apply 3.0x - 8.0x multipliers
   • Standard airports: Apply 1.0x multiplier

4. PRICING STRATEGY:
   • Low-risk flights: Offer 20-40% discounts to attract customers
   • Medium-risk flights: Standard pricing with slight adjustments
   • High-risk flights: Apply 50-200% surcharges to screen out risky customers

5. MONITORING & ADJUSTMENT:
   • Track claim rates by risk category monthly
   • Adjust multipliers based on actual vs. expected claim rates
   • Seasonal recalibration of risk factors
   • Continuous monitoring of new airline performance
    """)

if __name__ == "__main__":
    demonstrate_pricing_model() 