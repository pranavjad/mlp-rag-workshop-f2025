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


### Frontend (React + Vite)

1) Install frontend dependencies
```bash
cd frontend
npm install
```

2) Start the dev server
```bash
npm run dev
```
- Open http://localhost:5173
