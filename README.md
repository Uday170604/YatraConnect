# Sleeper Bus Ticket Booking System 🚌

A premium Django-based booking platform for intercity sleeper bus travel, featuring real-time seat selection, meal integration, and AI-powered booking predictions.


## ✨ Defined Features
1.  **Backend API Implementation**: Robust RESTful API using **Django REST Framework** with `ViewSets` and `Routers`.
2.  **Visual Seat Selection**: Interactive map distinguishing Lower (L1-L15) vs. Upper (U1-U15) deck sleeper seats.
3.  **Smart Prediction Logic**: Mock AI algorithm calculating a "Confirmation Probability %" based on user intent signals (meal choice, group size).
4.  **Concurrency Handling**: Prevents double-booking using Atomic Transactions and Row Locking.
5.  **Integrated Add-ons**: Seamless meal booking (Veg/Snack) affecting total fare calculation.

## 🧪 Test Cases
### Functional Tests
- [x] **Seat Booking Flow**: User selects seat -> Fills Passenger Details -> Booking Creation Success.
- [x] **API Validation**: Rejects invalid phone numbers (non-10 digits) and names (special characters).
- [x] **Race Condition Check**: Concurrent requests for the same seat results in one success and one failure.

### Edge Cases
- [x] **Zero Availability**: System gracefully handles full bus scenario.
- [x] **Data Integrity**: Checks ensuring Seat status updates strictly match Booking records.

## 🛠️ Setup Instructions
1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd sleeper_bus_project
    ```
2.  **Install Dependencies**:
    ```bash
    pip install django djangorestframework
    ```
3.  **Initialize Database**:
    ```bash
    python manage.py migrate
    python manage.py shell -c "import populate_db; populate_db.run()"
    ```
4.  **Run Application**:
    ```bash
    python manage.py runserver
    ```

<img width="940" height="467" alt="image" src="https://github.com/user-attachments/assets/79603bd7-759f-42d8-bed5-2eb9101fe8e7" />
<img width="940" height="467" alt="image" src="https://github.com/user-attachments/assets/4cd6b833-5a1a-4b4f-b305-eba76d8d91f6" />
<img width="940" height="465" alt="image" src="https://github.com/user-attachments/assets/6076a2b5-a14b-43ab-9212-da9356541579" />
