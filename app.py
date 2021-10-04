from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import csv
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Show(db.Model):
    __tablename__ = 'shows'
    __description__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    rating = db.Column(db.String(120))
    rating_level = db.Column(db.String(80))
    rating_description = db.Column(db.String(320))
    release_year = db.Column(db.Integer)
    user_rating_score = db.Column(db.Integer)
    user_rating_size = db.Column(db.Integer)

    def __init__(self,
            title,
            rating,
            rating_level,
            rating_description,
            release_year,
            user_rating_score,
            user_rating_size):

            self.title = title
            self.rating = rating
            self.rating_level = rating_level
            self.rating_description = rating_description
            self.release_year = release_year
            self.user_rating_score = user_rating_score
            self.user_rating_size = user_rating_size

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

db.create_all()
db.session.commit()

with open("netflix.csv") as csvfile:
    reader = csv.reader(csvfile)
    first = False
    for row in reader:
        if not first:
            first = True
            continue
        data = {
            'title':row[0],
            'rating':row[1],
            'rating_level':row[2],
            'rating_description':row[3],
            'release_year':row[4],
            'user_rating_score':row[5],
            'user_rating_size':row[6]}
        #print(data)
        #print(Show(**data))
        #record = Show(**data)
        record = Show(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6])
        db.session.add(record)
    db.session.commit()

ROWS_PER_PAGE = 15

@app.route('/show', methods = ['GET', 'POST'])
def get_show():
    if request.method == 'GET':
        filter = request.args.get('filter', default = '', type = str)
        page = request.args.get('page', default = 1, type = int)
        sort = request.args.get('sort', default = 'desc', type = str)
        if sort == 'desc':
            filtered = Show.query.filter(Show.title.like(f"%{filter}%")).order_by(Show.title.desc()).paginate(page = page, per_page = ROWS_PER_PAGE)
        else:
            filtered = Show.query.filter(Show.title.like(f"%{filter}%")).order_by(Show.title.asc()).paginate(page = page, per_page = ROWS_PER_PAGE)
        return json.dumps([show.as_dict() for show in filtered.items])
    if request.method == 'POST':
        id = request.json['id']
        show = Show.query.get_or_404(id)
        show = Show(**request.json)
        db.session.add(show)
        db.session.commit()

if '__name__' == '__main__':
    app.run(host='0.0.0.0', debug=True)
