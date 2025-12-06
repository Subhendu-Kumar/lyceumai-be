# Lyceum AI Backend

## Setup and Run Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/subhendu-kumar/lyceumai-be.git
cd lyceumai-be
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**On Windows:**

```bash
.venv\Scripts\activate
```

**On macOS/Linux:**

```bash
source .venv/bin/activate
```

### Step 4: Install Required Packages

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

Start the FastAPI server with Uvicorn:

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000` by default.

### Step 6: Access API Documentation

Visit the interactive API documentation at:

- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Database

This project uses Prisma as the ORM. Make sure to generate Prisma client:

```bash
prisma generate
```

## Environment Variables

Create a `.env` file in the root directory with necessary configuration variables (contact the team for required values).
