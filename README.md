# Stock Chat Assistant

A Django-based platform for investors and analysts to manage portfolios, receive recommendations, and interact with a smart stock chatbot.

---

## Features
- **Role-based dashboards** for Investors and Analysts
- **Portfolio management** and stock recommendations
- **Interactive chatbot** for real-time stock queries
- **Modern UI** with Bootstrap and HTMX for dynamic updates
- **Custom admin interface** for easy data management

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/anuragkasat/stock_chat_assistant.git
cd stock_chat_assistant
```

### 2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies:

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
**On Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create a Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 6. Start the Development Server
```bash
python manage.py runserver
```

Visit [http://localhost:8000/](http://localhost:8000/) in your browser.

---

## Chatbot Usage
- Go to the chat page from your dashboard.
- Enter a stock-related question (e.g., "Show me AAPL").
- The chatbot will fetch data and provide advice or visualizations.

---

## Notes
- To fetch live stock data, integrate `yfinance` in `fetch_and_plot_stock`.
- You can extend the chatbot logic in `core/views.py`.

---

## License
This project is for educational/demo purposes. Add your license as needed.
