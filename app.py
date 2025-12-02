import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import os
import re
import traceback

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tu-clave-secreta-super-segura-cambiar-en-produccion')

# Configuración de MySQL
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'admin')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'licoreria')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para requerir rol de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        if session.get('rol_id') != 1:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def utility_processor():
    return {
        'now': datetime.now,
        'current_year': lambda: datetime.now().year
    }

# Ruta principal - redirige según el rol
@app.route('/')
@login_required
def index():
    if session.get('rol_id') == 1:  # Administrador
        return redirect(url_for('dashboard'))
    else:  # Vendedor
        return redirect(url_for('ventas'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está autenticado, redirigir al índice
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validación básica
        if not username or not password:
            flash('Por favor ingrese usuario y contraseña', 'danger')
            return render_template('login.html')
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT u.ID_Usuario, u.NombreUsuario, u.ContrasenaHash, 
                       u.Rol_ID, r.Nombre_Rol
                FROM Usuarios u
                INNER JOIN Roles r ON u.Rol_ID = r.ID_Rol
                WHERE u.NombreUsuario = %s AND u.Estado = 1
            """, (username,))
            user = cur.fetchone()
            cur.close()
            
            if user and check_password_hash(user['ContrasenaHash'], password):
                session['user_id'] = user['ID_Usuario']
                session['username'] = user['NombreUsuario']
                session['rol_id'] = user['Rol_ID']
                session['rol_nombre'] = user['Nombre_Rol']
                flash(f'Bienvenido {username}', 'success')
                return redirect(url_for('index'))
            else:
                # Log del intento fallido (opcional)
                flash('Usuario o contraseña incorrectos', 'danger')
                
        except Exception as e:
            flash('Error en el sistema, por favor intente más tarde', 'danger')
            # Log del error real para administradores
    
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@admin_required
def dashboard():
    cur = mysql.connection.cursor()
    
    # Obtener estadísticas
    # Total de ventas del día
    cur.execute("""
        SELECT COALESCE(SUM(Total), 0) as total_dia
        FROM Facturacion
        WHERE DATE(Fecha) = CURDATE() AND Estado = 1
    """)
    ventas_dia_result = cur.fetchone()
    ventas_dia = float(ventas_dia_result['total_dia']) if ventas_dia_result['total_dia'] else 0.0
    
    # Total de ventas del mes
    cur.execute("""
        SELECT COALESCE(SUM(Total), 0) as total_mes
        FROM Facturacion
        WHERE MONTH(Fecha) = MONTH(CURDATE()) 
        AND YEAR(Fecha) = YEAR(CURDATE()) 
        AND Estado = 1
    """)
    ventas_mes_result = cur.fetchone()
    ventas_mes = float(ventas_mes_result['total_mes']) if ventas_mes_result['total_mes'] else 0.0
    
    # Productos con stock bajo - CONVERSIÓN SEGURA
    cur.execute("""
        SELECT p.ID_Producto, p.Descripcion, 
               COALESCE(SUM(ib.Existencias), 0) as Existencias, 
               p.Stock_Minimo
        FROM Productos p
        LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto
        WHERE p.Estado = 'activo'
        GROUP BY p.ID_Producto, p.Descripcion, p.Stock_Minimo
        HAVING COALESCE(SUM(ib.Existencias), 0) <= p.Stock_Minimo
        ORDER BY Existencias ASC
        LIMIT 10
    """)
    productos_bajo_stock_raw = cur.fetchall()
    
    # Procesar productos con stock bajo
    productos_bajo_stock = []
    for producto in productos_bajo_stock_raw:
        # Convertir a float para evitar problemas con Decimal
        existencias = int(producto['Existencias']) if producto['Existencias'] else 0.0
        stock_minimo = int(producto['Stock_Minimo']) if producto['Stock_Minimo'] else 0.0
        
        # Solo incluir si realmente está bajo stock
        if existencias <= stock_minimo:
            producto_dict = {
                'ID_Producto': producto['ID_Producto'],
                'Descripcion': producto['Descripcion'],
                'Existencias': existencias,
                'Stock_Minimo': stock_minimo,
                'existencias_display': producto['Existencias'],  # Mantener formato original para display
                'stock_minimo_display': producto['Stock_Minimo']  # Mantener formato original para display
            }
            
            # Determinar estado
            if existencias == 0:
                producto_dict['estado'] = 'agotado'
                producto_dict['estado_badge'] = 'bg-danger'
                producto_dict['estado_texto'] = 'Agotado'
            elif existencias <= stock_minimo * 0.5:
                producto_dict['estado'] = 'critico'
                producto_dict['estado_badge'] = 'bg-warning'
                producto_dict['estado_texto'] = 'Crítico'
            else:
                producto_dict['estado'] = 'bajo'
                producto_dict['estado_badge'] = 'bg-info'
                producto_dict['estado_texto'] = 'Bajo'
            
            productos_bajo_stock.append(producto_dict)
    
    # Total de productos
    cur.execute("SELECT COUNT(*) as total FROM Productos WHERE Estado = 1")
    total_productos = cur.fetchone()['total']
    
    # Ventas de los últimos 7 días - CONVERSIÓN SEGURA
    cur.execute("""
        SELECT DATE(Fecha) as fecha, COALESCE(SUM(Total), 0) as total
        FROM Facturacion
        WHERE Fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND Estado = 1
        GROUP BY DATE(Fecha)
        ORDER BY fecha ASC
    """)
    ventas_semana_raw = cur.fetchall()
    
    # Convertir ventas a float para el gráfico
    ventas_semana = []
    for venta in ventas_semana_raw:
        ventas_semana.append({
            'fecha': venta['fecha'],
            'total': float(venta['total']) if venta['total'] else 0.0,
            'total_display': venta['total']  # Mantener para display si es necesario
        })
    
    # Productos más vendidos
    cur.execute("""
        SELECT p.Descripcion, SUM(df.Cantidad) as total_vendido
        FROM Detalle_Facturacion df
        INNER JOIN Productos p ON df.ID_Producto = p.ID_Producto
        INNER JOIN Facturacion f ON df.ID_Factura = f.ID_Factura
        WHERE f.Fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND f.Estado = 1
        GROUP BY p.ID_Producto, p.Descripcion
        ORDER BY total_vendido DESC
        LIMIT 5
    """)
    productos_mas_vendidos = cur.fetchall()
    
    # Función para obtener la fecha actual
    def now():
        return datetime.now()
    
    cur.close()
    
    return render_template('dashboard.html',
                         ventas_dia=ventas_dia,
                         ventas_mes=ventas_mes,
                         productos_bajo_stock=productos_bajo_stock,
                         total_productos=total_productos,
                         ventas_semana=ventas_semana,
                         productos_mas_vendidos=productos_mas_vendidos,
                         now=now)

# Usuarios
@app.route('/usuarios')
@admin_required
def usuarios():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.ID_Usuario, u.NombreUsuario, r.Nombre_Rol, u.Estado, u.Fecha_Creacion, u.Rol_ID
        FROM Usuarios u
        INNER JOIN Roles r ON u.Rol_ID = r.ID_Rol
        ORDER BY u.NombreUsuario
    """)
    usuarios = cur.fetchall()
    cur.close()
    
    return render_template('usuarios/lista.html', usuarios=usuarios)

# Mostrar formulario para crear usuario
@app.route('/usuarios/crear', methods=['GET'])
@admin_required
def crear_usuario():
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT ID_Rol, Nombre_Rol FROM Roles")
    roles = cur.fetchall()
    cur.close()
    
    return render_template('usuarios/formulario.html', usuario=None, roles=roles)


# Procesar creación de usuario
@app.route('/usuarios/crear', methods=['POST'])
@admin_required
def crear_usuario_post():
    
    nombre_usuario = request.form['nombre_usuario']
    contrasena = request.form['contrasena']
    confirmar_contrasena = request.form['confirmar_contrasena']
    rol_id = request.form['rol_id']
    estado = request.form.get('estado', 1)
    
    # Validaciones
    if not nombre_usuario or not contrasena or not rol_id:
        flash('Todos los campos obligatorios deben ser completados', 'error')
        return redirect(url_for('crear_usuario'))
    
    if contrasena != confirmar_contrasena:
        flash('Las contraseñas no coinciden', 'error')
        return redirect(url_for('crear_usuario'))
    
    if len(contrasena) < 6:
        flash('La contraseña debe tener al menos 6 caracteres', 'error')
        return redirect(url_for('crear_usuario'))
    
    # Generar hash de la contraseña
    contrasena_hash = generate_password_hash(contrasena)
    
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO Usuarios (NombreUsuario, ContrasenaHash, Rol_ID, Estado)
            VALUES (%s, %s, %s, %s)
        """, (nombre_usuario, contrasena_hash, rol_id, estado))
        
        mysql.connection.commit()
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('usuarios'))
        
    except MySQLdb.IntegrityError:
        flash('El nombre de usuario ya existe', 'error')
        return redirect(url_for('crear_usuario'))
    except Exception as e:
        flash(f'Error al crear usuario: {str(e)}', 'error')
        return redirect(url_for('crear_usuario'))
    finally:
        cur.close()

# Mostrar formulario para editar usuario
@app.route('/usuarios/editar/<int:id>', methods=['GET'])
@admin_required
def editar_usuario(id):
    cur = mysql.connection.cursor()
    
    # Obtener datos del usuario
    cur.execute("""
        SELECT u.ID_Usuario, u.NombreUsuario, u.Rol_ID, u.Estado, u.Fecha_Creacion, r.Nombre_Rol
        FROM Usuarios u
        INNER JOIN Roles r ON u.Rol_ID = r.ID_Rol
        WHERE u.ID_Usuario = %s
    """, (id,))
    
    usuario = cur.fetchone()
    
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('usuarios'))
    
    # Obtener roles
    cur.execute("SELECT ID_Rol, Nombre_Rol FROM Roles")
    roles = cur.fetchall()
    cur.close()
    
    return render_template('usuarios/formulario.html', usuario=usuario, roles=roles)

# Procesar edición de usuario
@app.route('/usuarios/editar/<int:id>', methods=['POST'])
@admin_required
def editar_usuario_post(id):
    nombre_usuario = request.form['nombre_usuario']
    rol_id = request.form['rol_id']
    estado = request.form.get('estado', 0)
    contrasena = request.form.get('contrasena')
    confirmar_contrasena = request.form.get('confirmar_contrasena')
    
    # Validar contraseñas si se proporcionan
    if contrasena:
        if contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('editar_usuario', id=id))
        
        if len(contrasena) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return redirect(url_for('editar_usuario', id=id))
    
    cur = mysql.connection.cursor()
    try:
        if contrasena:  # Si se proporciona nueva contraseña
            contrasena_hash = generate_password_hash(contrasena)
            cur.execute("""
                UPDATE Usuarios 
                SET NombreUsuario = %s, Rol_ID = %s, Estado = %s, ContrasenaHash = %s
                WHERE ID_Usuario = %s
            """, (nombre_usuario, rol_id, estado, contrasena_hash, id))
        else:  # No cambiar contraseña
            cur.execute("""
                UPDATE Usuarios 
                SET NombreUsuario = %s, Rol_ID = %s, Estado = %s
                WHERE ID_Usuario = %s
            """, (nombre_usuario, rol_id, estado, id))
        
        mysql.connection.commit()
        flash('Usuario actualizado exitosamente', 'success')
        return redirect(url_for('usuarios'))
        
    except MySQLdb.IntegrityError:
        flash('El nombre de usuario ya existe', 'error')
        return redirect(url_for('editar_usuario', id=id))
    except Exception as e:
        flash(f'Error al actualizar usuario: {str(e)}', 'error')
        return redirect(url_for('editar_usuario', id=id))
    finally:
        cur.close()

# Eliminar usuario (soft delete)
@app.route('/usuarios/eliminar/<int:id>')
@admin_required
def eliminar_usuario(id):
    cur = mysql.connection.cursor()
    try:
        # Soft delete - cambiar estado a 0 (inactivo)
        cur.execute("UPDATE Usuarios SET Estado = 0 WHERE ID_Usuario = %s", (id,))
        mysql.connection.commit()
        flash('Usuario desactivado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al desactivar usuario: {str(e)}', 'error')
    finally:
        cur.close()
    return redirect(url_for('usuarios'))

@app.route('/usuarios/activar/<int:id>')
@admin_required
def activar_usuario(id):
    cur = mysql.connection.cursor()
    try:
        # Cambiar estado a 1 (activo)
        cur.execute("UPDATE Usuarios SET Estado = 1 WHERE ID_Usuario = %s", (id,))
        mysql.connection.commit()
        flash('Usuario activado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al activar usuario: {str(e)}', 'error')
    finally:
        cur.close()
    return redirect(url_for('usuarios'))

# Productos
@app.route('/productos')
@admin_required
def productos():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.ID_Producto,
               p.Descripcion,
               p.Unidad_Medida,
               p.Estado,
               p.Costo_Promedio,
               p.Precio_Venta,
               p.Categoria_ID,
               p.Fecha_Creacion,
               p.Usuario_Creador,
               p.Stock_Minimo,  -- Asegurar que traemos este campo
               c.Descripcion as Categoria,  
               u.Descripcion as Unidad,     
               u.Abreviatura,
               COALESCE(SUM(ib.Existencias), 0) as Existencias_Totales
        FROM productos p                
        LEFT JOIN categorias c ON p.Categoria_ID = c.ID_Categoria  
        LEFT JOIN unidades_medida u ON p.Unidad_Medida = u.ID_Unidad  
        LEFT JOIN inventario_bodega ib ON p.ID_Producto = ib.ID_Producto 
        WHERE p.Estado = 'activo'
        GROUP BY p.ID_Producto, p.Descripcion, p.Unidad_Medida, p.Estado,
                 p.Costo_Promedio, p.Precio_Venta, p.Categoria_ID, p.Fecha_Creacion,
                 p.Usuario_Creador, p.Stock_Minimo, c.Descripcion, u.Descripcion, u.Abreviatura
        ORDER BY p.Descripcion
    """)
    productos = cur.fetchall()
    cur.close()
    
    # DEBUG: Verificar la estructura de los datos
    if productos:
        print(f"Primer producto: {productos[0]}")
        print(f"Claves disponibles: {productos[0].keys()}")
    
    return render_template('productos/lista.html', productos=productos)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@admin_required
def producto_nuevo():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            descripcion = request.form['descripcion'].strip()
            unidad_medida = request.form['unidad_medida']
            precio_venta = request.form['precio_venta']
            costo_promedio = request.form.get('costo_promedio', 0)
            categoria_id = request.form['categoria_id']
            stock_minimo = request.form.get('stock_minimo', 5)
            existencias_iniciales = request.form.get('existencias_iniciales', 0)
            
            # Validación 1: Campos obligatorios
            campos_obligatorios = ['descripcion', 'unidad_medida', 'precio_venta', 'categoria_id']
            faltantes = [campo for campo in campos_obligatorios if not request.form.get(campo)]
            if faltantes:
                flash(f'Por favor complete los siguientes campos: {", ".join(faltantes)}', 'error')
                return redirect(url_for('producto_nuevo'))
            
            # Validación 2: Descripción no vacía después de trim
            if not descripcion:
                flash('La descripción no puede estar vacía', 'error')
                return redirect(url_for('producto_nuevo'))
            
            # Validación 3: Longitud máxima
            if len(descripcion) > 100:
                flash('La descripción no puede tener más de 100 caracteres', 'error')
                return redirect(url_for('producto_nuevo'))
            
            cur = mysql.connection.cursor()
            
            # Validación 4: Producto duplicado (misma descripción)
            cur.execute("""
                SELECT ID_Producto FROM Productos 
                WHERE LOWER(TRIM(Descripcion)) = LOWER(%s)
            """, (descripcion,))
            
            producto_existente = cur.fetchone()
            if producto_existente:
                flash('Ya existe un producto con esa descripción', 'error')
                cur.close()
                return redirect(url_for('producto_nuevo'))
            
            # Validación 5: Formato numérico
            try:
                precio_venta = float(precio_venta)
                costo_promedio = float(costo_promedio) if costo_promedio else 0
                stock_minimo = int(stock_minimo)
                existencias_iniciales = int(existencias_iniciales) if existencias_iniciales else 0
            except ValueError:
                flash('Los valores numéricos deben ser números válidos', 'error')
                cur.close()
                return redirect(url_for('producto_nuevo'))
            
            # Validación 6: Valores negativos
            if precio_venta < 0:
                flash('El precio de venta no puede ser negativo', 'error')
                cur.close()
                return redirect(url_for('producto_nuevo'))
            
            if costo_promedio < 0:
                flash('El costo promedio no puede ser negativo', 'error')
                cur.close()
                return redirect(url_for('producto_nuevo'))
            
            if stock_minimo < 0:
                flash('El stock mínimo no puede ser negativo', 'error')
                cur.close()
                return redirect(url_for('producto_nuevo'))
            
            if existencias_iniciales < 0:
                flash('Las existencias iniciales no pueden ser negativas', 'error')
                cur.close()
                return redirect(url_for('producto_nuevo'))
            
            # Validación 7: Precio mayor a costo (opcional pero recomendado)
            if precio_venta <= costo_promedio:
                flash('Advertencia: El precio de venta es menor o igual al costo', 'warning')
                # No redirigimos, solo mostramos advertencia
            
            # Validación 8: Existencia en catálogo de unidad de medida
            cur.execute("SELECT ID_Unidad FROM Unidades_Medida WHERE ID_Unidad = %s", (unidad_medida,))
            if not cur.fetchone():
                flash('La unidad de medida seleccionada no existe', 'error')
                cur.close()
                return redirect(url_for('producto_nuevo'))
            
            # Validación 9: Existencia en catálogo de categoría
            cur.execute("SELECT ID_Categoria FROM Categorias WHERE ID_Categoria = %s", (categoria_id,))
            if not cur.fetchone():
                flash('La categoría seleccionada no existe', 'error')
                cur.close()
                return redirect(url_for('producto_nuevo'))
            
            # Insertar producto
            cur.execute("""
                INSERT INTO Productos (Descripcion, Unidad_Medida, Precio_Venta, Costo_Promedio, 
                                     Categoria_ID, Stock_Minimo, Usuario_Creador)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (descripcion, unidad_medida, precio_venta, costo_promedio, categoria_id, 
                  stock_minimo, session['user_id']))
            
            producto_id = cur.lastrowid
            
            # Insertar en inventario
            cur.execute("""
                INSERT INTO Inventario_Bodega (ID_Bodega, ID_Producto, Existencias)
                VALUES (1, %s, %s)
            """, (producto_id, existencias_iniciales))
            
            mysql.connection.commit()
            cur.close()
            
            flash('Producto creado exitosamente', 'success')
            return redirect(url_for('productos'))
            
        except Exception as e:
            if 'cur' in locals():
                cur.close()
            flash(f'Error al crear el producto: {str(e)}', 'error')
            return redirect(url_for('producto_nuevo'))
    
    # GET request
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Categorias ORDER BY Descripcion")
    categorias = cur.fetchall()
    cur.execute("SELECT * FROM Unidades_Medida ORDER BY Descripcion")
    unidades = cur.fetchall()
    cur.close()
    
    return render_template('productos/form.html', 
                         categorias=categorias, 
                         unidades=unidades)

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def producto_editar(id):
    # Validación crítica del ID
    if id <= 0:
        flash('ID de producto inválido', 'error')
        return redirect(url_for('productos'))
    
    print(f"DEBUG: Editando producto ID: {id}")
    
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario (igual que en producto_nuevo)
            descripcion = request.form['descripcion'].strip()
            unidad_medida = request.form['unidad_medida']
            precio_venta = request.form['precio_venta']
            costo_promedio = request.form.get('costo_promedio', 0)
            categoria_id = request.form['categoria_id']
            stock_minimo = request.form.get('stock_minimo', 5)
            
            # Validación 1: Campos obligatorios
            campos_obligatorios = ['descripcion', 'unidad_medida', 'precio_venta', 'categoria_id']
            faltantes = [campo for campo in campos_obligatorios if not request.form.get(campo)]
            if faltantes:
                flash(f'Por favor complete los siguientes campos: {", ".join(faltantes)}', 'error')
                return redirect(url_for('producto_editar', id=id))
            
            # Validación 2: Descripción no vacía después de trim
            if not descripcion:
                flash('La descripción no puede estar vacía', 'error')
                return redirect(url_for('producto_editar', id=id))
            
            # Validación 3: Longitud máxima
            if len(descripcion) > 100:
                flash('La descripción no puede tener más de 100 caracteres', 'error')
                return redirect(url_for('producto_editar', id=id))
            
            # Validación 4: Producto duplicado (misma descripción, excluyendo el actual)
            cur.execute("""
                SELECT ID_Producto FROM Productos 
                WHERE LOWER(TRIM(Descripcion)) = LOWER(%s) 
                AND ID_Producto != %s
                AND Estado = 1
            """, (descripcion, id))
            
            producto_existente = cur.fetchone()
            if producto_existente:
                flash('Ya existe otro producto con esa descripción', 'error')
                cur.close()
                return redirect(url_for('producto_editar', id=id))
            
            # Validación 5: Formato numérico
            try:
                precio_venta = float(precio_venta)
                costo_promedio = float(costo_promedio) if costo_promedio else 0
                stock_minimo = int(stock_minimo)
            except ValueError:
                flash('Los valores numéricos deben ser números válidos', 'error')
                cur.close()
                return redirect(url_for('producto_editar', id=id))
            
            # Validación 6: Valores negativos
            if precio_venta < 0:
                flash('El precio de venta no puede ser negativo', 'error')
                cur.close()
                return redirect(url_for('producto_editar', id=id))
            
            if costo_promedio < 0:
                flash('El costo promedio no puede ser negativo', 'error')
                cur.close()
                return redirect(url_for('producto_editar', id=id))
            
            if stock_minimo < 0:
                flash('El stock mínimo no puede ser negativo', 'error')
                cur.close()
                return redirect(url_for('producto_editar', id=id))
            
            # Validación 7: Precio mayor a costo (opcional pero recomendado)
            if precio_venta <= costo_promedio:
                flash('Advertencia: El precio de venta es menor o igual al costo', 'warning')
                # No redirigimos, solo mostramos advertencia
            
            # Validación 8: Existencia en catálogo de unidad de medida
            cur.execute("SELECT ID_Unidad FROM Unidades_Medida WHERE ID_Unidad = %s", (unidad_medida,))
            if not cur.fetchone():
                flash('La unidad de medida seleccionada no existe', 'error')
                cur.close()
                return redirect(url_for('producto_editar', id=id))
            
            # Validación 9: Existencia en catálogo de categoría
            cur.execute("SELECT ID_Categoria FROM Categorias WHERE ID_Categoria = %s", (categoria_id,))
            if not cur.fetchone():
                flash('La categoría seleccionada no existe', 'error')
                cur.close()
                return redirect(url_for('producto_editar', id=id))
            
            # Actualizar producto - CORREGIDO para usar los tipos correctos
            # Nota: Convertimos unidad_medida y categoria_id a enteros ya que las validaciones
            # anteriores ya verificaron que existen
            unidad_medida = int(unidad_medida)
            categoria_id = int(categoria_id)
            
            cur.execute("""
                UPDATE Productos 
                SET Descripcion = %s, Unidad_Medida = %s, Precio_Venta = %s, 
                    Costo_Promedio = %s, Categoria_ID = %s, Stock_Minimo = %s
                WHERE ID_Producto = %s
            """, (descripcion, unidad_medida, precio_venta, costo_promedio, 
                  categoria_id, stock_minimo, id))
            
            mysql.connection.commit()
            flash('Producto actualizado exitosamente', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al actualizar el producto: {str(e)}', 'error')
            return redirect(url_for('producto_editar', id=id))
        
        finally:
            cur.close()
        
        return redirect(url_for('productos'))
    
    # GET - Cargar datos del producto
    try:
        print(f"DEBUG: Cargando datos para producto ID: {id}")
        
        # Obtener datos del producto
        cur.execute("SELECT * FROM Productos WHERE ID_Producto = %s AND Estado = 1", (id,))
        producto = cur.fetchone()
        
        print(f"DEBUG: Producto encontrado: {producto}")
        
        # Validar que el producto existe
        if not producto:
            flash('Producto no encontrado', 'error')
            cur.close()
            return redirect(url_for('productos'))
        
        # Obtener existencias actuales
        cur.execute("""
            SELECT COALESCE(SUM(Existencias), 0) as Existencias 
            FROM Inventario_Bodega 
            WHERE ID_Producto = %s
        """, (id,))
        existencias_data = cur.fetchone()
        
        # Extraer existencias del diccionario
        existencias = existencias_data.get('Existencias', 0) if existencias_data else 0
        
        print(f"DEBUG: Existencias: {existencias}")
        
        # Crear copia del diccionario del producto y agregar existencias
        producto_edit = dict(producto)
        producto_edit['Existencias'] = float(existencias)
        
        # Obtener categorías y unidades
        cur.execute("SELECT * FROM Categorias ORDER BY Descripcion")
        categorias = cur.fetchall()
        
        cur.execute("SELECT * FROM Unidades_Medida ORDER BY Descripcion")
        unidades = cur.fetchall()
        
        print(f"DEBUG: Categorías: {len(categorias)}, Unidades: {len(unidades)}")
        
    except Exception as e:
        error_msg = f"Error al cargar el producto: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        print(f"TRACEBACK: {traceback.format_exc()}")
        
        flash(error_msg, 'error')
        return redirect(url_for('productos'))
    
    finally:
        cur.close()
    
    return render_template('productos/form.html', 
                         producto=producto_edit, 
                         categorias=categorias, 
                         unidades=unidades)

@app.route('/productos/eliminar/<int:id>', methods=['POST'])
@admin_required
def producto_eliminar(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE Productos SET Estado = 'inactivo' WHERE ID_Producto = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('productos'))

# Categorías
@app.route('/categorias')
@admin_required
def categorias():
    cur = mysql.connection.cursor()
    # Solo mostrar categorías activas en la vista principal
    cur.execute("SELECT * FROM Categorias WHERE Estado = 'activo' ORDER BY Descripcion")
    categorias = cur.fetchall()
    cur.close()
    return render_template('productos/categorias.html', categorias=categorias)

@app.route('/categorias/nueva', methods=['POST'])
@admin_required
def categoria_nueva():
    descripcion = request.form['descripcion'].strip()
    
    # Validación 1: No permitir números en la descripción
    if re.search(r'\d', descripcion):
        flash('La categoría no puede contener números', 'error')
        return redirect(url_for('categorias'))
    
    # Validación 2: No permitir descripción vacía
    if not descripcion:
        flash('La descripción de la categoría no puede estar vacía', 'error')
        return redirect(url_for('categorias'))
    
    cur = mysql.connection.cursor()
    
    # Validación 3: No permitir categorías duplicadas (considerando solo activas o inactivas con el mismo nombre)
    cur.execute("""
        SELECT 1 FROM Categorias 
        WHERE LOWER(Descripcion) = LOWER(%s)
    """, (descripcion,))
    
    if cur.fetchone():
        cur.close()
        flash('Ya existe una categoría con este nombre', 'error')
        return redirect(url_for('categorias'))
    
    # Crear nueva categoría con estado activo por defecto
    cur.execute("INSERT INTO Categorias (Descripcion, Estado) VALUES (%s, 'activo')", (descripcion,))
    mysql.connection.commit()
    cur.close()
    
    flash('Categoría creada exitosamente', 'success')
    return redirect(url_for('categorias'))

@app.route('/categorias/editar/<int:id>', methods=['POST'])
@admin_required
def categoria_editar(id):
    descripcion = request.form['descripcion'].strip()
    
    # Validación 1: No permitir números en la descripción
    if re.search(r'\d', descripcion):
        flash('La categoría no puede contener números', 'error')
        return redirect(url_for('categorias'))
    
    # Validación 2: No permitir descripción vacía
    if not descripcion:
        flash('La descripción de la categoría no puede estar vacía', 'error')
        return redirect(url_for('categorias'))
    
    cur = mysql.connection.cursor()
    
    # Validación 3: Verificar que la categoría exista y esté activa
    cur.execute("SELECT 1 FROM Categorias WHERE ID_Categoria = %s AND Estado = 'activo'", (id,))
    if not cur.fetchone():
        cur.close()
        flash('La categoría no existe o está inactiva', 'error')
        return redirect(url_for('categorias'))
    
    # Validación 4: No permitir duplicados excluyendo la categoría actual
    cur.execute("""
        SELECT 1 FROM Categorias 
        WHERE LOWER(Descripcion) = LOWER(%s) 
        AND ID_Categoria != %s
    """, (descripcion, id))
    
    if cur.fetchone():
        cur.close()
        flash('Ya existe otra categoría con este nombre', 'error')
        return redirect(url_for('categorias'))
    
    # Actualizar descripción
    cur.execute("UPDATE Categorias SET Descripcion = %s WHERE ID_Categoria = %s", 
                (descripcion, id))
    mysql.connection.commit()
    cur.close()
    
    flash('Categoría actualizada exitosamente', 'success')
    return redirect(url_for('categorias'))

@app.route('/categorias/eliminar/<int:id>', methods=['POST'])
@admin_required
def categoria_eliminar(id):
    cur = mysql.connection.cursor()
    
    # Verificar si hay productos asociados a esta categoría
    cur.execute("""
        SELECT 1 FROM Productos 
        WHERE ID_Categoria = %s AND Estado = 'activo'
    """, (id,))
    
    if cur.fetchone():
        cur.close()
        flash('No se puede eliminar la categoría porque tiene productos asociados', 'error')
        return redirect(url_for('categorias'))
    
    # En lugar de eliminar físicamente, cambiar estado a inactivo (soft delete)
    cur.execute("UPDATE Categorias SET Estado = 'inactivo' WHERE ID_Categoria = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Categoría marcada como inactiva exitosamente', 'success')
    return redirect(url_for('categorias'))

@app.route('/categorias/inactivas')
@admin_required
def categorias_inactivas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Categorias WHERE Estado = 'inactivo' ORDER BY Descripcion")
    categorias = cur.fetchall()
    cur.close()
    return render_template('productos/categorias_inactivas.html', categorias=categorias)

@app.route('/categorias/activar/<int:id>', methods=['POST'])
@admin_required
def categoria_activar(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE Categorias SET Estado = 'activo' WHERE ID_Categoria = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Categoría reactivada exitosamente', 'success')
    return redirect(url_for('categorias_inactivas'))

# Unidades de Medida
@app.route('/unidades-medida')
@admin_required
def unidades_medida():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Unidades_Medida ORDER BY Descripcion")
    unidades = cur.fetchall()
    cur.close()
    return render_template('productos/unidades.html', unidades=unidades)

@app.route('/unidades-medida/nueva', methods=['POST'])
@admin_required
def unidad_nueva():
    descripcion = request.form['descripcion'].strip()
    abreviatura = request.form['abreviatura'].strip()
    
    cur = mysql.connection.cursor()
    
    # Validar que la descripción no exista en unidades activas
    cur.execute("""
        SELECT COUNT(*) as count FROM Unidades_Medida 
        WHERE LOWER(Descripcion) = LOWER(%s) AND Estado = 'activo'
    """, (descripcion,))
    resultado = cur.fetchone()
    existe_descripcion = resultado['count']
    
    if existe_descripcion > 0:
        flash('La descripción ya existe en una unidad activa. Por favor, use otra descripción.', 'error')
        return redirect(url_for('unidades_medida'))
    
    # Validar que la abreviatura no exista en unidades activas
    cur.execute("""
        SELECT COUNT(*) as count FROM Unidades_Medida 
        WHERE LOWER(Abreviatura) = LOWER(%s) AND Estado = 'activo'
    """, (abreviatura,))
    resultado = cur.fetchone()
    existe_abreviatura = resultado['count']
    
    if existe_abreviatura > 0:
        flash('La abreviatura ya existe en una unidad activa. Por favor, use otra abreviatura.', 'error')
        return redirect(url_for('unidades_medida'))
    
    # Insertar nueva unidad como activa por defecto
    cur.execute("""
        INSERT INTO Unidades_Medida (Descripcion, Abreviatura, Estado) 
        VALUES (%s, %s, 'activo')
    """, (descripcion, abreviatura))
    mysql.connection.commit()
    cur.close()
    
    flash('Unidad de medida creada exitosamente', 'success')
    return redirect(url_for('unidades_medida'))

@app.route('/unidades-medida/editar/<int:id>', methods=['POST'])
@admin_required
def unidad_editar(id):
    descripcion = request.form['descripcion'].strip()
    abreviatura = request.form['abreviatura'].strip()
    
    cur = mysql.connection.cursor()
    
    # Validar que la descripción no exista en otras unidades activas
    cur.execute("""
        SELECT COUNT(*) as count FROM Unidades_Medida 
        WHERE LOWER(Descripcion) = LOWER(%s) 
        AND ID_Unidad != %s 
        AND Estado = 'activo'
    """, (descripcion, id))
    resultado = cur.fetchone()
    existe_descripcion = resultado['count']
    
    if existe_descripcion > 0:
        flash('La descripción ya existe en otra unidad activa. Por favor, use otra descripción.', 'error')
        return redirect(url_for('unidades_medida'))
    
    # Validar que la abreviatura no exista en otras unidades activas
    cur.execute("""
        SELECT COUNT(*) as count FROM Unidades_Medida 
        WHERE LOWER(Abreviatura) = LOWER(%s) 
        AND ID_Unidad != %s 
        AND Estado = 'activo'
    """, (abreviatura, id))
    resultado = cur.fetchone()
    existe_abreviatura = resultado['count']
    
    if existe_abreviatura > 0:
        flash('La abreviatura ya existe en otra unidad activa. Por favor, use otra abreviatura.', 'error')
        return redirect(url_for('unidades_medida'))
    
    # Actualizar la unidad
    cur.execute("""
        UPDATE Unidades_Medida 
        SET Descripcion = %s, Abreviatura = %s 
        WHERE ID_Unidad = %s
    """, (descripcion, abreviatura, id))
    
    mysql.connection.commit()
    cur.close()
    
    flash('Unidad de medida actualizada exitosamente', 'success')
    return redirect(url_for('unidades_medida'))

@app.route('/unidades-medida/cambiar-estado/<int:id>', methods=['POST'])
@admin_required
def unidad_cambiar_estado(id):
    # Esta función cambia el estado entre 'activo' e 'inactivo'
    cur = mysql.connection.cursor()
    
    # Obtener el estado actual
    cur.execute("SELECT Estado FROM Unidades_Medida WHERE ID_Unidad = %s", (id,))
    unidad = cur.fetchone()
    
    if not unidad:
        flash('Unidad no encontrada', 'error')
        return redirect(url_for('unidades_medida'))
    
    # Cambiar el estado
    nuevo_estado = 'inactivo' if unidad['Estado'] == 'activo' else 'activo'
    
    # Verificar si hay productos usando esta unidad antes de inactivar
    if nuevo_estado == 'inactivo':
        cur.execute("""
            SELECT COUNT(*) as count FROM Productos 
            WHERE ID_Unidad = %s AND Estado = 'activo'
        """, (id,))
        resultado = cur.fetchone()
        productos_activos = resultado['count']
        
        if productos_activos > 0:
            flash(f'No se puede inactivar la unidad porque está siendo usada por {productos_activos} producto(s) activo(s).', 'error')
            return redirect(url_for('unidades_medida'))
    
    # Actualizar el estado
    cur.execute("""
        UPDATE Unidades_Medida 
        SET Estado = %s 
        WHERE ID_Unidad = %s
    """, (nuevo_estado, id))
    
    mysql.connection.commit()
    cur.close()
    
    accion = "activada" if nuevo_estado == 'activo' else "inactivada"
    flash(f'Unidad de medida {accion} exitosamente', 'success')
    return redirect(url_for('unidades_medida'))

# Opcional: Si prefieres eliminar físicamente en lugar de cambiar estado
@app.route('/unidades-medida/eliminar/<int:id>', methods=['POST'])
@admin_required
def unidad_eliminar(id):
    cur = mysql.connection.cursor()
    
    # Verificar si hay productos usando esta unidad
    cur.execute("SELECT COUNT(*) as count FROM Productos WHERE ID_Unidad = %s", (id,))
    resultado = cur.fetchone()
    productos_relacionados = resultado['count']
    
    if productos_relacionados > 0:
        flash(f'No se puede eliminar la unidad porque está siendo usada por {productos_relacionados} producto(s).', 'error')
        return redirect(url_for('unidades_medida'))
    
    # Si no hay productos relacionados, eliminar
    cur.execute("DELETE FROM Unidades_Medida WHERE ID_Unidad = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Unidad de medida eliminada exitosamente', 'success')
    return redirect(url_for('unidades_medida'))

# Proveedores
@app.route('/proveedores')
@admin_required
def proveedores():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Proveedores ORDER BY Nombre")
    proveedores = cur.fetchall()
    cur.close()
    return render_template('proveedores/lista.html', proveedores=proveedores)

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@admin_required
def proveedor_nuevo():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()
        ruc_cedula = request.form.get('ruc_cedula', '').strip()
        estado = request.form.get('estado', 'activo')  # Nuevo campo
        
        # Validar campos obligatorios
        if not nombre:
            flash('El nombre del proveedor es requerido', 'error')
            return render_template('proveedores/form.html')
        
        cur = mysql.connection.cursor()
        
        # Verificar que el nombre no exista
        cur.execute("SELECT ID_Proveedor, Nombre FROM Proveedores WHERE LOWER(Nombre) = LOWER(%s)", 
                    (nombre,))
        proveedores_existentes = cur.fetchall()
        
        if proveedores_existentes:
            flash(f'El nombre "{nombre}" ya existe', 'error')
            return render_template('proveedores/form.html')
        
        # Alternativa más estricta: también verificar nombres similares (incluyendo espacios)
        cur.execute("SELECT ID_Proveedor, Nombre FROM Proveedores WHERE TRIM(Nombre) = %s", 
                    (nombre,))
        proveedores_exactos = cur.fetchall()
        
        if proveedores_exactos:
            flash(f'Ya existe un proveedor con el nombre exacto: "{nombre}"', 'error')
            return render_template('proveedores/form.html')
        
        # Validar que el RUC/Cédula no exista (si se proporciona)
        if ruc_cedula:
            cur.execute("SELECT COUNT(*) as count FROM Proveedores WHERE RUC_CEDULA = %s", 
                        (ruc_cedula,))
            resultado = cur.fetchone()
            existe_ruc = resultado['count']
            
            if existe_ruc > 0:
                flash('El RUC/Cédula ya existe. Por favor, verifique el número.', 'error')
                return render_template('proveedores/form.html')
        
        # Si todo está bien, insertar
        cur.execute("""
            INSERT INTO Proveedores (Nombre, Telefono, Direccion, RUC_CEDULA, Estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, telefono, direccion, ruc_cedula, estado))
        mysql.connection.commit()
        cur.close()
        
        flash('Proveedor creado exitosamente', 'success')
        return redirect(url_for('proveedores'))
    
    return render_template('proveedores/form.html')

@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def proveedor_editar(id):
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()
        ruc_cedula = request.form.get('ruc_cedula', '').strip()
        estado = request.form.get('estado', 'activo')  # Nuevo campo
        
        # Validar campos obligatorios
        if not nombre:
            flash('El nombre del proveedor es requerido', 'error')
            cur.execute("SELECT * FROM Proveedores WHERE ID_Proveedor = %s", (id,))
            proveedor = cur.fetchone()
            cur.close()
            return render_template('proveedores/form.html', proveedor=proveedor)
        
        # Obtener el nombre actual del proveedor
        cur.execute("SELECT Nombre FROM Proveedores WHERE ID_Proveedor = %s", (id,))
        proveedor_actual = cur.fetchone()
        nombre_actual = proveedor_actual['Nombre'].strip() if proveedor_actual else ""
        
        # Solo validar si el nombre cambió
        if nombre.lower() != nombre_actual.lower():
            # Validar que el nuevo nombre no exista en otros proveedores
            cur.execute("""
                SELECT ID_Proveedor, Nombre FROM Proveedores 
                WHERE LOWER(Nombre) = LOWER(%s) AND ID_Proveedor != %s
            """, (nombre, id))
            otros_proveedores = cur.fetchall()
            
            if otros_proveedores:
                flash(f'El nombre "{nombre}" ya existe', 'error')
                cur.execute("SELECT * FROM Proveedores WHERE ID_Proveedor = %s", (id,))
                proveedor = cur.fetchone()
                cur.close()
                return render_template('proveedores/form.html', proveedor=proveedor)
        
        # Validar que el RUC/Cédula no exista en otros proveedores
        if ruc_cedula:
            cur.execute("""
                SELECT COUNT(*) as count FROM Proveedores 
                WHERE RUC_CEDULA = %s AND ID_Proveedor != %s
            """, (ruc_cedula, id))
            resultado = cur.fetchone()
            existe_ruc = resultado['count']
            
            if existe_ruc > 0:
                flash('El RUC/Cédula ya existe en otro proveedor. Por favor, verifique el número.', 'error')
                cur.execute("SELECT * FROM Proveedores WHERE ID_Proveedor = %s", (id,))
                proveedor = cur.fetchone()
                cur.close()
                return render_template('proveedores/form.html', proveedor=proveedor)
        
        # Si todo está bien, actualizar
        cur.execute("""
            UPDATE Proveedores 
            SET Nombre = %s, Telefono = %s, Direccion = %s, 
                RUC_CEDULA = %s, Estado = %s
            WHERE ID_Proveedor = %s
        """, (nombre, telefono, direccion, ruc_cedula, estado, id))
        mysql.connection.commit()
        cur.close()
        
        flash('Proveedor actualizado exitosamente', 'success')
        return redirect(url_for('proveedores'))
    
    cur.execute("SELECT * FROM Proveedores WHERE ID_Proveedor = %s", (id,))
    proveedor = cur.fetchone()
    cur.close()
    
    return render_template('proveedores/form.html', proveedor=proveedor)

@app.route('/proveedores/eliminar/<int:id>', methods=['POST'])
@admin_required
def proveedor_eliminar(id):
    cur = mysql.connection.cursor()
    
    # Verificar si el proveedor tiene compras asociadas antes de eliminar
    cur.execute("SELECT COUNT(*) as count FROM Compras WHERE ID_Proveedor = %s", (id,))
    resultado = cur.fetchone()
    
    if resultado['count'] > 0:
        # En lugar de eliminar, cambiar el estado a 'inactivo'
        cur.execute("UPDATE Proveedores SET Estado = 'inactivo' WHERE ID_Proveedor = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('El proveedor tenía compras asociadas, se ha cambiado a estado inactivo', 'warning')
    else:
        # Eliminar completamente si no tiene compras
        cur.execute("DELETE FROM Proveedores WHERE ID_Proveedor = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Proveedor eliminado exitosamente', 'success')
    
    return redirect(url_for('proveedores'))

# Sistema de Ventas (POS) - Accesible para vendedores y administradores
@app.route('/ventas')
@login_required
def ventas():
    cur = mysql.connection.cursor()
    
    try:
        # Obtener productos activos con stock (CORREGIDO para nuevas tablas)
        cur.execute("""
            SELECT p.*, c.Descripcion as Categoria, u.Abreviatura,
                   COALESCE(ib.Existencias, 0) as Stock_Bodega
            FROM Productos p
            LEFT JOIN Categorias c ON p.Categoria_ID = c.ID_Categoria
            LEFT JOIN Unidades_Medida u ON p.Unidad_Medida = u.ID_Unidad
            LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto AND ib.ID_Bodega = 1
            WHERE p.Estado = 'activo' AND COALESCE(ib.Existencias, 0) > 0
            ORDER BY p.Descripcion
        """)
        productos = cur.fetchall()
        
        # Obtener métodos de pago activos
        cur.execute("SELECT * FROM Metodos_Pago WHERE Nombre = 'EFECTIVO' ")
        metodos_pago = cur.fetchall()
        
        # Obtener categorías activas para filtros
        cur.execute("SELECT * FROM Categorias ORDER BY Descripcion")
        categorias = cur.fetchall()
        
        # Obtener bodega principal para ventas
        cur.execute("SELECT * FROM Bodegas WHERE ID_Bodega = 1")
        bodega_principal = cur.fetchone()
        
        return render_template('ventas/pos.html', 
                             productos=productos, 
                             metodos_pago=metodos_pago,
                             categorias=categorias,
                             bodega_principal=bodega_principal)
    except Exception as e:
        flash(f'Error al cargar datos: {str(e)}', 'danger')
        return render_template('ventas/pos.html', 
                             productos=[], 
                             metodos_pago=[],
                             categorias=[],
                             bodega_principal=None)
    finally:
        cur.close()

@app.route('/ventas/procesar', methods=['POST'])
@login_required
def procesar_venta():
    try:
        data = request.get_json()
        items = data.get('items', [])
        metodo_pago_id = data.get('metodo_pago_id')
        efectivo = data.get('efectivo', 0)
        observacion = data.get('observacion', '')
        bodega_id = data.get('bodega_id', 1)
        
        # Validaciones básicas
        if not items:
            return jsonify({'success': False, 'message': 'No hay productos en el carrito'}), 400
        
        if not metodo_pago_id:
            return jsonify({'success': False, 'message': 'Selecciona un método de pago'}), 400
        
        # Calcular total - CORREGIDO: convertir cantidades a int
        total = sum(float(item['subtotal']) for item in items)
        cambio = max(float(efectivo) - total, 0)
        
        cur = mysql.connection.cursor()
        
        # Verificar stock disponible EN LA BODEGA (CORREGIDO para enteros)
        productos_sin_stock = []
        for item in items:
            producto_id = item['producto_id']
            # Convertir a int para validación de stock
            cantidad_necesaria = int(float(item['cantidad']))
            
            cur.execute("""
                SELECT p.Descripcion, p.Estado, COALESCE(ib.Existencias, 0) as Stock_Bodega
                FROM Productos p
                LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto AND ib.ID_Bodega = %s
                WHERE p.ID_Producto = %s AND p.Estado = 'activo'
            """, (bodega_id, producto_id))
            
            inventario = cur.fetchone()
            stock_disponible = int(inventario['Stock_Bodega']) if inventario else 0
            
            if not inventario:
                productos_sin_stock.append(f"Producto ID {producto_id} no encontrado o inactivo")
            elif stock_disponible < cantidad_necesaria:
                productos_sin_stock.append(
                    f"{inventario['Descripcion']} (disp: {stock_disponible}, neces: {cantidad_necesaria})"
                )
        
        if productos_sin_stock:
            mensaje_error = "Stock insuficiente: " + ", ".join(productos_sin_stock)
            return jsonify({'success': False, 'message': mensaje_error}), 400
        
        # Insertar factura
        cur.execute("""
            INSERT INTO Facturacion (Total, Efectivo, Cambio, ID_MetodoPago, Observacion, ID_Usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (total, efectivo, cambio, metodo_pago_id, observacion, session['user_id']))
        
        factura_id = cur.lastrowid
        
        # Obtener ID del tipo de movimiento para venta
        cur.execute("""
            SELECT ID_TipoMovimiento 
            FROM Catalogo_Movimientos 
            WHERE Descripcion LIKE '%VENTA%' AND Adicion = 'SALIDA'
        """)
        tipo_movimiento_venta = cur.fetchone()
        
        if not tipo_movimiento_venta:
            mysql.connection.rollback()
            return jsonify({'success': False, 'message': 'Tipo de movimiento para venta no configurado'}), 500
        
        # GENERAR NÚMERO DE FACTURA CON PREFIJO VTA- PARA VENTAS
        numero_factura = f"VTA-{factura_id:06d}"  # VTA-000001, VTA-000002
        
        # Insertar movimiento de inventario para la venta
        cur.execute("""
            INSERT INTO Movimientos_Inventario 
            (ID_TipoMovimiento, N_Factura, Observacion, ID_Bodega)
            VALUES (%s, %s, %s, %s)
        """, (tipo_movimiento_venta['ID_TipoMovimiento'], numero_factura, f"Venta - Factura #{factura_id}", bodega_id))
        
        movimiento_id = cur.lastrowid
        
        # Insertar detalles de factura y ACTUALIZAR STOCK (CORREGIDO para enteros)
        for item in items:
            producto_id = item['producto_id']
            # Convertir a int para la base de datos
            cantidad = int(float(item['cantidad']))
            precio_venta = float(item['precio_venta'])
            subtotal = float(item['subtotal'])
            
            # Insertar detalle de factura (Cantidad ahora es INT)
            cur.execute("""
                INSERT INTO Detalle_Facturacion (ID_Factura, ID_Producto, Cantidad, Precio_Venta, Subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (factura_id, producto_id, cantidad, precio_venta, subtotal))
            
            # Insertar detalle en movimiento de inventario (Cantidad ahora es INT)
            cur.execute("""
                INSERT INTO Detalle_Movimiento_Inventario 
                (ID_Movimiento, ID_Producto, Cantidad, Costo, Costo_Total)
                VALUES (%s, %s, %s, %s, %s)
            """, (movimiento_id, producto_id, cantidad, precio_venta, subtotal))
            
            # ACTUALIZAR INVENTARIO EN BODEGA (Existencias ahora es INT)
            cur.execute("""
                SELECT 1 FROM Inventario_Bodega 
                WHERE ID_Producto = %s AND ID_Bodega = %s
            """, (producto_id, bodega_id))
            
            if cur.fetchone():
                cur.execute("""
                    UPDATE Inventario_Bodega 
                    SET Existencias = Existencias - %s 
                    WHERE ID_Producto = %s AND ID_Bodega = %s
                """, (cantidad, producto_id, bodega_id))
            else:
                # Si no existe registro, crear uno con existencia negativa
                cur.execute("""
                    INSERT INTO Inventario_Bodega (ID_Bodega, ID_Producto, Existencias)
                    VALUES (%s, %s, %s)
                """, (bodega_id, producto_id, -cantidad))
        
        mysql.connection.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Venta procesada exitosamente! Factura #{factura_id}',
            'factura_id': factura_id,
            'n_factura': numero_factura,
            'total': total,
            'cambio': cambio
        })
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': f'Error al procesar la venta: {str(e)}'}), 500
    finally:
        cur.close()

@app.route('/ventas/historial')
@login_required
def ventas_historial():
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    
    cur = mysql.connection.cursor()
    
    try:
        # Construir consulta base (optimizada)
        if session.get('rol_id') == 2:  # Vendedor
            sql = """
                SELECT f.*, u.NombreUsuario, m.Nombre as MetodoPago
                FROM Facturacion f
                INNER JOIN Usuarios u ON f.ID_Usuario = u.ID_Usuario
                INNER JOIN Metodos_Pago m ON f.ID_MetodoPago = m.ID_MetodoPago
                WHERE f.ID_Usuario = %s AND f.Estado = 1
            """
            params = [session['user_id']]
        else:  # Administrador
            sql = """
                SELECT f.*, u.NombreUsuario, m.Nombre as MetodoPago
                FROM Facturacion f
                INNER JOIN Usuarios u ON f.ID_Usuario = u.ID_Usuario
                INNER JOIN Metodos_Pago m ON f.ID_MetodoPago = m.ID_MetodoPago
                WHERE f.Estado = 1
            """
            params = []
        
        # Aplicar filtros de fecha
        if fecha_inicio:
            sql += " AND f.Fecha >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            sql += " AND f.Fecha <= %s"
            params.append(fecha_fin)
        
        sql += " ORDER BY f.Fecha DESC, f.Hora DESC LIMIT 100"
        
        cur.execute(sql, params)
        ventas = cur.fetchall()
        
        # Estadísticas
        total_ventas = len(ventas)
        total_monto = sum(float(venta['Total']) for venta in ventas) if ventas else 0
        
        mensaje = f'Mostrando {total_ventas} ventas - Total: ${total_monto:.2f}' if fecha_inicio or fecha_fin else f'Historial de ventas - {total_ventas} registros'
        
        return render_template('ventas/historial.html', 
                             ventas=ventas, 
                             fecha_inicio=fecha_inicio, 
                             fecha_fin=fecha_fin,
                             mensaje=mensaje)
    except Exception as e:
        flash(f'Error al cargar historial: {str(e)}', 'danger')
        return render_template('ventas/historial.html', ventas=[])
    finally:
        cur.close()

@app.route('/ventas/detalle/<int:id>')
@login_required
def venta_detalle(id):
    cur = mysql.connection.cursor()
    
    try:
        # Obtener factura
        cur.execute("""
            SELECT f.*, u.NombreUsuario, m.Nombre as MetodoPago
            FROM Facturacion f
            INNER JOIN Usuarios u ON f.ID_Usuario = u.ID_Usuario
            INNER JOIN Metodos_Pago m ON f.ID_MetodoPago = m.ID_MetodoPago
            WHERE f.ID_Factura = %s AND f.Estado = 1
        """, (id,))
        factura = cur.fetchone()
        
        if not factura:
            flash('Factura no encontrada', 'danger')
            return redirect(url_for('ventas_historial'))
        
        # Verificar permisos
        if session.get('rol_id') == 2 and factura['ID_Usuario'] != session['user_id']:
            flash('No tienes permisos para ver esta factura', 'danger')
            return redirect(url_for('ventas_historial'))
        
        # Obtener detalles
        cur.execute("""
            SELECT df.*, p.Descripcion as Producto, u.Abreviatura
            FROM Detalle_Facturacion df
            INNER JOIN Productos p ON df.ID_Producto = p.ID_Producto
            LEFT JOIN Unidades_Medida u ON p.Unidad_Medida = u.ID_Unidad
            WHERE df.ID_Factura = %s
        """, (id,))
        detalles = cur.fetchall()
        
        return render_template('ventas/detalle.html', factura=factura, detalles=detalles)
    except Exception as e:
        flash(f'Error al cargar detalle: {str(e)}', 'danger')
        return redirect(url_for('ventas_historial'))
    finally:
        cur.close()

@app.route('/api/productos/buscar')
@login_required
def buscar_productos():
    query = request.args.get('q', '')
    categoria_id = request.args.get('categoria', '')
    bodega_id = request.args.get('bodega_id', 1)
    
    cur = mysql.connection.cursor()
    
    try:
        sql = """
            SELECT p.*, c.Descripcion as Categoria, u.Abreviatura,
                   COALESCE(ib.Existencias, 0) as Stock_Bodega
            FROM Productos p
            LEFT JOIN Categorias c ON p.Categoria_ID = c.ID_Categoria
            LEFT JOIN Unidades_Medida u ON p.Unidad_Medida = u.ID_Unidad
            LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto AND ib.ID_Bodega = %s
            WHERE p.Estado = 1 AND COALESCE(ib.Existencias, 0) > 0
        """
        params = [bodega_id]
        
        if query:
            sql += " AND (p.Descripcion LIKE %s OR p.ID_Producto = %s)"
            params.extend([f'%{query}%', query if query.isdigit() else '0'])
        
        if categoria_id and categoria_id != 'todas':
            sql += " AND p.Categoria_ID = %s"
            params.append(categoria_id)
        
        sql += " ORDER BY p.Descripcion LIMIT 50"
        
        cur.execute(sql, params)
        productos = cur.fetchall()
        
        return jsonify([dict(producto) for producto in productos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()

@app.route('/api/producto/<int:id>')
@login_required
def obtener_producto(id):
    bodega_id = request.args.get('bodega_id', 1)
    
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT p.*, c.Descripcion as Categoria, u.Abreviatura,
                   COALESCE(ib.Existencias, 0) as Stock_Bodega
            FROM Productos p
            LEFT JOIN Categorias c ON p.Categoria_ID = c.ID_Categoria
            LEFT JOIN Unidades_Medida u ON p.Unidad_Medida = u.ID_Unidad
            LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto AND ib.ID_Bodega = %s
            WHERE p.ID_Producto = %s AND p.Estado = 1
        """, (bodega_id, id))
        producto = cur.fetchone()
        
        if producto:
            return jsonify(dict(producto))
        
        return jsonify({'error': 'Producto no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()

# Inventario - Gestión de movimientos
@app.route('/inventario')
@admin_required
def inventario():
    cur = mysql.connection.cursor()
    
    # Obtener movimientos recientes
    cur.execute("""
        SELECT mi.*, cm.Descripcion as TipoMovimiento, cm.Letra, 
               p.Nombre as Proveedor, b.Nombre as Bodega
        FROM Movimientos_Inventario mi
        INNER JOIN Catalogo_Movimientos cm ON mi.ID_TipoMovimiento = cm.ID_TipoMovimiento
        LEFT JOIN Proveedores p ON mi.ID_Proveedor = p.ID_Proveedor
        LEFT JOIN Bodegas b ON mi.ID_Bodega = b.ID_Bodega
        ORDER BY mi.Fecha DESC, mi.ID_Movimiento DESC
        LIMIT 100
    """)
    movimientos = cur.fetchall()
    
    cur.close()
    return render_template('inventario/lista.html', movimientos=movimientos)

@app.route('/inventario/entrada', methods=['GET', 'POST'])
@admin_required
def inventario_entrada():
    if request.method == 'POST':
        try:
            data = request.get_json()
            tipo_movimiento_id = data.get('tipo_movimiento_id')
            proveedor_id = data.get('proveedor_id')
            bodega_id = data.get('bodega_id')
            n_factura = data.get('n_factura', '').strip()
            observacion = data.get('observacion', '').strip()
            items = data.get('items', [])
            
            # Validaciones básicas
            if not items:
                return jsonify({'success': False, 'message': 'No hay productos en el movimiento'}), 400
            
            if not bodega_id:
                return jsonify({'success': False, 'message': 'Debe seleccionar una bodega'}), 400
            
            if not proveedor_id:
                return jsonify({'success': False, 'message': 'Debe seleccionar un proveedor'}), 400
            
            cur = mysql.connection.cursor()
            
            # VERIFICAR que el tipo de movimiento es de entrada
            cur.execute("""
                SELECT Descripcion, Adicion 
                FROM Catalogo_Movimientos 
                WHERE ID_TipoMovimiento = %s
            """, (tipo_movimiento_id,))
            tipo_movimiento = cur.fetchone()
            
            if not tipo_movimiento or tipo_movimiento['Adicion'] != 'ENTRADA':
                return jsonify({'success': False, 'message': 'Tipo de movimiento no válido para entrada'}), 400
            
            # Verificar que la bodega existe (bodega no tiene estado)
            cur.execute("SELECT Nombre FROM Bodegas WHERE ID_Bodega = %s", (bodega_id,))
            bodega = cur.fetchone()
            if not bodega:
                return jsonify({'success': False, 'message': 'Bodega no encontrada'}), 400
            
            # Verificar que el proveedor existe y está activo
            cur.execute("SELECT Nombre, Estado FROM Proveedores WHERE ID_Proveedor = %s", (proveedor_id,))
            proveedor = cur.fetchone()
            if not proveedor:
                return jsonify({'success': False, 'message': 'Proveedor no encontrado'}), 400
            if proveedor['Estado'] != 'activo':
                return jsonify({'success': False, 'message': 'El proveedor seleccionado no está activo'}), 400
            
            # LÓGICA PARA N_FACTURA
            if n_factura:
                # Si el usuario ingresó una factura, verificar que no exista previamente
                cur.execute("""
                    SELECT ID_Movimiento 
                    FROM Movimientos_Inventario 
                    WHERE N_Factura = %s AND ID_Proveedor = %s
                """, (n_factura, proveedor_id))
                if cur.fetchone():
                    return jsonify({
                        'success': False, 
                        'message': f'Ya existe un movimiento con la factura {n_factura} para este proveedor'
                    }), 400
                numero_factura_final = n_factura
                tipo_factura = "factura_proveedor"
            else:
                # Generar número interno automático con prefijo CMP-
                cur.execute("""
                    SELECT MAX(CAST(SUBSTRING(N_Factura, 5) AS UNSIGNED)) as last_num
                    FROM Movimientos_Inventario 
                    WHERE N_Factura LIKE 'CMP-%'
                """)
                last_mov = cur.fetchone()
                last_num = last_mov['last_num'] if last_mov and last_mov['last_num'] else 0
                numero_factura_final = f"CMP-{(last_num + 1):06d}"
                tipo_factura = "interno"
            
            # Validar que todos los productos existen y están activos
            producto_ids = [item['producto_id'] for item in items]
            placeholders = ','.join(['%s'] * len(producto_ids))
            
            cur.execute(f"""
                SELECT ID_Producto, Descripcion, Estado, Costo_Promedio
                FROM Productos 
                WHERE ID_Producto IN ({placeholders})
            """, tuple(producto_ids))
            
            productos_db = {p['ID_Producto']: p for p in cur.fetchall()}
            
            for item in items:
                producto_id = item['producto_id']
                if producto_id not in productos_db:
                    return jsonify({
                        'success': False, 
                        'message': f'Producto ID {producto_id} no encontrado'
                    }), 400
                
                if productos_db[producto_id]['Estado'] != 'activo':
                    return jsonify({
                        'success': False, 
                        'message': f'Producto "{productos_db[producto_id]["Descripcion"]}" no está activo'
                    }), 400
            
            # Insertar movimiento
            cur.execute("""
                INSERT INTO Movimientos_Inventario 
                (ID_TipoMovimiento, N_Factura, ID_Proveedor, Observacion, ID_Bodega, Fecha_Creacion)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (tipo_movimiento_id, numero_factura_final, proveedor_id, observacion, bodega_id))
            
            movimiento_id = cur.lastrowid
            
            # Procesar cada item del movimiento
            total_productos = 0
            total_costo = 0
            
            for item in items:
                producto_id = item['producto_id']
                cantidad = int(item['cantidad'])
                costo = float(item['costo'])
                costo_total = float(item['costo_total'])
                
                if cantidad <= 0:
                    mysql.connection.rollback()
                    return jsonify({
                        'success': False, 
                        'message': f'Cantidad inválida para producto ID {producto_id}'
                    }), 400
                
                if costo <= 0:
                    mysql.connection.rollback()
                    return jsonify({
                        'success': False, 
                        'message': f'Costo inválido para producto ID {producto_id}'
                    }), 400
                
                total_productos += cantidad
                total_costo += costo_total
                
                # Insertar detalle del movimiento
                cur.execute("""
                    INSERT INTO Detalle_Movimiento_Inventario 
                    (ID_Movimiento, ID_Producto, Cantidad, Costo, Costo_Total)
                    VALUES (%s, %s, %s, %s, %s)
                """, (movimiento_id, producto_id, cantidad, costo, costo_total))
                
                # ACTUALIZAR INVENTARIO EN BODEGA
                cur.execute("""
                    INSERT INTO Inventario_Bodega (ID_Bodega, ID_Producto, Existencias)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    Existencias = Existencias + VALUES(Existencias)
                """, (bodega_id, producto_id, cantidad))
                
                # ACTUALIZAR COSTO PROMEDIO
                # Obtener existencias totales actuales
                cur.execute("""
                    SELECT COALESCE(SUM(Existencias), 0) as Existencias_Totales
                    FROM Inventario_Bodega 
                    WHERE ID_Producto = %s
                """, (producto_id,))
                existencias_result = cur.fetchone()
                existencias_totales = existencias_result['Existencias_Totales'] if existencias_result else 0
                
                # Obtener el costo promedio actual
                cur.execute("SELECT Costo_Promedio FROM Productos WHERE ID_Producto = %s", (producto_id,))
                producto_actual = cur.fetchone()
                costo_promedio_actual = float(producto_actual['Costo_Promedio']) if producto_actual and producto_actual['Costo_Promedio'] else 0.0
                
                # Calcular nuevo costo promedio
                if existencias_totales > 0:
                    # Fórmula: (costo_actual * existencias_actuales + costo_nuevo * cantidad_nueva) / (existencias_actuales + cantidad_nueva)
                    valor_actual = costo_promedio_actual * (existencias_totales - cantidad)
                    valor_nuevo = costo * cantidad
                    nuevo_costo_promedio = (valor_actual + valor_nuevo) / existencias_totales
                else:
                    nuevo_costo_promedio = costo
                
                # Actualizar costo promedio en Productos
                cur.execute("""
                    UPDATE Productos 
                    SET Costo_Promedio = %s
                    WHERE ID_Producto = %s
                """, (nuevo_costo_promedio, producto_id))
            
            mysql.connection.commit()
            cur.close()
            
            mensaje = f'✅ Entrada registrada exitosamente! Movimiento #{movimiento_id}'
            if tipo_factura == "factura_proveedor":
                mensaje += f' - Factura: {numero_factura_final}'
            else:
                mensaje += f' - Referencia: {numero_factura_final}'
            mensaje += f' - {total_productos} unidades - Total: ${total_costo:,.2f} en {bodega["Nombre"]}'
            
            flash(mensaje, 'success')
            return jsonify({
                'success': True,
                'message': 'Entrada de inventario registrada exitosamente',
                'movimiento_id': movimiento_id,
                'n_factura': numero_factura_final,
                'tipo_factura': tipo_factura,
                'total_productos': total_productos,
                'total_costo': total_costo,
                'bodega_nombre': bodega['Nombre']
            })
            
        except Exception as e:
            mysql.connection.rollback()
            error_msg = f'❌ Error al registrar entrada: {str(e)}'
            print(error_msg)  # Para debugging
            return jsonify({'success': False, 'message': error_msg}), 500
    
    # ===== GET - Cargar datos para el formulario =====
    cur = mysql.connection.cursor()
    
    # Obtener proveedor_id del query string si existe (para filtro visual)
    proveedor_filtro = request.args.get('proveedor_filtro', type=int)
    
    # Base de la consulta de productos (solo activos)
    query_productos = """
        SELECT 
            p.ID_Producto,
            p.Descripcion,
            p.Unidad_Medida,
            p.Estado,
            p.Costo_Promedio,
            p.Precio_Venta,
            p.Categoria_ID,
            p.Fecha_Creacion,
            p.Usuario_Creador,
            p.Stock_minimo,
            c.Descripcion as Categoria, 
            u.Abreviatura,
            COALESCE(SUM(ib.Existencias), 0) as Existencias_Totales,
            GROUP_CONCAT(DISTINCT b.Nombre SEPARATOR ', ') as Bodegas_Con_Existencia,
            -- Nueva columna: indica si se ha comprado al proveedor filtrado
            EXISTS(
                SELECT 1 
                FROM Detalle_Movimiento_Inventario dm
                INNER JOIN Movimientos_Inventario m ON dm.ID_Movimiento = m.ID_Movimiento
                WHERE dm.ID_Producto = p.ID_Producto 
                AND m.ID_Proveedor = %s
            ) as Comprado_Anteriormente
        FROM Productos p
        LEFT JOIN Categorias c ON p.Categoria_ID = c.ID_Categoria
        LEFT JOIN Unidades_Medida u ON p.Unidad_Medida = u.ID_Unidad
        LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto
        LEFT JOIN Bodegas b ON ib.ID_Bodega = b.ID_Bodega
        WHERE p.Estado = 'activo'
    """
    
    # Siempre pasamos el proveedor_filtro como parámetro, incluso si es None
    params = [proveedor_filtro if proveedor_filtro else None]
    
    # Completar consulta
    query_productos += """
        GROUP BY 
            p.ID_Producto,
            p.Descripcion,
            p.Unidad_Medida,
            p.Estado,
            p.Costo_Promedio,
            p.Precio_Venta,
            p.Categoria_ID,
            p.Fecha_Creacion,
            p.Usuario_Creador,
            p.Stock_minimo,
            c.Descripcion,
            u.Abreviatura
        ORDER BY 
            CASE WHEN %s IS NOT NULL THEN Comprado_Anteriormente END DESC,
            p.Descripcion
    """
    
    params.append(proveedor_filtro if proveedor_filtro else None)
    
    cur.execute(query_productos, params)
    productos = cur.fetchall()
    
    # Obtener proveedor actual para mostrar su nombre
    proveedor_actual_nombre = None
    proveedor_actual_estado = 'activo'
    if proveedor_filtro:
        cur.execute("SELECT Nombre, Estado FROM Proveedores WHERE ID_Proveedor = %s", (proveedor_filtro,))
        proveedor_actual = cur.fetchone()
        if proveedor_actual:
            proveedor_actual_nombre = proveedor_actual['Nombre']
            proveedor_actual_estado = proveedor_actual['Estado']
            if proveedor_actual['Estado'] != 'activo':
                flash('El proveedor seleccionado no está activo', 'warning')
    
    # Obtener proveedores activos
    cur.execute("SELECT * FROM Proveedores WHERE Estado = 'activo' ORDER BY Nombre")
    proveedores = cur.fetchall()
    
    # Obtener bodegas (bodega no tiene estado)
    cur.execute("SELECT * FROM Bodegas ORDER BY Nombre")
    bodegas = cur.fetchall()
    
    # Obtener tipos de movimiento de entrada (Catalogo_Movimientos NO tiene Estado)
    cur.execute("""
        SELECT * FROM Catalogo_Movimientos 
        WHERE Adicion = 'ENTRADA'
        ORDER BY Descripcion
    """)
    tipos_movimiento = cur.fetchall()
    
    cur.close()
    
    return render_template('inventario/entrada.html',
                         productos=productos,
                         proveedores=proveedores,
                         bodegas=bodegas,
                         tipos_movimiento=tipos_movimiento,
                         proveedor_filtro=proveedor_filtro,
                         proveedor_actual_nombre=proveedor_actual_nombre,
                         proveedor_actual_estado=proveedor_actual_estado)


# Ruta API para filtro AJAX
@app.route('/api/productos_por_proveedor/<int:proveedor_id>')
@admin_required
def api_productos_por_proveedor(proveedor_id):
    """API para obtener productos filtrados por proveedor (para AJAX)"""
    cur = mysql.connection.cursor()
    
    query = """
        SELECT 
            p.ID_Producto,
            p.Descripcion,
            p.Unidad_Medida,
            p.Estado,
            p.Costo_Promedio,
            p.Precio_Venta,
            p.Categoria_ID,
            p.Fecha_Creacion,
            p.Usuario_Creador,
            p.Stock_minimo,
            c.Descripcion as Categoria, 
            u.Abreviatura,
            COALESCE(SUM(ib.Existencias), 0) as Existencias_Totales,
            EXISTS(
                SELECT 1 
                FROM Detalle_Movimiento_Inventario dm
                INNER JOIN Movimientos_Inventario m ON dm.ID_Movimiento = m.ID_Movimiento
                WHERE dm.ID_Producto = p.ID_Producto 
                AND m.ID_Proveedor = %s
            ) as Comprado_Anteriormente
        FROM Productos p
        LEFT JOIN Categorias c ON p.Categoria_ID = c.ID_Categoria
        LEFT JOIN Unidades_Medida u ON p.Unidad_Medida = u.ID_Unidad
        LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto
        WHERE p.Estado = 'activo'
        GROUP BY 
            p.ID_Producto,
            p.Descripcion,
            p.Unidad_Medida,
            p.Estado,
            p.Costo_Promedio,
            p.Precio_Venta,
            p.Categoria_ID,
            p.Fecha_Creacion,
            p.Usuario_Creador,
            p.Stock_minimo,
            c.Descripcion,
            u.Abreviatura
        ORDER BY 
            Comprado_Anteriormente DESC,
            p.Descripcion
    """
    
    cur.execute(query, (proveedor_id,))
    productos = cur.fetchall()
    cur.close()
    
    return jsonify(productos)

@app.route('/inventario/salida', methods=['GET', 'POST'])
@admin_required
def inventario_salida():
    if request.method == 'POST':
        try:
            data = request.get_json()
            tipo_movimiento_id = data.get('tipo_movimiento_id')
            bodega_id = data.get('bodega_id')
            observacion = data.get('observacion', '')
            n_factura = data.get('n_factura', '')
            id_proveedor = data.get('id_proveedor')
            items = data.get('items', [])
            
            if not items:
                flash('No hay productos en el movimiento', 'warning')
                return jsonify({'success': False, 'message': 'No hay productos en el movimiento'}), 400
            
            cur = mysql.connection.cursor()
            
            # VERIFICAR que el tipo de movimiento es de salida
            cur.execute("SELECT Descripcion, Adicion FROM Catalogo_Movimientos WHERE ID_TipoMovimiento = %s", (tipo_movimiento_id,))
            tipo_movimiento = cur.fetchone()
            
            if not tipo_movimiento or tipo_movimiento['Adicion'] != 'SALIDA':
                flash('Tipo de movimiento no válido para salida', 'danger')
                return jsonify({'success': False, 'message': 'Tipo de movimiento no válido para salida'}), 400
            
            # Obtener nombre de bodega para mensajes
            cur.execute("SELECT Nombre FROM Bodegas WHERE ID_Bodega = %s", (bodega_id,))
            bodega_nombre = cur.fetchone()['Nombre']
            
            # Verificar stock disponible EN LA BODEGA ESPECÍFICA
            productos_sin_stock = []
            for item in items:
                cur.execute("""
                    SELECT COALESCE(ib.Existencias, 0) as Existencias_Bodega, 
                           p.Descripcion as Nombre_Producto
                    FROM Productos p
                    LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto AND ib.ID_Bodega = %s
                    WHERE p.ID_Producto = %s
                """, (bodega_id, item['producto_id']))
                
                inventario = cur.fetchone()
                stock_disponible = inventario['Existencias_Bodega'] if inventario else 0
                
                if not inventario or stock_disponible < item['cantidad']:
                    productos_sin_stock.append({
                        'producto': inventario['Nombre_Producto'] if inventario else f"ID {item['producto_id']}",
                        'disponible': stock_disponible,
                        'solicitado': item['cantidad']
                    })
            
            if productos_sin_stock:
                mensaje_error = "Stock insuficiente: " + ", ".join([
                    f"{p['producto']} (disp: {p['disponible']}, neces: {p['solicitado']})" 
                    for p in productos_sin_stock
                ])
                flash(mensaje_error, 'danger')
                return jsonify({'success': False, 'message': mensaje_error}), 400
            
            # Insertar movimiento CON FACTURA Y PROVEEDOR
            cur.execute("""
                INSERT INTO Movimientos_Inventario 
                (ID_TipoMovimiento, Observacion, ID_Bodega, Fecha, N_Factura, ID_Proveedor)
                VALUES (%s, %s, %s, CURDATE(), %s, %s)
            """, (tipo_movimiento_id, observacion, bodega_id, n_factura, id_proveedor))
            
            movimiento_id = cur.lastrowid
            
            # Insertar detalles y ACTUALIZAR INVENTARIO
            total_productos = 0
            total_costo = 0
            
            for item in items:
                producto_id = item['producto_id']
                cantidad = item['cantidad']
                
                # Obtener el costo promedio del producto para registrar en el detalle
                cur.execute("""
                    SELECT Costo_Promedio 
                    FROM Productos 
                    WHERE ID_Producto = %s
                """, (producto_id,))
                
                producto_info = cur.fetchone()
                costo = producto_info['Costo_Promedio'] if producto_info and producto_info['Costo_Promedio'] else 0
                costo_total = cantidad * costo
                total_costo += costo_total
                
                total_productos += cantidad
                
                # Insertar detalle
                cur.execute("""
                    INSERT INTO Detalle_Movimiento_Inventario 
                    (ID_Movimiento, ID_Producto, Cantidad, Costo, Costo_Total)
                    VALUES (%s, %s, %s, %s, %s)
                """, (movimiento_id, producto_id, cantidad, costo, costo_total))
                
                # ACTUALIZAR INVENTARIO EN BODEGA
                cur.execute("""
                    UPDATE Inventario_Bodega 
                    SET Existencias = Existencias - %s
                    WHERE ID_Bodega = %s AND ID_Producto = %s
                """, (cantidad, bodega_id, producto_id))
            
            mysql.connection.commit()
            cur.close()
            
            # Preparar mensaje con información de factura si existe
            mensaje_factura = f"Factura: {n_factura}" if n_factura else "Sin factura"
            flash(f'✅ Salida registrada! Movimiento #{movimiento_id} - {total_productos} unidades desde {bodega_nombre} | {mensaje_factura}', 'success')
            
            return jsonify({
                'success': True,
                'message': 'Salida de inventario registrada exitosamente',
                'movimiento_id': movimiento_id,
                'n_factura': n_factura,
                'total_productos': total_productos,
                'total_costo': total_costo
            })
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'❌ Error al registrar salida: {str(e)}', 'danger')
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # GET - Cargar datos para el formulario CON FILTRO POR PROVEEDOR
    cur = mysql.connection.cursor()
    
    # Obtener proveedor_id del query string si existe
    proveedor_filtro = request.args.get('proveedor_filtro', type=int)
    
    # Consulta base para productos con stock
    query_productos = """
        SELECT 
            p.ID_Producto, 
            p.Descripcion,
            COALESCE(SUM(ib.Existencias), 0) as Stock_Total,
            u.Abreviatura,
            c.Descripcion as Categoria,
            p.Costo_Promedio,
            p.Estado,
            p.Unidad_Medida,
            p.Stock_Minimo
        FROM Productos p
        LEFT JOIN Unidades_Medida u ON p.Unidad_Medida = u.ID_Unidad
        LEFT JOIN Categorias c ON p.Categoria_ID = c.ID_Categoria
        LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto
    """
    
    # Aplicar filtro por proveedor si se seleccionó
    params = ()
    if proveedor_filtro:
        query_productos += """
            WHERE p.ID_Producto IN (
                SELECT DISTINCT dm.ID_Producto 
                FROM detalle_movimiento_inventario dm
                INNER JOIN movimientos_inventario m ON dm.ID_Movimiento = m.ID_Movimiento
                WHERE m.ID_Proveedor = %s
            )
            AND p.Estado = 1
        """
        params = (proveedor_filtro,)
    else:
        query_productos += " WHERE p.Estado = 1"
    
    # Completar consulta
    query_productos += """
        GROUP BY 
            p.ID_Producto, 
            p.Descripcion, 
            u.Abreviatura, 
            c.Descripcion, 
            p.Costo_Promedio,
            p.Estado,
            p.Unidad_Medida,
            p.Stock_Minimo
        HAVING Stock_Total > 0
        ORDER BY p.Descripcion
    """
    
    cur.execute(query_productos, params)
    productos = cur.fetchall()
    
    # Obtener proveedor actual para mostrar su nombre
    proveedor_actual_nombre = None
    if proveedor_filtro:
        cur.execute("SELECT Nombre FROM Proveedores WHERE ID_Proveedor = %s", (proveedor_filtro,))
        proveedor_actual = cur.fetchone()
        proveedor_actual_nombre = proveedor_actual['Nombre'] if proveedor_actual else None
    
    cur.execute("SELECT * FROM Bodegas WHERE ID_Bodega > 0 ORDER BY Nombre")
    bodegas = cur.fetchall()
    
    cur.execute("SELECT * FROM Catalogo_Movimientos WHERE Adicion = 'SALIDA' ORDER BY Descripcion")
    tipos_movimiento = cur.fetchall()
    
    # Obtener proveedores (pueden ser clientes/destinatarios para salidas)
    cur.execute("SELECT * FROM Proveedores ORDER BY Nombre")
    proveedores = cur.fetchall()
    
    cur.close()
    
    return render_template('inventario/salida.html',
                         productos=productos,
                         bodegas=bodegas,
                         tipos_movimiento=tipos_movimiento,
                         proveedores=proveedores,
                         proveedor_filtro=proveedor_filtro,
                         proveedor_actual_nombre=proveedor_actual_nombre)

@app.route('/inventario/detalle/<int:id>')
@admin_required
def inventario_detalle(id):
    try:
        cur = mysql.connection.cursor()
        
        # Obtener movimiento
        cur.execute("""
            SELECT mi.*, cm.Descripcion as TipoMovimiento, cm.Adicion, cm.Letra,
                   p.Nombre as Proveedor, b.Nombre as Bodega
            FROM Movimientos_Inventario mi
            INNER JOIN Catalogo_Movimientos cm ON mi.ID_TipoMovimiento = cm.ID_TipoMovimiento
            LEFT JOIN Proveedores p ON mi.ID_Proveedor = p.ID_Proveedor
            LEFT JOIN Bodegas b ON mi.ID_Bodega = b.ID_Bodega
            WHERE mi.ID_Movimiento = %s
        """, (id,))
        movimiento = cur.fetchone()
        
        if not movimiento:
            flash('❌ Movimiento no encontrado', 'danger')
            return redirect(url_for('inventario'))
        
        # Obtener detalles
        cur.execute("""
            SELECT dmi.*, p.Descripcion as Producto, u.Abreviatura
            FROM Detalle_Movimiento_Inventario dmi
            INNER JOIN Productos p ON dmi.ID_Producto = p.ID_Producto
            LEFT JOIN Unidades_Medida u ON p.Unidad_Medida = u.ID_Unidad
            WHERE dmi.ID_Movimiento = %s
            ORDER BY p.Descripcion  -- Agregar ordenamiento
        """, (id,))
        detalles = cur.fetchall()
        
        cur.close()
        
        return render_template('inventario/detalle.html', 
                               movimiento=movimiento, 
                               detalles=detalles)
    
    except Exception as e:
        if 'cur' in locals():
            cur.close()
        flash('❌ Error al cargar el detalle del movimiento', 'danger')
        return redirect(url_for('inventario'))

@app.route('/inventario/reportes')
@admin_required
def reportes():
    cur = mysql.connection.cursor()
    
    try:
        # Productos con más movimientos - CORREGIDO
        cur.execute("""
            SELECT p.Descripcion, 
                   SUM(CASE WHEN cm.Adicion = 'ENTRADA' THEN dmi.Cantidad ELSE 0 END) as Entradas,
                   SUM(CASE WHEN cm.Adicion = 'SALIDA' THEN dmi.Cantidad ELSE 0 END) as Salidas,
                   COALESCE(SUM(ib.Existencias), 0) as Existencias
            FROM Detalle_Movimiento_Inventario dmi
            INNER JOIN Productos p ON dmi.ID_Producto = p.ID_Producto
            INNER JOIN Movimientos_Inventario mi ON dmi.ID_Movimiento = mi.ID_Movimiento
            INNER JOIN Catalogo_Movimientos cm ON mi.ID_TipoMovimiento = cm.ID_TipoMovimiento
            LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto
            WHERE mi.Fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY p.ID_Producto, p.Descripcion
            ORDER BY (Entradas + Salidas) DESC
            LIMIT 10
        """)
        productos_movimientos = cur.fetchall()
        
        # Movimientos por tipo (esta consulta está bien)
        cur.execute("""
            SELECT cm.Descripcion, COUNT(*) as Total, cm.Letra, cm.Adicion
            FROM Movimientos_Inventario mi
            INNER JOIN Catalogo_Movimientos cm ON mi.ID_TipoMovimiento = cm.ID_TipoMovimiento
            WHERE mi.Fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY cm.ID_TipoMovimiento, cm.Descripcion, cm.Letra, cm.Adicion
            ORDER BY Total DESC
        """)
        movimientos_tipo = cur.fetchall()
        
        # Valor del inventario - CORREGIDO
        cur.execute("""
            SELECT SUM(COALESCE(ib.Existencias, 0) * p.Costo_Promedio) as ValorTotal
            FROM Productos p
            LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto
            WHERE p.Estado = 1
        """)
        valor_inventario = cur.fetchone()['ValorTotal'] or 0
        
        # Productos sin movimiento - CORREGIDO
        cur.execute("""
            SELECT p.Descripcion, 
                   COALESCE(SUM(ib.Existencias), 0) as Existencias, 
                   p.Fecha_Creacion
            FROM Productos p
            LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto
            WHERE p.Estado = 1
            AND NOT EXISTS (
                SELECT 1 FROM Detalle_Movimiento_Inventario dmi
                INNER JOIN Movimientos_Inventario mi ON dmi.ID_Movimiento = mi.ID_Movimiento
                WHERE dmi.ID_Producto = p.ID_Producto
                AND mi.Fecha >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
            )
            GROUP BY p.ID_Producto, p.Descripcion, p.Fecha_Creacion
            ORDER BY p.Fecha_Creacion DESC
            LIMIT 10
        """)
        productos_sin_movimiento = cur.fetchall()
        
        # Productos con stock bajo - CORREGIDO
        cur.execute("""
            SELECT p.Descripcion, 
                   COALESCE(SUM(ib.Existencias), 0) as Existencias, 
                   p.Stock_Minimo,
                   (COALESCE(SUM(ib.Existencias), 0) - p.Stock_Minimo) as Diferencia
            FROM Productos p
            LEFT JOIN Inventario_Bodega ib ON p.ID_Producto = ib.ID_Producto
            WHERE p.Estado = 1
            GROUP BY p.ID_Producto, p.Descripcion, p.Stock_Minimo
            HAVING COALESCE(SUM(ib.Existencias), 0) <= p.Stock_Minimo
            ORDER BY Diferencia ASC
            LIMIT 10
        """)
        productos_stock_bajo = cur.fetchall()
        
        cur.close()
        
    except Exception as e:
        flash(f'❌ Error al generar reportes: {str(e)}', 'danger')
        # Inicializar variables vacías en caso de error
        productos_movimientos = []
        movimientos_tipo = []
        valor_inventario = 0
        productos_sin_movimiento = []
        productos_stock_bajo = []
    
    return render_template('inventario/reportes.html',
                         productos_movimientos=productos_movimientos,
                         movimientos_tipo=movimientos_tipo,
                         valor_inventario=valor_inventario,
                         productos_sin_movimiento=productos_sin_movimiento,
                         productos_stock_bajo=productos_stock_bajo)

if __name__ == '__main__':
    app.run(debug=True)
