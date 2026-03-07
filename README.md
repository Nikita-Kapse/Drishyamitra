# 👁️ Drishyamitra

**AI-powered photo management system** with face recognition, chatbot interaction, and photo delivery.

---

## 🗂️ Project Structure

```
drishyamitra/
├── backend/         # Python Flask REST API
│   ├── app/         # App factory, config, database
│   ├── models/      # SQLAlchemy ORM models
│   ├── routes/      # API blueprints
│   ├── services/    # Business logic
│   ├── utils/       # File helpers
│   ├── uploads/     # Uploaded photos (gitignored)
│   └── start_server.py
└── frontend/        # React.js single-page application
    └── src/
        ├── components/  # Navbar
        ├── pages/       # UploadPage, GalleryPage, ChatbotPage
        └── services/    # API service (photoService.js)
```

---

## 🚀 Running the Project

### Backend (Flask)

```bash
cd backend

# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy the env example and fill in your keys
copy .env.example .env

# 4. Start the server
python start_server.py
```

The API will be available at **http://localhost:5000**

| Endpoint                | Method | Description            |
|-------------------------|--------|------------------------|
| `/`                     | GET    | Health check           |
| `/api/upload-photo`     | POST   | Upload a photo         |
| `/api/photos`           | GET    | List all photos        |
| `/api/photos/<id>`      | GET    | Get a single photo     |
| `/api/photos/<id>`      | DELETE | Delete a photo         |
| `/api/uploads/<file>`   | GET    | Serve an uploaded file |

---

### Frontend (React)

```bash
cd frontend
npm install
npm start
```

The app will open at **http://localhost:3000**

| Route      | Page        |
|------------|-------------|
| `/`        | Upload Page |
| `/gallery` | Gallery     |
| `/chat`    | AI Chatbot  |

---

## 🔧 Environment Variables (backend/.env)

| Variable           | Description                        |
|--------------------|------------------------------------|
| `GROQ_API_KEY`     | Groq LLM API key (future phase)    |
| `GMAIL_USER`       | Gmail address for photo delivery   |
| `GMAIL_APP_PASSWORD` | Gmail app password               |
| `DATABASE_URL`     | SQLAlchemy DB URL (default: SQLite)|
| `SECRET_KEY`       | Flask secret key                   |
| `FLASK_DEBUG`      | `true` / `false`                   |
| `UPLOAD_FOLDER`    | Directory for uploads              |

---

## 🐳 Docker

```bash
docker compose up --build
```

- Backend: http://localhost:5000
- Frontend: http://localhost:3000

---

## 🛣️ Roadmap

- [x] Base Flask REST API with photo upload / gallery / delete
- [x] React UI: Upload, Gallery, Chatbot pages
- [ ] Face recognition with DeepFace (Facenet512 + RetinaFace)
- [ ] AI chatbot via Groq API
- [ ] Photo delivery via Gmail
- [ ] User authentication
