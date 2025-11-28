# 🌟 PortfolioCraft — AI‑Powered Portfolio Builder

PortfolioCraft is an **AI-powered portfolio website generator** built using **Flask, Tailwind CSS, JavaScript, and OpenAI/Gemini APIs**. It converts a user’s **resume** into a **professional, editable portfolio website** with drag‑and‑drop sections, custom themes, and profile photo uploads.

Perfect for students, developers, designers, or professionals who want a fast, beautiful online portfolio.


## 🚀 Key Features

### 🔹 **AI‑Generated Portfolio Content**

Upload your resume (PDF/DOCX) and the AI converts it into:

- About Me
- Skills
- Experience
- Projects
- Education
- Certificates

All sections are **editable** before saving.

### 🔹 **Drag & Drop Section Reordering**

Users can reorder portfolio sections using **SortableJS** for full customization.

### 🔹 **User Authentication**

- Signup / Login system
- Personal dashboard
- User-specific saved portfolios

### 🔹 **Custom Themes + Dark/Light Mode**

Built‑in themes based on your color palette:

- Peach (#FCD8CD)
- Pink (#FEEBF6)
- Lavender (#EBD6FB)
- Royal Blue (#687FE5)

Includes theme selector + toggle button.

### 🔹 **Profile Photo Upload**

Optional photo upload to personalize portfolios.

### 🔹 **Responsive UI/UX**

Made with **Tailwind CSS** + custom styling.


## 🏗️ Tech Stack

| Layer          | Technology                     |
| -------------- | ------------------------------ |
| Backend        | Flask, Python, SQLite          |
| Frontend       | HTML, Tailwind CSS, JavaScript |
| AI             | OpenAI API / Gemini API        |
| Resume Parsing | PDFPlumber                     |
| Database ORM   | SQLAlchemy                     |
| Deployment     | Render.com                     |
| Extra          | SortableJS, Jinja Templates    |


## 📂 Project Structure

```
PortfolioCraft/
├── app/
│   ├── ai_processor.py
│   ├── forms.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── index.html
│   │   ├── portfolio_view.html
│   │   ├── upload.html
│   │   ├── upload_photo.html
│   │   └── theme-selector.html
├── uploads/
├── instance/
├── run.py
├── requirements.txt
├── README.md
└── .env
```


## ⚙️ Installation & Setup

### 🔧 1. Clone the Repository

```bash
git clone <your-repo-url>
cd PortfolioCraft
```

### 🐍 2. Create & Activate Virtual Environment

#### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 📦 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 🔑 4. Create .env File

Create a `.env` file in the root:

```
SECRET_KEY=your-secret-key
FLASK_ENV=development
DATABASE_URL=sqlite:///data.db
AI_API_KEY=YOUR_GEMINI_OR_OPENAI_KEY
UPLOAD_FOLDER=uploads
```

### 🗄️ 5. Initialize Database (If using migrations)

```bash
flask db upgrade
```

### ▶️ 6. Run the Application

```bash
flask run
```

Visit: [**http://127.0.0.1:5000**](http://127.0.0.1:5000)

---

## 🌐 Deploying on Render.com

### 1️⃣ Add Build Command

```
pip install -r requirements.txt
```

### 2️⃣ Add Start Command

```
gunicorn run:app --bind 0.0.0.0:$PORT
```

### 3️⃣ Add Environment Variables

- SECRET\_KEY
- DATABASE\_URL
- AI\_API\_KEY
- UPLOAD\_FOLDER

### 4️⃣ Connect GitHub → Auto Deploy

---

## 📤 API Integration (AI Processing)

`ai_processor.py` handles:

- Sending resume text to OpenAI/Gemini
- Formatting structured JSON response
- Returning portfolio-ready sections

Example flow:

```
Resume → PDFPlumber Extract → AI → JSON → Editable Portfolio Page
```


## 🧩 Core Modules

### 📌 `routes.py`

Contains all user-facing routes:

- Home
- Login / Signup
- Dashboard
- Resume Upload
- Portfolio Preview
- Save Portfolio

### 📌 `models.py`

Defines:

- User model
- Portfolio model
- Resume data storage

### 📌 `ai_processor.py`

AI resume → portfolio generator.

### 📌 `forms.py`

WTForms forms for login, signup, upload.


## 🎨 Frontend Features

- Tailwind-powered responsive UI
- Custom theme selector
- Dark/light toggle
- Drag & drop sections (SortableJS)
- Smooth animations and professional layout


## 🧪 Troubleshooting

### ❌ AI not generating?

- Check `AI_API_KEY` in `.env`
- Check network/Render logs

### ❌ Resume not uploading?

- Ensure `UPLOAD_FOLDER` exists
- Check file extensions in config

### ❌ TemplateSyntaxError?

- Look for unclosed `{% %}` or `{{ }}`

### ❌ Static files not loading?

- Use `url_for('static', filename='...')`


## 🛠️ Future Enhancements

- Export portfolio as HTML template
- More AI theme styles
- Add custom domain support
- Portfolio analytics dashboard


## ❤️ Credits

Developed by **Sharma Riya & Prajapati Shivam**, MCA (Cyber Security & Forensics).\
Built with passion, teamwork, and love.

If you like this project, ⭐ star the repo and share it!


## 📩 Need help?

I can generate:

- A complete PPT for your viva
- Architecture diagram
- Use-case diagrams
- ER diagram
- API documentation

Just ask! 🚀 **shivam4918@gmail.com**

