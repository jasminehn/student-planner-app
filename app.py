from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

#class Todo(db.Model):
 #   id = db.Column(db.Integer, primary_key=True)
 #   content = db.Column(db.String(200), nullable=False)
 #   date_created = db.Column(db.DateTime, default=datetime.utcnow)

#    def __repr__(self):
 #       return '<Task %r>' % self.id

class TaskList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    details = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    duedate = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id

#class CourseList(db.Model):
 #   id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(200), nullable=False)
 #   code = db.Column(db.String(200), nullable=False)
 #   semester = db.Column(db.String(200), nullable=False)
    
 #   def __repr__(self):
 #       return '<Course %r>' % self.id

@app.route('/', methods=['POST','GET']) #add get/post functionality here!!!
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        task_details = request.form['details']
        task_subject = request.form['subject']
        task_duedate = request.form['duedate']
        new_task = TaskList(content=task_content, details=task_details, subject=task_subject, duedate=task_duedate)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = TaskList.query.order_by(TaskList.duedate).all()
        return render_template('index.html', tasks=tasks)

        
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = TaskList.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = TaskList.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        task.details = request.form['details']
        task.subject = request.form['subject']
        task.duedate = request.form['duedate']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login_data = {
            #'utf8': '✓',
            #'authenticity_token': '1H45HviBe+Tx2g8fACOtaCbbeRWE3Z7RYGf7Nb6vDKGZFG0ozesaprSDdn5GUeA9Rbk1LLCKp7kJDJhTyNljxA==', #ORIGINAL
            #'authenticity_token': '2761~C9yI5vo5A7QjXpcuItqn7coJg6TchdFaJXBlmGPUJ0YsDI1xbBpMsfq345byOeyj',
            #'redirect_to_ssl': 1,
            #'pseudonym_session[unique_id]': 'jnelson20',
            #'pseudonym_session[password]': 'NE031413418yehet',
            #'pseudonym_session[remember_me]': 0

            'utf8': '✓',
            'authenticity_token': request.form['authtoken'],
            'redirect_to_ssl': 1,
            'pseudonym_session[unique_id]': request.form['username'],
            'pseudonym_session[password]': request.form['password'],
            'pseudonym_session[remember_me]': 0
            
        }
        with requests.Session() as s:
            url = "https://canvas.jcu.edu/login/ldap"
            url2 = "https://canvas.jcu.edu/api/v1/users/self/upcoming_events"
            url3 = "https://canvas.jcu.edu/api/v1/users/self/favorites/courses"
            r = s.get(url)
            #print(r.content)
            soup = BeautifulSoup(r.content, 'html.parser')
            login_data['authenticity_token'] = soup.find('input', attrs={'name': 'authenticity_token'})['value']
            #url2 = "https://canvas.jcu.edu/api/v1/users/self/upcoming_events"
            r = s.post(url, data=login_data)
            r = s.get(url2)
            #print(r.content)
            data_pull = r.content.decode('utf-8')
            look4title = '\"title\":'

            favorite_courses = s.get(url3).content.decode('utf-8')
            #titles = [i for i in range(len(data_pull)) if data_pull.startswith(b'look4title', i)]
            #titles = [i.start() for i in re.finditer(b'look4title', data_pull)]
            
            #print(data_pull)
            #print("> > > > The start indices of the substrings are : " + str(titles))
            #print(data_pull.split(b'look4title', 1)[0])

            thing = [m.start() for m in re.finditer(look4title, data_pull)] #prints the first one
            print(str(thing))

            result = re.search('\"title\":(.*?)\,', data_pull) #? makes ikt get the first one
            print(result.group(1))

            #TITLES
            titles = re.findall('\"title\":(.*?)\,', data_pull)
            print(titles)
            print(type(titles))            
            #SUBJECT
            subjects = re.findall('\"context_name\":(.*?)\,', data_pull)
            #DUE DATE
            duedates = re.findall('\"end_at\":(.*?)\,', data_pull)
            

            for (a, b, c) in zip(titles, subjects, duedates):    
                #print (a, b, c)            
                task_content = a
                task_details = "(canvas assignment)"
                task_subject = b
                task_duedate = c
                new_task = TaskList(content=task_content, details=task_details, subject=task_subject, duedate=task_duedate)
                db.session.add(new_task)

            #NAME
            coursename = re.findall('\"name\":(.*?)\,', favorite_courses)                       
            #COURSE CODE
            coursecode = re.findall('\"course_code\":(.*?)\,', favorite_courses)
            
            #for (a, b) in zip(coursename, coursecode):    
            #    print (a, b)            
            #    course_name = a
            #    course_code = b
             #   course_semester = "Spring 2021"
            #    new_course = CourseList(name=course_name, code=course_code, semester=course_semester)
             #   db.session.add(new_course)

            try:
                
                db.session.commit()
                return redirect('/')
            except:
                return 'There was an issue logging into Canvas'
            #result = re.search('\"title\":(.*)\"', data_pull)
            #print(result.group(1))
    else:
        #courses = CourseList.query.order_by(CourseList.semester).all()
        
        return render_template('index.html', error=error)

@app.route("/tasks")
def tasks():
    return render_template('tasks.html')

@app.route("/calendar")
def calendar():
    return render_template('calendar.html')

@app.route("/settings")
def settings():
    return render_template('settings.html')

@app.route("/info")
def info():
    return render_template('info.html')

if __name__ == "__main__":
    app.run(debug=True)