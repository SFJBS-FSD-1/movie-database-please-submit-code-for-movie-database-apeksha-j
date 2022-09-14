from flask import Flask, request, jsonify, Response, render_template
from flask_restful import Api,Resource
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
import os
from flask_migrate import Migrate

class Config:
    SQLALCHEMY_DATABASE_URI= 'postgresql+psycopg2://root:1234@localhost/moviedatabase2'

class Development_Config(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://root:1234@localhost/moviedatabase2'

class Production_Config(Config):
    uri = os.environ.get("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri=uri.replace("postgres://","postgresql://",1)
    SQLALCHEMY_DATABASE_URI = uri

env = os.environ.get("ENV","Development")

if env=="Production":
    config_str= Production_Config
else:
    config_str= Development_Config

app = Flask(__name__)

app.config.from_object(config_str)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:welcome$1234@localhost/Moviedb'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://root:1234@localhost/moviedatabase2'

db = SQLAlchemy(app)
api=Api(app)
migrate = Migrate(app,db)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # this is the primary key
    title = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(80), nullable=False)

    @staticmethod
    def add_movie(title,year,genre):
        new_movie = Movie(title=title, year=year, genre=genre)
        db.session.add(new_movie)
        db.session.commit()

    @staticmethod
    def get_movies():
        data=Movie.query.all()
        return data

    @staticmethod
    def get_one_movie(id):
        data = Movie.query.filter_by(id = id).first()
        return data

    @staticmethod
    def delete_movie(id):
        data = Movie.query.filter_by(id=id).delete()
        db.session.commit()
        return data

    @staticmethod
    def put_movie(id,title,year,genre):
        data = Movie.query.filter_by(id=id).first()
        data.title=title
        data.year = year
        data.genre = genre
        db.session.commit()

@app.route("/")
def home():
    if request.method=="GET":
        return render_template("moviehomepage.html")

class AllMovies(Resource):
    def post(self):
        data=request.get_json()
        print(data)
        Movie.add_movie(title=data["title"],year=data["year"],genre=data["genre"])
        return ""

    def get(self):
        data=Movie.get_movies()
        movielist=[]
        for movie in data:
            moviedict={'title':movie.title,'year':movie.year,'genre':movie.genre}
            movielist.append(moviedict)
        return jsonify(movielist)

class AllMovies_getbyID(Resource):
    def get(self,movie_id):
# FILTER_BY METHOD
        dictt={}
        data=Movie.get_one_movie(movie_id)
        if data:
            dictt["id"]=data.id
            dictt["title"] = data.title
            dictt["year"] = data.year
            dictt["genre"] = data.genre
            return jsonify((dictt),{'status':HTTPStatus.OK})
        else:
            return jsonify({"message": "ID Not Found","status": HTTPStatus.NOT_FOUND})

# FOR LOOP METHOD
#         data=Movie.get_movies()
#         for movie in data:
#             dict={}
#             if movie.id == movie_id:
#                 dict['title']=movie.title
#                 dict['year'] = movie.year
#                 dict['genre'] = movie.genre
#                 return jsonify(dict)
#         else:
#             return jsonify({"message":"ID Not Found"})

    def delete(self,movie_id):
        data = Movie.delete_movie(movie_id)
        if data:
            return jsonify(data)

    def put(self,movie_id):
        data= request.get_json()
        Movie.put_movie(movie_id,data["title"],data["year"],data["genre"])
        if data:
            return jsonify({"message":"Updated successfully"})
        else:
            return jsonify({"message":"ID Not Found"})

api.add_resource(AllMovies,"/movies")
api.add_resource(AllMovies_getbyID,"/movies/<int:movie_id>")
if __name__=="__main__":
    app.run(port=5001)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)

# class Profile(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)

# COMMANDS FOR PYTHON CONSOLE TO ADD ENTRY
# from sql_alchemy_test import db
# from sql_alchemy_test import Profile
# admin = Profile(username='admin',email='admin@example.com')
# db.session.add(admin)
# db.session.commit()