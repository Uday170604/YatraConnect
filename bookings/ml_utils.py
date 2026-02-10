import random

def predict_booking_confirmation(date, seat_count, meal_included):
    """
    Mock logic to predict booking confirmation probability.
    
    Factors considered (Mock):
    - Date: Weekend vs Value
    - Seat Count: More seats -> slightly lower probability (group coordination)
    - Meal Included: Higher intent -> higher probability
    """
    
    base_probability = 85.0
    
    # Mock Factor 1: Random slight variation
    variation = random.uniform(-5.0, 5.0)
    
    # Mock Factor 2: Meal inclusion (Higher intent)
    if meal_included:
        base_probability += 5.0
        
    # Mock Factor 3: Seat count (More seats = slightly riskier or more committed? Let's say riskier for mock)
    if seat_count > 2:
        base_probability -= 3.0
        
    final_score = base_probability + variation
    
    # Clamp between 0 and 100
    final_score = max(0.0, min(100.0, final_score))
    
    return round(final_score, 2)
