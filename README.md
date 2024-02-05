# Task Manager Application

## Introduction
This Task Manager is a Flask-based web application developed by Szabolcs Balogh, demonstrating practical skills in full-stack web development. The application is designed to manage daily tasks, offering functionalities like task creation, modification, and deletion, all within a user-friendly and secure environment. It's now hosted online and accessible at [https://s2a31.pythonanywhere.com/](https://s2a31.pythonanywhere.com/).

## Features
- **User Authentication**: Secure registration and login processes using Flask-Bcrypt.
- **Task Management**: Ability to add, update, delete, and categorize tasks based on their status (Pending, In Progress, Completed).
- **Interactive User Interface**: Built with Bootstrap and custom CSS for a responsive design.
- **Drag-and-Drop Functionality**: Enhanced UX with JavaScript-implemented drag-and-drop feature for task categorization.
- **Database Integration**: Using MySQL to store and manage user and task data efficiently.

## Technologies Used
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Python, Flask
- **Database**: MySQL
- **Security**: Flask-Bcrypt for password hashing

## Access and Local Setup

### Access Online
The application is hosted and can be accessed directly at [https://s2a31.pythonanywhere.com/](https://s2a31.pythonanywhere.com/). Feel free to create an account and start managing your tasks.

### Local Setup (For Developers)
Developers who are interested in running the application locally or contributing to the project can set it up as follows:

1. **Clone the Repository**: 
   ```
   git clone https://github.com/s2a31/task-manager-web.git
   ```
2. **Install Dependencies**: 
   ```
   pip install -r requirements.txt
   ```
3. **Initialize Database**:
   Run the provided schema in your MySQL environment to set up the database.

4. **Run the Application Locally**:
   ```
   flask run
   ```
   Then navigate to `http://127.0.0.1:5000/` in your browser.

## Usage
After accessing the application online or running it locally:
1. Register a new user account or log in.
2. Start managing your tasks through the intuitive user interface.

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Szabolcs Balogh - baloghszabolcs43@gmail.com

## Acknowledgments
- Special thanks to online learning platforms like Udemy, Pluralsight, and CS50 that have been instrumental in my journey into the IT world.