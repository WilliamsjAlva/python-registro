import re
import json
import datetime
import smtplib
from email.message import EmailMessage
import pywhatkit as pwk
import os

# correo (por cierto, casi subo la contraseña en el repositorio de github,
# algo que recorde mientras estaba creando el repositorio)
correoDeEnvio = ""
contrasenaCorreo = ""
nombreArchivo = "usuarios.txt"

# archivo
def cargarDatos():
    if not os.path.exists(nombreArchivo):
        with open(nombreArchivo, "w") as file:
            json.dump([], file)
    with open(nombreArchivo, "r") as file:
        return json.load(file)

# guardar archivo
def guardarDatos(usuarios):
    with open(nombreArchivo, "w") as file:
        json.dump(usuarios, file, indent=4)

# regex
def validarDato(dato, tipo):
    patrones = {
        "nombre": r"^[A-Za-zñÑaeiouAEIOU]{2,30}$",
        "apellido": r"^[A-Za-zñÑaeiouAEIOU]{2,30}$",
        "fecha": r"^\d{2}-\d{2}-\d{4}$",
        "pais": r"^[A-Za-z\s]{2,30}$",
        "correo": r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$",
        "telefono": r"^\+?\d{7,15}$"
    }
    return re.match(patrones[tipo], dato)

# mayor de edad o no
def calcularEdad(fechaNacimiento):
    fechaNacimiento = datetime.datetime.strptime(fechaNacimiento, "%d-%m-%Y")
    hoy = datetime.datetime.now()
    return hoy.year - fechaNacimiento.year - ((hoy.month, hoy.day) < (fechaNacimiento.month, fechaNacimiento.day))

# mensaje de bienvenida whatsapp
def enviarMensajeWhatsapp(nombre, numeroTelefono):
    mensaje = f"Hola {nombre}! Bienvenido a nuestro sistema de registro"
    pwk.sendwhatmsg_instantly(numeroTelefono, mensaje, 15, tab_close=True)
    print("Mensaje de whatsApp enviado correctamente al usuario")

# enviar correo de bienvenida
def enviarCorreo(nombre, correoDestino):
    mensaje = EmailMessage()
    mensaje.set_content(f"Hola {nombre}! bienvenido a nuestro sistema de registro")
    mensaje["Subject"] = "Bienvenida"
    mensaje["From"] = correoDeEnvio
    mensaje["To"] = correoDestino


    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(correoDeEnvio, contrasenaCorreo)
        smtp.send_message(mensaje)
    print("Correo de bienvenida enviado correctamente")

# registrar usuario
def registrarUsuario():
    usuarios = cargarDatos()
    nombre = input("Nombre: ")
    if not validarDato(nombre, "nombre"):
        print("Error: nombre invalido")
        return
    apellido = input("Apellido: ")
    if not validarDato(apellido, "apellido"):
        print("Error: apellido invalido.")
        return
    fechaNacimiento = input("Fecha de nacimiento (DD-MM-AAAA): ")
    if not validarDato(fechaNacimiento, "fecha"):
        print("Error: fecha de nacimiento invalida")
        return
    edad = calcularEdad(fechaNacimiento)
    if edad < 18:
        print("Usuario menor de 18 años. Redirigiendo al menu principal")
        return
    pais = input("Pais: ")
    if not validarDato(pais, "pais"):
        print("Error: pais invalido")
        return
    correo = input("Correo electronico: ")
    if not validarDato(correo, "correo"):
        print("Error: correo electronico invalido")
        return
    telefono = input("Numero de telefono (incluir + y codigo de pais): ")
    if not validarDato(telefono, "telefono"):
        print("Error: numero de telefono invalido")
        return

    usuario = {
        "nombre": nombre,
        "apellido": apellido,
        "fechaNacimiento": fechaNacimiento,
        "edad": edad,
        "pais": pais,
        "correo": correo,
        "telefono": telefono
    }
    usuarios.append(usuario)
    guardarDatos(usuarios)
    print("Usuario registrado exitosamente.")
    enviarMensajeWhatsapp(nombre, telefono)
    enviarCorreo(nombre, correo)

# ver usuarios
def verUsuarios():
    usuarios = cargarDatos()
    if not usuarios:
        print("No hay usuarios registrados")
        return
    for i, usuario in enumerate(usuarios, start=1):
        print(f"\nUsuario {i}:")
        for key, value in usuario.items():
            print(f"{key.capitalize()}: {value}")

# modificar usuario
def modificarUsuario():
    usuarios = cargarDatos()
    if not usuarios:
        print("No hay usuarios registrados")
        return
    verUsuarios()
    indice = int(input("\nIngrese el numero de usuario que desea modificar: ")) - 1
    if 0 <= indice < len(usuarios):
        usuario = usuarios[indice]
        print("\nDeje el campo en blanco si no desea modificarlo.")
        for campo in usuario.keys():
            nuevoValor = input(f"{campo.capitalize()} (actual: {usuario[campo]}): ")
            if nuevoValor:
                if campo == "fechaNacimiento":
                    if validarDato(nuevoValor, "fecha"):
                        usuario[campo] = nuevoValor
                        usuario["edad"] = calcularEdad(nuevoValor)
                    else:
                        print("Fecha invalida. Manteniendo valor actual.")
                elif validarDato(nuevoValor, campo):
                    usuario[campo] = nuevoValor
                else:
                    print(f"{campo.capitalize()} invalido. Manteniendo valor actual.")
        guardarDatos(usuarios)
        print("Usuario actualizado exitosamente")
    else:
        print("Numero de usuario invalido")

# eliminar usuario
def eliminarUsuario():
    usuarios = cargarDatos()
    if not usuarios:
        print("No hay usuarios registrados")
        return
    verUsuarios()
    indice = int(input("\nIngrese el numero de usuario que desea eliminar: ")) - 1
    if 0 <= indice < len(usuarios):
        confirmacion = input(f"Esta seguro de que desea eliminar al usuario {usuarios[indice]['nombre']}? (s/n): ").lower()
        if confirmacion == "s":
            usuarios.pop(indice)
            guardarDatos(usuarios)
            print("Usuario eliminado exitosamente")
        else:
            print("Eliminacion cancelada")
    else:
        print("Numero de usuario invalido")

# menu
def menu():
    while True:
        print("\nMenu de registro (ingrese un numero para acceder a una opcion):")
        print("R. Registrar usuario")
        print("V. Ver usuarios registrados")
        print("M. Modificar usuario")
        print("E. Eliminar usuario")
        print("S. Salir")
        
        opcion = input("Seleccione una opcion: ")
        if opcion == "R":
            registrarUsuario()
        elif opcion == "V":
            verUsuarios()
        elif opcion == "M":
            modificarUsuario()
        elif opcion == "M":
            eliminarUsuario()
        elif opcion == "S":
            print("Saliendo del programa")
            break
        else:
            print("Opcion invalida. Intente de nuevo")

# ejecutar menu
menu()
