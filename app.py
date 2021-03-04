from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
import random

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

# TODO - Move to config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/data.sqlite'

db = SQLAlchemy(app)


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    password = db.Column(db.String(64))

    def to_json(self):
        return {
            "ID": int(self.id),
            "Name": self.name,
            "password": self.password
        }

    def __repr__(self):
        return '<User %r>' % self.name


class Notes(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer)
    noteID = db.Column(db.Integer, primary_key=True)
    noteTitle = db.Column(db.String(64))
    notes = db.Column(db.String(200))

    def __repr__(self):
        return '<User %r>' % self.name


class AddUser(Resource):
    def post(self):
        name_param = request.form['name']
        password_param = request.form['password']
        userCheck = User.query.filter_by(name=name_param).first()
        if userCheck is None:
            randID = random.randint(50, 200)
            new_user = User(id=randID, name=name_param, password=password_param)
            db.session.add(new_user)
            db.session.commit()
            return make_response({'ID': randID}, 201)
        else:
            if userCheck.password == password_param:
                return make_response("Login successful")
            else:
                return make_response("Login Incorrect")

    def get(self):
        records = [z.to_json() for z in User.query]
        return str(records)


class UserID(Resource):
    def delete(self, user_id):
        passwordTest = request.form['password']
        user = User.query.filter_by(id=user_id, password=passwordTest).first()

        if user is not None:
            db.session.delete(user)
            db.session.commit()
            return make_response("deleted", 202)
        else:
            return make_response("User not found or password incorrect", 404)


class NoteRetrieve(Resource):
    def post(self, user_id):
        password_param = request.form['password']
        user = User.query.filter_by(id=user_id, password=password_param).first()
        if user is None:
            return make_response("No notes found for that user or password incorrect", 404)
        else:
            note = Notes.query.filter_by(id=user_id).first()
            return {'NoteID': note.noteID, 'Notes': note.notes}


class NoteID(Resource):
    def post(self, user_id, note_id):
        #check if password is correct
        password_param = request.form['password']
        user = User.query.filter_by(id=user_id, password=password_param).first()
        if user is None:
            return make_response("ID or password incorrect", 404)
        #check if ID or title
        if note_id.isdigit():
            note = Notes.query.filter_by(id=user_id, noteID=note_id).first()
            return{'Notes': note.notes}
        else:
            note = Notes.query.filter_by(noteTitle=note_id, id=user_id).first()
            #if no note with title, add it
            if note is None:
                randNoteID = random.randint(1, 50)
                notes_param = request.form['notes']
                new_note = Notes(id=user_id, noteID=randNoteID, noteTitle=note_id,
                                notes=notes_param)
                db.session.add(new_note)
                db.session.commit()
                return make_response({'Note added with ID': randNoteID}, 201)
            return {'Notes': note.notes}

    def put(self, user_id, note_id):
        passwordTest = request.form['password']
        user = User.query.filter_by(id=user_id, password=passwordTest).first()
        if user is None:
            return make_response("Invalid User or password", 401)

        if note_id.isdigit():
            note = Notes.query.filter_by(id=user_id, noteID=note_id).first()
        else:
            note = Notes.query.filter_by(id=user_id, noteTitle=note_id).first()
        if note is not None:
            note.notes = request.form['notes']
            db.session.add(note)
            db.session.commit()
            return make_response({'id': note.id, 'noteID': note.noteID, 'noteTitle': note.noteTitle,
                                  'Notes': note.notes}, 201)
        else:
            return make_response("no user matching that id", 404)


    def delete(self,user_id, note_id):
        passwordTest = request.form['password']
        user = User.query.filter_by(id=user_id, password=passwordTest).first()

        if user is not None:
            note = Notes.query.filter_by(id=user_id, noteID=note_id).first()
            db.session.delete(note)
            db.session.commit()
            return make_response("deleted", 202)
        else:
            return make_response("User not found or password incorrect", 404)

api.add_resource(AddUser, '/user/')
api.add_resource(UserID, '/user/<string:user_id>')
api.add_resource(NoteRetrieve, '/user/<string:user_id>/notes')
api.add_resource(NoteID, '/user/<string:user_id>/notes/<string:note_id>')
#db.create_all()


if __name__ == '__main__':
    app.run()
