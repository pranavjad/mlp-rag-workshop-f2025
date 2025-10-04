## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the server
Create a `.env` file with `GEMINI_API_KEY=<YOUR KEY HERE>`. Then run:
```
python server.py
```