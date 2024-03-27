# Wallrus

**Steps to bring up the backend**   
1. **Create a virtual environment**   
  `cd backend`  
  `python -m venv wallrus_env`  
2. **Activate the virtual environment**   
  On windows: `wallrus_env\Scripts\activate`  
  On linux: `source wallrus_env/bin/activate`
3. **Install the requirements**  
  `pip install -r requirements.txt`
4. **Setup the database**  
  `python manage.py migrate`  
5. **Create a super user to access the admin panel**  
   `python manage.py createsuperuser` (input for type will be 0)  
6. **Run the server**  
  `python manage.py runserver`
  
  **Root URL for apis**: `http://127.0.0.1:8000/`   

**Steps to bring up the frontend**
1. **Install all dependencies**     
  `cd frontend`   
  `npm install`
2. **Run the server**   
  `npm start`
  
  
