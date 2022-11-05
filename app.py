from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movies_ns = api.namespace("movies")
director_ns = api.namespace("director")
genre_ns = api.namespace("genre")


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    director_id = fields.Int()
    genre_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = MovieSchema()
directors_schema = MovieSchema(many=True)

genre_schema = MovieSchema()
genres_schema = MovieSchema(many=True)


@movies_ns.route("/")
class MoviesView(Resource):
    def get(self):
        all_movies = db.session.query(Movie)

        director_id = request.args.get("director_id")
        if director_id is not None:
            all_movies = all_movies.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            all_movies = all_movies.filter(Movie.genre == genre_id)

        return movies_schema.dump(all_movies), 200

    def post(self):
        request_json = request.json
        new_movie = Movie(**request_json)

        with db.session.begin():
            db.session.add(new_movie)

        return "New movie has been added", 201


@movies_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id):
        movie = Movie.query.get(id)
        return movie_schema.dump(movie), 200

    def put(self, id):
        updated_rows = db.session.query(Movie).filter(Movie.id == id).update(request.json)

        if not updated_rows:
            return "", 400

        return "", 204

    def delete(self, id):
        deleted_row = db.session.query(Movie).get(id)

        if not deleted_row:
            return "", 400

        db.session.delete(deleted_row)
        db.session.commit()

        return "", 204


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director)
        return directors_schema.dump(all_directors), 200

    def post(self):
        request_json = request.json
        new_director = Director(**request_json)

        with db.session.begin():
            db.session.add(new_director)

        return "", 201


@director_ns.route('/<int:id>')
class DirectorView(Resource):
    def get(self, id):
        director = Director.query.get(id)
        return director_schema.dump(director), 200

    def put(self, id):
        updated_rows = db.session.query(Movie).filter(Movie.id == id).update(request.json)

        if updated_rows != 1:
            return "", 400

        return "", 204

    def delete(self, id):
        deleted_row = db.session.query(Movie).get(id)

        if deleted_row != 1:
            return "", 400

        db.session.delete()
        db.session.commit()

        return "", 204


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre)
        return genres_schema.dump(all_genres), 200

    def post(self):
        request_json = request.json
        new_genre = Director(**request_json)

        with db.session.begin():
            db.session.add(new_genre)

        return "", 201


@genre_ns.route('/<int:id>')
class GenreView(Resource):
    def get(self, id):
        genre = Genre.query.get(id)
        return genre_schema.dump(genre), 200

    def put(self, id):
        updated_rows = db.session.query(Movie).filter(Movie.id == id).update(request.json)

        if updated_rows != 1:
            return "", 400

        return "", 204

    def delete(self, id):
        deleted_row = db.session.query(Movie).get(id)

        if deleted_row != 1:
            return "", 400

        db.session.delete()
        db.session.commit()

        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
