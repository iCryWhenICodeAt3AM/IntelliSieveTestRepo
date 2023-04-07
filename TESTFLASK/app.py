import json

from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

from sqlalchemy import text, update

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
    job_title = db.Column(db.String(100), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    job_description = db.Column(db.String(100), nullable=True)
    recommended = db.Column(db.String(100), nullable=True)

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
            company = request.form['jobpost_company']
            job_title = request.form['jobpost_title']
            job_description = request.form['jobpost_description']
            try:
                jobposting = JobPosting(skill_required=skills, education_required=education_required, experience_required=experience_required, job_title=job_title, company=company,job_description=job_description)
                db.session.add(jobposting)
                db.session.commit()
                db.session.close()
                getPercentage()  # to get the scores first and also add it to the list
                return redirect('/home')
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
        return redirect('/recruiter')
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




@app.route('/recruiter')
def recruiter():
    jobs = JobPosting.query.all()
    return render_template('recruiter.html', jobposts=jobs)

@app.route('/jobpost')
def jobpost():
    return render_template('jobpost.html')

@app.route('/jobpostinfo')
def jobpostinfo():
    id = request.args.get('id')
    jobs = JobPosting.query.filter(JobPosting.id == id).all()
    return render_template('jobpostinfo.html', jobs=jobs)

@app.route('/home')
def home():
    jobs = JobPosting.query.order_by(JobPosting.id.desc()).all() #change by date_time later
    return render_template('index1.html', jobs=jobs)

@app.route('/jobs_posted')
def jobs_posted():
    id = request.args.get('id')
    jobs = JobPosting.query.filter(JobPosting.id == id).all()
    return render_template('jobs_posted.html', jobs=jobs)


def getPercentage():
    last_job_posting = JobPosting.query.order_by(JobPosting.id.desc()).first()
    required_skills = last_job_posting.skill_required
    required_education = last_job_posting.education_required
    required_experience = last_job_posting.experience_required
    print(required_education)
    print(required_skills)
    print(required_experience)
    result = db.session.execute(text(
        'SELECT experience.id, education.degree, skill.name, experience.years FROM experience INNER JOIN skill ON experience.id = skill.id INNER JOIN education ON experience.id = education.id')).fetchall()

    percentage_list = []

    for row in result:
        id = row[0]
        degree = row[1]
        name = row[2]
        years = row[3]

        # Compare required education with degree per id
        req_educations = set(required_education.split(','))
        matched_educations = [edu.strip() for edu in req_educations if edu.strip() in degree]
        education_percentage = (len(matched_educations) / len(req_educations)) * 100

        # Compare required skills with name per id
        req_skills = set(required_skills.split(','))
        matched_skills = [skill.strip() for skill in req_skills if skill.strip() in name]
        skills_percentage = (len(matched_skills) / len(req_skills)) * 100

        # # Compare required experience with years per id
        # req_experiences = required_experience.split(',')
        # print(req_experiences)
        # matched_counter = 0
        # for req_exp in req_experiences:
        #     req_jobtitle, req_years = req_exp.split(':')
        #     req_years = req_years.replace(' years', '').replace(' year', '')
        #     years = years.replace(' years', '').replace('Years:', '').replace(' year', '').split(',')
        #     for year in years:
        #         nName, nYear = year.split(':')
        #         print(nName, nYear, req_jobtitle, req_years)
        #         if req_jobtitle.strip() == nName.strip() and int(nYear) >= int(req_years.strip()):
        #             matched_counter += 1
        #
        #     print("Done Loop.")
        #
        #     experience_percentage = (matched_counter / len(req_experiences)) * 100
        overall = (education_percentage + skills_percentage) / 2
        print(f"ID: {id}\nDegree: {degree}\nName: {name}\nYears: {years}\nEducation Percentage: {education_percentage}%\nSkills Percentage: {skills_percentage}%\nExperience Percentage: N/A\nOverall Percentage: {overall}%\n")

        percentage_list.append((id, round(education_percentage), round(skills_percentage), round(overall)))

    # Get the last job posting ID
    last_job_posting = JobPosting.query.order_by(JobPosting.id.desc()).first()
    last_job_posting_id = last_job_posting.id

    # # Convert percentage_list to JSON string
    sorted_list = sorted(percentage_list, key=lambda x: x[3], reverse=True)
    percentage_list_json = json.dumps(sorted_list)
    #
    # # Convert percentage_list_json back to a dictionary
    # percentage_list_dict = json.loads(percentage_list_json)

    # Get the row to update
    job_posting = db.session.query(JobPosting).filter_by(id=last_job_posting_id).one()

    # Update the recommended column
    job_posting.recommended = percentage_list_json

    # Commit the changes
    db.session.commit()
    # Checking the values of the column recommended
    # job_posting = JobPosting.query.get(last_job_posting.id)
    # print(job_posting.recommended)

    for row in percentage_list:
        id = row[0]
        education_percentage = row[1]
        skills_percentage = row[2]
        overall_percentage = row[3]
        print(
            f"ID: {id}\nEducation Percentage: {education_percentage}%\nSkills Percentage: {skills_percentage}%\nOverall Percentage: {overall_percentage}%\n")

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
