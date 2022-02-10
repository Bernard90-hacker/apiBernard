import os
from select import select
from urllib.parse import quote_plus
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from dotenv import load_dotenv
load_dotenv() #Permet de charger toutes les variables d'environnement
#On ne peut pas avoir plus de trois éléments dans la norme d'écriture des routes


app = Flask(__name__) #Démarrrer l'application
motdepasse=quote_plus(os.getenv('password'))
hostname=os.getenv('host')
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:{}@{}:5432/db_api".format(motdepasse, hostname) #Fournir une chaine de connexion a la BD
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #Eviter les avertissements.

db = SQLAlchemy(app) #Creé une instance de la BD

class Etudiant(db.Model):
    __tablename__='etudiants'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    adresse = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(200), unique=True)
    
    def __init__(self, nom, adresse, email) :
        self.nom = nom
        self.adresse = adresse
        self.email = email
        
    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def format(self):
        return{
            'id'     :self.id,
            'nom'    : self.nom,
            'adresse': self.adresse,
            'email'  : self.email
        }
db.create_all()

@app.route('/etudiants', methods=['GET'])
def get_all_students():
    etudiants = Etudiant.query.all()
    formated_students = [etudiant.format() for etudiant in etudiants]
    return jsonify({
        'success': True,
        'etudiants' : formated_students,
        'Total' : len(formated_students) # or Etudiant.query.count()
    })#Le jsonify doit retourner un dictionnaire.
    #Pour changer le debug mode il faut taper set FLASK_DEBUG = On, or True or 1 ceux-ci étant les différentes valeurs
@app.route('/etudiants', methods=['POST'])
def add_student():
    try :
        body=request.get_json()
        new_nom = body.get('nom', None) #Si aucune valeur fournie alors prend la valeur nulle.
        new_email=body.get('email', None)
        new_adresse=body.get('adresse', None)
        etudiant = Etudiant(nom=new_nom, adresse=new_adresse, email=new_email)
        etudiant.insert()
        etudiants = Etudiant.query.all()
        etudiants_formated = [etu.format() for etu in etudiants]
        
        return jsonify({
            'created_id': etudiant.id,
            'success'   : True,
            'total'     : len(Etudiant.query.all()),
            'etudiants' : etudiants_formated      
        })
    except :
        abort(400) #bad request

@app.route('/etudiants/<int:id>', methods=['GET'])
def get_one_student(id):
    etudiant = Etudiant.query.get(id) #ou etudiant = Etudiant.query.filter(Etudiant.id==id).first()
    if etudiant is None:
            abort(404) #erreur de type not found
    else :
        return jsonify({
                'success' : True,
                'select_id' : id,
                'select_student' : etudiant.format()
                    
        })
        
@app.route('/etudiants/<int:id>', methods=['DELETE'])
def delete_student(id):
    etudiant = Etudiant.query.get(id)
    if etudiant is None:
        abort(404)
    else:
        etudiant.delete()
        return jsonify({
            "deleted_id"      :  id,
            "success"         : True,
            "Total"           : Etudiant.query.count(),
            "deleted_student" : etudiant.format()
        })
        
@app.route('/etudiants/<int:id>', methods=['PATCH'])
def update_student(id):
    body = request.get_json() #get data from json
    etudiant = Etudiant.query.get(id) #get student from database
    etudiant.nom = body.get('nom', None) #populate student
    etudiant.adresse = body.get('adresse', None)
    etudiant.email = body.get('email', None)
    
    if  etudiant.nom is None or etudiant.adresse is None or etudiant.email is None :
        abort(400)
    
    etudiant.update()
    return jsonify({
        "success"            :  True,
        "updated_id_student" : id,
        "new_student"        : etudiant.format()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success'  :  False,
        'error'    : 404,
        'message'  : 'Not found',
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success'  : False,
        'error'    : 400,
        'Message'  : 'Bad request'
    }), 400
    