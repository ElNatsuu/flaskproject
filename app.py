from flask import Flask #Importacion de libreria Flask
from flask import render_template, redirect, request, Response, session, url_for,flash
from flask_mysqldb import MySQL, MySQLdb #lIBRERIAS DE BASE DE DATOS

#Enlace con el directorio de archivos
app = Flask(__name__,template_folder='template')

#Variable global para indicar si el inicio de sesión se realizó correctamente
sesion_iniciada = False
correo = ""

#Conexion a la base de datos
app.config['MYSQL_HOST']='34.29.193.58'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='1234'
app.config['MYSQL_DB']='LOGIN'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)

#Agregar el acceso a las paginas web
@app.route('/')
def home():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM restaurantes")
    restaurantes=cur.fetchall()
    #Convertir los datos a diccionario
    #insertObject=[]
    #columnNames=[column[0] for column in cur.description]
    #for record in restaurantes:
        #insertObject.append(dict(zip(columnNames,record)))
    cur.close()

    if sesion_iniciada==False:
        return render_template('index2.html',restaurantes=restaurantes) #Me envia al archivo indicado
    else:
        return render_template('index2.html',restaurantes=restaurantes,usuario=correo) #Me envia al archivo indicado


#Registro de datos con funcion (ruta para duadarlos)
@app.route('/restaurante',methods=["GET","POST"])
def addRestaurante():
    if sesion_iniciada==True:
        nombre=request.form['txtNombreR']
        tipo=request.form['txtTipoR']
        direccion=request.form['txtDireccionR']
        telefono=request.form['txtTelefonoR']

        if nombre and tipo and direccion and telefono:
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO restaurantes (nombre,tipo,direccion,telefono) VALUES(%s,%s,%s,%s)",(nombre,tipo,direccion,telefono))
            mysql.connection.commit()
        return redirect(url_for('home')) #Refrescar pagina
    else:
        flash('Necesitas iniciar sesion para realizar un nuevo registro', 'danger')
        return redirect(url_for('home'))  # Refrescar página

#Eliminar restaurante
@app.route('/delete/<string:idrestaurante>')
def delete(idrestaurante):
    if sesion_iniciada==True:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM restaurantes WHERE idrestaurante=%s", (idrestaurante,))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('home'))  # Refrescar página
    else:
        flash('Necesitas iniciar sesion para eliminar un registro', 'danger')
        return redirect(url_for('home'))  # Refrescar página
   

#Editar restaurante
@app.route('/edit/<string:idrestaurante>', methods=["GET", "POST"])
def update(idrestaurante):
    if sesion_iniciada==True:
        if request.method == "POST":
            nombre = request.form['txtNombreR']
            tipo = request.form['txtTipoR']
            direccion = request.form['txtDireccionR']
            telefono = request.form['txtTelefonoR']

            if nombre and tipo and direccion and telefono:
                cur = mysql.connection.cursor()
                cur.execute("UPDATE restaurantes SET nombre=%s, tipo=%s, direccion=%s, telefono=%s WHERE idrestaurante=%s",
                            (nombre, tipo, direccion, telefono, idrestaurante))
                mysql.connection.commit()
                cur.close()

        return redirect(url_for('home'))  # Refrescar página
    else:
        flash('Necesitas iniciar sesion para actualizar un registro', 'danger')
        return redirect(url_for('home'))  # Refrescar página

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/iniciosesion')
def iniciosesion():
    if sesion_iniciada==True:
        return redirect(url_for('home'))  
    else:
        return render_template('index.html')


#FUNCION DE LOGIN (llamada al metodo, tipo de envio)
@app.route('/acceso-login',methods=["GET","POST"])
def login():
    global sesion_iniciada  # Declarar que estamos utilizando la variable global
    global correo

    # Recuperación de la información del formulario
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword':
        # Almacenamiento en variables
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        # Ejecución de BD y consulta SQL
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE correo=%s AND password=%s', (_correo, _password))
        account = cur.fetchone()  # Guardando el resultado

        # Respuesta a la consulta del inicio de sesión con lo guardado
        if account:
            session['logueado'] = True  # Guardado de sesión
            session['id'] = account['id']  # Guarda id de sesión
            session['id_rol'] = account['id_rol']  # Recupera el tipo de rol

            if session['id_rol'] in (1, 2):  # Comprueba si el rol es válido
                sesion_iniciada = True  # Marca la variable global como verdadera
                correo=_correo
                return redirect(url_for('home'))
        else:
            return render_template('index.html', mensaje="Usuario incorrecto")  # Si no coincide con ningún registro, no se mueve a otro HTML

#Funcion de registro que me dirige a el HTML de registro
@app.route('/registro')
def registro():
    if sesion_iniciada==True:
        return redirect(url_for('home')) 
    else:
        return render_template('registro.html')

#Funcion de registro que me dirige a el HTML de registro
@app.route('/cerrar-sesion')
def logout():
    global sesion_iniciada # Marca la variable global como verdadera
    global correo

    sesion_iniciada = False  # Marca la variable global como verdadera
    correo=""

    return redirect(url_for('home'))
    

#Funcion de crear nuevo registro
@app.route('/crear-registro',methods=["GET","POST"])
def crear_registro():
    correo=request.form['txtCorreo']
    username=request.form['txtUsername']
    password=request.form['txtPassword']

    if correo!="" and username!="" and password!="":
        #Ejecucion de BD y consulta SQL
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (username,correo,password,id_rol) VALUES(%s,%s,%s,'2')",(username,correo,password))
        mysql.connection.commit()

        return render_template("index.html", mensaje2="usuario registrado exitosamente, ya puedes iniciar sesion:)")
    else:
        return render_template("registro.html",mensaje3="Ingresa todos los campos para realizar el registro:(")

#----------------------


#------LISTAR USAURIOS---------
@app.route('/listar',methods=["GET","POST"])
def listar():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM restaurantes")
    restaurantes=cur.fetchall()
    cur.close()

    return render_template("listar_usuarios.html",restaurantes=restaurantes)


#------------------------------





if __name__ == '__main__':
    app.secret_key="fabian_pc"
    app.run(debug=True,host='0.0.0.0',port=5000,threaded=True)




