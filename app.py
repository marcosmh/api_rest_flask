from flask import Flask
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from PIL import Image
from werkzeug.utils import secure_filename

from flask_uploads import UploadSet, configure_uploads, IMAGES
from sqlalchemy import Null

app = Flask(__name__)
#CORS(app)  # Enable CORS for all origins
CORS(app, resources={
    r"/productos": {"origins": "http://localhost:4200"},
    r"/uploads/*": {"origins": "http://localhost:4200"}
})

# Configuración de la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:admindba@localhost/api_rest_php'
db = SQLAlchemy(app)

photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)



class Producto(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(255), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    precio      = db.Column(db.String(255))
    imagen      = db.Column(db.String(255))

    def __repr__(self):
        return '<Producto %r>' % self.nombre, self.descripcion, self.precio
    
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
    print("create_producto:")
    try:
        data = request.get_json()
    
        nuevo_producto = Producto(nombre=data['nombre'], descripcion=data['descripcion'], 
                                precio=data['precio'], imagen=data['imagen'] )
        db.session.add(nuevo_producto)
        db.session.commit()
        print("Producto guardado correctamente.","[OK]")
        return jsonify(nuevo_producto.json()), 201
    except Exception as e:
        json = jsonify({'error': str(e)})
        print("Error: ",json)
        return json, 400


# Actualizar un producto
@app.route('/productos/<int:id>', methods=['PUT'])
def update_producto(id):
    print("update_producto:")
    try:
        producto = Producto.query.get_or_404(id)
        data = request.get_json()
        producto.nombre = data['nombre']
        producto.descripcion = data['descripcion']
        producto.precio = data['precio']
        producto.imagen = id+"_"+data['imagen']
        db.session.commit()
        return jsonify(producto.json())
    except Exception as e:
        json = jsonify({'error': str(e)})
        print("Error: ",json)
        return json, 400


# Eliminar un producto
@app.route('/productos/<int:id>', methods=['DELETE'])
def delete_producto(id):
    print("delete_producto:")
    try:
        producto = Producto.query.get_or_404(id)
        db.session.delete(producto)
        db.session.commit()
        return jsonify({'message': 'Producto eliminado'})
    except Exception as e:
        json = jsonify({'error': str(e)})
        print("Error: ",json)
        return json, 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','txt'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<int:id>', methods=['POST'])
def upload_image(id):
    print("Upload imagen...", id)

    if request.method == 'POST':
        if 'uploads[]' not in request.files:
            return jsonify({'message': 'No hay parte de la imagen'}), 400

        file = request.files['uploads[]']

        if file.filename == '':
            return jsonify({'message': 'No hay ningún archivo seleccionado'}), 400

        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filename = str(id)+"_"+filename      
                photos.save(file, filename)
                nameImg = f'static/img/{filename}'

                # Guardar la ruta en la bd
                producto = Producto.query.get_or_404(id)
                producto.imagen = nameImg
                db.session.commit()

                # Crear la miniatura
                # img = Image.open(nameImg)
                # img.thumbnail((128, 128))
                # img.save(f'static/img/thumb_{filename}')
                
                return jsonify({'message': 'Se cargó la imagen y se creó la miniatura', 'filename': filename})
            except Exception as e:
                print(f"Error al cargar la imagen: {e}")
                return jsonify({'message': 'Se ha producido un error durante la carga de la imagen'}), 500

        return jsonify({'message': 'Archivo Invalido.'}), 400



if __name__ == '__main__':
    app.run(debug=True)

