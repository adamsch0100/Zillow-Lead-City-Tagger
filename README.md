# Zillow Lead City Tagger

Automatically enrich Zillow showing requests with city information and sync to Follow Up Boss CRM - saving real estate agents hours of manual data entry.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?logo=stripe&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-Deployed-0B0D0E?logo=railway&logoColor=white)

## The Problem

Real estate agents receive hundreds of Zillow showing requests, but the leads often lack critical city/location information. Manually looking up and tagging each lead takes hours every week.

## The Solution

City Tagger automatically:
1. Monitors incoming Zillow leads
2. Extracts property addresses
3. Geocodes to determine city/area
4. Tags leads in Follow Up Boss with the correct city
5. Runs 24/7 as a background service

## Features

- **Automatic Processing** - Set it and forget it lead enrichment
- **Follow Up Boss Integration** - Direct CRM sync via API
- **Real-time Dashboard** - Monitor processing status
- **Stripe Subscriptions** - SaaS billing built-in
- **Email Notifications** - Processing alerts and summaries
- **Multi-user Support** - Each agent gets their own instance

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python, Flask |
| **Database** | PostgreSQL (Supabase) |
| **Payments** | Stripe Subscriptions |
| **Email** | Transactional email service |
| **Deployment** | Railway |
| **Migrations** | Alembic |

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Zillow Leads   │────▶│  City Tagger     │────▶│  Follow Up Boss │
│  (via email)    │     │  Service         │     │  CRM            │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Dashboard       │
                        │  (Flask App)     │
                        └──────────────────┘
```

## Project Structure

```
city_tagger/
├── src/
│   ├── models/           # SQLAlchemy database models
│   ├── services/         # Lead processing logic
│   ├── utils/            # Helper scripts
│   ├── tests/            # Test suite
│   └── app.py            # Flask application
├── templates/            # HTML templates
│   ├── dashboard.html    # Main dashboard
│   ├── settings.html     # User settings
│   └── login.html        # Authentication
├── alembic/              # Database migrations
├── config/               # Configuration files
└── requirements.txt      # Python dependencies
```

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL database
- Follow Up Boss API access
- Stripe account (for subscriptions)

### Installation

```bash
# Clone and setup
git clone https://github.com/adamsch0100/Zillow-Lead-City-Tagger.git
cd Zillow-Lead-City-Tagger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/.env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start the application
python src/app.py
```

## Deployment

Deployed on Railway with automatic scaling:

```bash
railway login
railway init
railway up
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dashboard` | GET | Main dashboard view |
| `/settings` | GET/POST | User settings |
| `/api/process` | POST | Trigger lead processing |
| `/api/status` | GET | Service status |
| `/webhook/stripe` | POST | Stripe webhooks |

## Environment Variables

```env
FLASK_ENV=production
DATABASE_URL=postgresql://...
FUB_API_KEY=your_follow_up_boss_key
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
EMAIL_API_KEY=your_email_service_key
```

## License

Proprietary - All rights reserved.

---

Built to save real estate agents time and improve lead management efficiency.
