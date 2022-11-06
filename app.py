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
director_ns = api.namespace("directors")
genre_ns = api.namespace("genres")


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
            all_movies = all_movies.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)

        return "New movie has been added", 201


@movies_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id):
        movie = Movie.query.get(id)
        return movie_schema.dump(movie), 200

    def put(self, id):
        updated_movie = db.session.query(Movie).filter(Movie.id == id).update(request.json)
        db.session.commit()

        if not updated_movie:
            return "Error. Movie data not updated", 400

        return "Movie data updated successfully.", 204

    def delete(self, id):
        deleted_row = db.session.query(Movie).get(id)

        if not deleted_row:
            return "Error. The movie data has not been deleted.", 400

        db.session.delete(deleted_row)
        db.session.commit()

        return "Movie data deleted.", 204


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

        return "New director successfully added.", 201


@director_ns.route('/<int:id>')
class DirectorView(Resource):
    def get(self, id):
        director = Director.query.get(id)
        return director_schema.dump(director), 200

    def put(self, id):
        updated_director = db.session.query(Director).filter(Director.id == id).update(request.json)
        db.session.commit()

        if not updated_director:
            return "Error. Director not updated.", 400

        return "Director updated successfully.", 204

    def delete(self, id):
        deleted_director = db.session.query(Director).get(id)

        if not deleted_director:
            return "Error. The director's data has not been deleted", 400

        db.session.delete(deleted_director)
        db.session.commit()

        return "The director's data has been successfully deleted.", 204


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre)
        return genres_schema.dump(all_genres), 200

    def post(self):
        request_json = request.json
        new_genre = Genre(**request_json)

        with db.session.begin():
            db.session.add(new_genre)

        return "New genre successfully added.", 201


@genre_ns.route('/<int:id>')
class GenreView(Resource):
    def get(self, id):
        genre = Genre.query.get(id)
        return genre_schema.dump(genre), 200

    def put(self, id):
        updated_genre = db.session.query(Genre).filter(Genre.id == id).update(request.json)
        db.session.commit()

        if not updated_genre:
            return "Error. Genre not updated.", 400

        return "Genre updated successfully", 204

    def delete(self, id):
        deleted_genre = db.session.query(Genre).get(id)

        if not deleted_genre:
            return "Error. Genre not deleted.", 400

        db.session.delete(deleted_genre)
        db.session.commit()

        return "Genre deleted successfully", 204


if __name__ == '__main__':
    app.run(debug=True)
