from data_model import DataModel

data_model = DataModel()

# Verificar conexión
print("Conectado a MongoDB Atlas correctamente.")

# Insertar un producto de prueba
producto = {
    "id_producto": "P100",
    "nombre_producto": "Producto de Prueba",
    "categoria": "Categoría A",
    "cantidad_disponible": 10,
    "precio_unitario": 5.00,
    "costo_unitario": 2.50,
    "ultima_actualizacion": "2025-02-07",
    "historico_movimientos": []
}

data_model.coleccion_inventario.insert_one(producto)
print("Producto insertado correctamente.")

# Ver productos
for prod in data_model.coleccion_inventario.find():
    print(prod)
