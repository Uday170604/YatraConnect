# Prediction Approach - Booking Confirmation

## 1. Prediction Logic
The goal is to provide users with a dynamic "Booking Success Probability" score. In a real-world scenario, this would predict the likelihood of a waitlisted ticket getting confirmed. For this project, we calculate a score based on User Intent signals and market factors.

**Algorithm:**
```python
Base Probability = 85% (Baseline for confirmed inventory)

Factors:
1. Meal Inclusion: +5% (Indicates high commitment/intent)
2. Group Size: -3% (Larger groups have higher cancellation coordination risk)
3. Random Noise: +/- 5% (Simulates live market demand/traffic fluctuations)
```

## 2. Model Choice
We utilized a **Rule-Based Heuristic Model** (White-box approach) rather than a Black-box Neural Network for this iteration.
*   **Reasoning**: For a booking system where transparency is key, interpretable rules are superior to opaque models.
*   **Scalability**: This logic can easily be replaced by a Logistic Regression model when historical booking data becomes available.

## 3. Mock Dataset
To simulate testing, we conceptualized the following data structure:

| Booking ID | Date       | Passenger Count | Meal Added? | Status      |
|------------|------------|-----------------|-------------|-------------|
| B001       | 2024-01-20 | 1               | Yes         | Confirmed   |
| B002       | 2024-01-20 | 4               | No          | Cancelled   |
| B003       | 2024-01-21 | 2               | Yes         | Confirmed   |
| ...        | ...        | ...             | ...         | ...         |

## 4. Training Methodology
*   **Current State**: No "training" was performed as this is a deterministic rule-based system.
*   **Future State**: With 10,000+ records, we would split data (80% Train, 20% Test) and train a `scikit-learn` Logistic Regression classifier to optimize the weight of "Meal Inclusion" vs "Group Size".

## 5. Booking Probability Output
The final API and UI display a user-friendly percentage score.
*   **Output Format**: `87.5%`
*   **Visual**: A progress bar or badge color-coded (Green for >80%, Yellow for <50%).
