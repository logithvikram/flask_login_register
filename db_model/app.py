from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:logi2002@localhost/flask_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Owner(db.Model):
    __tablename__ = 'owners'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    toys = db.relationship('Toy', backref='owner', lazy=True)

class Toy(db.Model):
    __tablename__ = 'toys'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)

class OwnersToys(db.Model):
    __tablename__ = 'owners_toys'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    toy_id = db.Column(db.Integer, db.ForeignKey('toys.id'), nullable=False)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/add_data')
def add_data():
    owner1 = Owner(name='logith')
    owner2 = Owner(name='naveen')
    toy1 = Toy(name='car', owner=owner1)
    toy2 = Toy(name='bike', owner=owner1)
    toy3 = Toy(name='Doll', owner=owner2)
    
    db.session.add(owner1)
    db.session.add(owner2)
    db.session.add(toy1)
    db.session.add(toy2)
    db.session.add(toy3)
    db.session.commit()
    
    return 'Data added!'

@app.route('/owners')
def get_owners():
    owners = Owner.query.all()
    return {owner.id: owner.name for owner in owners}

@app.route('/toys')
def get_toys():
    toys = Toy.query.all()
    return {
            toy.id: 
             {
                 'name': toy.name, 
                 'owner': toy.owner.name
             } 
             for toy in toys
            }

@app.route('/owners/<int:owner_id>/toys')
def get_owner_toys(owner_id):
    owner = Owner.query.get(owner_id)
    if not owner:
        return 'Owner not found', 404
    return {
        toy.id: 
            toy.name for toy in owner.toys
        }

if __name__ == '__main__':
    app.run(debug=True)
