# City Tagger Service

Automatically tag Zillow showing requests with city information in Follow Up Boss.

## Project Structure

```
city_tagger/
├── src/
│   ├── models/
│   │   ├── models.py         # SQLAlchemy models
│   │   └── database.py      # Database connection and operations
│   ├── services/
│   │   ├── zillow_lead_tagger.py    # Lead processing logic
│   │   └── city_tagger_service.py   # Background service
│   ├── utils/
│   │   ├── setup_stripe_products.py  # Stripe product setup
│   │   ├── list_stripe_products.py   # List Stripe products
│   │   ├── monitor_service.py        # Service monitoring
│   │   └── check_user.py            # User verification
│   ├── tests/
│   │   ├── test_mail.py             # Email testing
│   │   ├── test_signup_flow.py      # Signup flow testing
│   │   └── create_test_*.py         # Test data creation
│   └── app.py                       # Main Flask application
├── config/
│   ├── schema.sql                   # Database schema
│   ├── alembic.ini                  # Alembic configuration
│   └── .env.example                 # Environment variables example
├── templates/                       # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   └── settings.html
├── alembic/                        # Database migrations
├── requirements.txt                # Python dependencies
├── project_management.md           # Project tracking
└── README.md                      # This file

## Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/city_tagger.git
cd city_tagger
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp config/.env.example .env
# Edit .env with your configuration
```

5. Initialize the database
```bash
# Using Supabase, follow migration instructions in schema.sql
```

## Development

1. Run the Flask application
```bash
python src/app.py
```

2. Run tests
```bash
cd src/tests
python -m pytest
```

## Deployment to Railway

1. Install Railway CLI
2. Login to Railway
```bash
railway login
```

3. Initialize Railway project
```bash
railway init
```

4. Add environment variables
```bash
railway vars set FLASK_ENV=production
# Add other required environment variables
```

5. Deploy
```bash
railway up
```

## Features

- Automatic city tagging for Zillow leads
- Follow Up Boss integration
- Stripe subscription management
- Email notifications
- Dashboard for monitoring
- Real-time lead processing

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is proprietary and confidential. 