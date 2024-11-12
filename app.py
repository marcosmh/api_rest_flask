from flask import Flask
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:admindba@localhost/api_rest_php'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Producto(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(255), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    precio      = db.Column(db.String(255))
    imagen      = db.Column(db.String(255))

    def __repr__(self):
        return '<Producto %r>' % self.nombre
    
    def json(self):
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion, 
                    'precio': self.precio, 'imagen': self.imagen }
    


# Obtener todos los productos
@app.route('/productos', methods=['GET'])
def get_all_productos():
    productos = Producto.query.all()
    return jsonify([pr.json() for pr in productos])


@app.route('/productos/<int:id>', methods=['GET'])
def get_producto(id):
    producto = Producto.query.get_or_404(id)
    return jsonify(producto.json())

# Crear un nuevo producto
@app.route('/productos', methods=['POST'])
def create_producto():
    data = request.get_json()
    nuevo_producto = Producto(nombre=data['nombre'], descripcion=data['descripcion'], 
                              precio=data['precio'], imagen=data['imagen'] )
    db.session.add(nuevo_producto)
    db.session.commit()
    return jsonify(nuevo_producto.json()), 201

# Actualizar un producto
@app.route('/productos/<int:id>', methods=['PUT'])
def update_producto(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json()
    producto.nombre = data['nombre']
    producto.descripcion = data['descripcion']
    producto.precio = data['precio']
    producto.imagen = data['imagen']
    db.session.commit()
    return jsonify(producto.json())

# Eliminar un producto
@app.route('/productos/<int:id>', methods=['DELETE'])
def delete_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return jsonify({'message': 'Producto eliminado'})

if __name__ == '__main__':
    app.run(debug=True)

