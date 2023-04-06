import json

from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    degree = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    graduation_date = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Education {self.id}: {self.degree} at {self.school}>'


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Skill {self.id}: {self.name}>'

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    years = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Experience {self.id}: {self.name}>'

class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_required = db.Column(db.String(100), nullable=False)
    education_required = db.Column(db.String(100), nullable=True)
    experience_required = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<JobPosting {self.id}: skill required: {self.skill_required}: education required: {self.education_required}: experiencece required: {self.experience_required}>'

def get_experience(input_string):
    experiences = input_string.split(", ")
    jobs = []
    for exp in experiences:
        match = re.search(r'(.*) at (.*) from (\d{4}) to (\d{4}|Present)', exp)
        if match:
            job_position = match.group(1)
            # company = match.group(2)
            start_year = int(match.group(3))
            end_year_str = match.group(4)
            end_year = datetime.now().year if end_year_str.lower() == 'present' else int(end_year_str)
            years_of_exp = end_year - start_year
            jobs.append((job_position, years_of_exp))
    return jobs

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if all(key in request.form and request.form[key] != "" for key in ["degree", "school", "graduation_date"]) and ('skill' in request.form and request.form['skill'] != "") and ('experience' in request.form and request.form['experience'] != ""):
            degree = request.form['degree']
            school = request.form['school']
            graduation_date = request.form['graduation_date']
            try:
                education = Education(degree=degree, school=school, graduation_date=graduation_date)
                db.session.add(education)
                db.session.commit()
                db.session.close()
            except:
                return "ERROR OCCURRED"
            #---------------
            skill_name = request.form['skill']

            try:
                skill = Skill(name=skill_name)
                db.session.add(skill)
                db.session.commit()
                db.session.close()
            except:
                return "ERROR OCCURRED"
            #------------
            experience_name = request.form['experience']
            experience_years = ""
            experience = get_experience(experience_name)
            for i, (job_position, years_of_exp) in enumerate(experience):
                experience_years += f"{job_position}: {years_of_exp} years"
                if i != len(experience) - 1:
                    experience_years += ", "

            try:
                experience = Experience(name=experience_name, years=experience_years)
                db.session.add(experience)
                db.session.commit()
                db.session.close()
            except:
                return "ERROR OCCURRED IN EXPERIENCE TABLE"
            #-------------
            return redirect('/')
        #-------------
        elif 'jobpost_skills' in request.form:
            skills = request.form['jobpost_skills']
            education_required = request.form['jobpost_education']
            experience_required = request.form['jobpost_experience']

            try:
                jobposting = JobPosting(skill_required=skills, education_required=education_required, experience_required=experience_required)
                db.session.add(jobposting)
                db.session.commit()
                db.session.close()
                return redirect('/')
            except:
                return "ERROR OCCURRED ADDING JOBPOST"

    else:
        educations = Education.query.all()
        skills = Skill.query.all()
        experiences = Experience.query.all()
        jobs = JobPosting.query.all()
        return render_template('index.html', educations=educations, skills=skills, experiences=experiences, jobposts=jobs)



@app.route('/delete_education/<int:id>')
def delete_education(id):
    education = Education.query.get(id)
    try:
        db.session.delete(education)
        db.session.commit()
        return redirect('/')
    except:
        return "ERROR DELETING"


@app.route('/delete_skill/<int:id>')
def delete_skill(id):
    skill = Skill.query.get(id)
    try:
        db.session.delete(skill)
        db.session.commit()
        return redirect('/')
    except:
        return "ERROR DELETING"

@app.route('/delete_experience/<int:id>')
def delete_experience(id):
    experience = Experience.query.get(id)
    try:
        db.session.delete(experience)
        db.session.commit()
        return redirect('/')
    except:
        return "ERROR DELETING"

@app.route('/delete_jobpost/<int:id>')
def delete_jobpost(id):
    jobpost = JobPosting.query.get(id)
    try:
        db.session.delete(jobpost)
        db.session.commit()
        return redirect('/')
    except:
        return "ERROR DELETING"


@app.route('/jobposts_json')
def jobposts_json():
    jobposts = JobPosting.query.all()
    jobposts_json = [{'skill_required': jobpost.skill_required} for jobpost in jobposts]
    return jsonify(jobposts_json)

@app.route('/get_jobpost_name/<int:jobpost_id>')
def get_jobpost_name(jobpost_id):
    jobpost = JobPosting.query.filter_by(id=jobpost_id).first()
    if jobpost:
        jobpost_name = jobpost.skill_required
        return jsonify({'jobpost_name': jobpost_name})
    else:
        return jsonify({'error': 'Job post not found'})

@app.route('/get_education_required/<int:jobpost_id>')
def get_education_required(jobpost_id):
    jobpost = JobPosting.query.filter_by(id=jobpost_id).first()
    if jobpost:
        education_required = jobpost.education_required
        return jsonify({'education_required': education_required})
    else:
        return jsonify({'error': 'Job post not found'})

@app.route('/get_experience_required/<int:jobpost_id>')
def get_experience_required(jobpost_id):
    jobpost = JobPosting.query.filter_by(id=jobpost_id).first()
    if jobpost:
        experience_required = jobpost.experience_required
        return jsonify({'experience_required': experience_required})
    else:
        return jsonify({'error': 'Job post not found'})

@app.route('/skills_json')
def skills_json():
    skills = Skill.query.all()
    skills_json = [{'id': skill.id, 'name': skill.name} for skill in skills]
    return jsonify(skills_json)

@app.route('/degrees_json')
def degrees_json():
    degrees = Education.query.all()
    degrees_json = [{'id': degree.id, 'name': degree.degree} for degree in degrees]
    return jsonify(degrees_json)

@app.route('/experience_json')
def experience_json():
    experiences = Experience.query.all()
    experiences_json = [{'id': exp.id, 'years': exp.years} for exp in experiences]
    return jsonify(experiences_json)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
