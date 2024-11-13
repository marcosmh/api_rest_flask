from flask import Flask
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy

"""
from flask_uploads import UploadSet, configure_uploads, IMAGES
from PIL import Image
"""

app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:admindba@localhost/api_rest_php'
db = SQLAlchemy(app)

"""
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
"""



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
    nuevo_producto = Producto(id=data['id'],nombre=data['nombre'], descripcion=data['descripcion'], 
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


"""
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'message': 'No image part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = photos.save(file)

        # Crear la miniatura
        img = Image.open(f'static/img/{filename}')
        img.thumbnail((128, 128))
        img.save(f'static/img/thumb_{filename}')
        return jsonify({'message': 'Image uploaded and thumbnail created', 'filename': filename})
    return jsonify({'message': 'Invalid file'}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
"""


if __name__ == '__main__':
    app.run(debug=True)

