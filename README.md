# Event-Management

# Event Management System – Setup Instructions

Follow the steps below to set up and run the Event Management API project on your local machine.

---

## 🔧 1. Clone the Repository

```bash
git clone <your-repository-url>
cd event_manager

windows
python -m venv venv
venv\Scripts\activate

Mac/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

http://127.0.0.1:8000/
POST /api/auth/token/
{
  "username": "your_username",
  "password": "your_password"
}
In Headers add this:
Authorization: Bearer <access_token>




