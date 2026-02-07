📝 Review Sentiment Analysis Web App (Flask)

A simple Flask-based web application where users can submit reviews and an admin dashboard displays sentiment analysis results.
Built as a learning + portfolio project, focusing on backend logic, authentication flow, and deployment.

🚀 Features
👤 User Side

Submit text reviews

Automatic sentiment analysis:

Positive / Negative

Word count for each review

🔐 Admin Side

Admin signup & login

Admin dashboard to:

View all submitted reviews

See sentiment and word count

Logout functionality

Password reset flow (demo implementation)

🧠 Tech Stack

Backend: Flask (Python)

Frontend: HTML, CSS (Jinja templates)

Sentiment Analysis: TextBlob (NLP)

Storage: CSV files

<img width="449" height="520" alt="image" src="https://github.com/user-attachments/assets/8e00bdb2-245f-4b06-9cc5-7c75e9b57412" />





⚙️ How It Works (High Level)

Users submit reviews from the home page

TextBlob analyzes sentiment

Review data is stored in a CSV file

Admin logs in to view all reviews

Password reset uses token-based flow (demo-safe)

Deployment: Render

Production Server: Gunicorn
