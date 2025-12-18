# CMMS - Computerized Maintenance Management System

Professional bilingual (English/Hungarian) desktop maintenance management application built with Python and Flet.

## Quick Start

### Prerequisites
- Python 3.9+
- pip (Python package manager)

### Installation

1. Clone or download the project:
```bash
cd CMMS_Project
```

2. Create virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Project Structure

```
CMMS_Project/
├── config/              # Configuration files
│   ├── app_config.py    # App settings
│   └── constants.py     # Constants and enums
├── database/            # Database layer
│   ├── connection.py    # DB connection
│   ├── models.py        # SQLAlchemy models
│   └── session_manager.py
├── localization/        # i18n support
│   ├── translator.py    # Translation manager
│   └── translations/
│       ├── en.json      # English strings
│       └── hu.json      # Hungarian strings
├── services/            # Business logic layer
│   ├── auth_service.py
│   ├── asset_service.py
│   ├── inventory_service.py
│   └── ...
├── ui/                  # User interface
│   ├── screens/         # Screen components
│   ├── components/      # Reusable components
│   └── theme.py         # UI theme
├── utils/               # Utility functions
├── data/                # Data directories
│   ├── files/           # Uploaded files
│   ├── reports/         # Generated reports
│   └── logs/            # Application logs
├── tests/               # Unit tests
├── templates/           # Jinja2 templates
└── main.py              # Application entry point
```

## Features

- 👤 User authentication with role-based access (Manager/Technician)
- 🏭 Asset management (Production Line → Machine → Module)
- 📦 Inventory management with bulk import and QR codes
- 📋 Worksheet system with status workflow
- 🔧 Preventive maintenance scheduling
- 📊 Dashboard with charts and metrics
- 📄 Multi-page reports (PDF/CSV export)
- 🌍 Bilingual UI (English/Hungarian)
- 💾 Automated backup and restore
- 🔐 Secure password hashing (Argon2)

## Development Phases

See `docs/IMPLEMENTATION_PLAN.md` for detailed 12-phase implementation plan.

## License

Proprietary - All rights reserved

## Documentation

- `docs/IMPLEMENTATION_PLAN.md` - Detailed implementation roadmap
- `config/app_config.py` - Configuration reference
- `config/constants.py` - Constants and enums reference
