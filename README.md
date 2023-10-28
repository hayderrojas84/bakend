# Requisitos del Proyecto

Asegúrate de tener instalada la versión adecuada de Python y los paquetes necesarios para ejecutar este proyecto.

## Python

Este proyecto requiere Python 3.9.13. Puedes descargar Python desde [el sitio oficial de Python](https://www.python.org/downloads/release).

## Paquetes de Python

Asegúrate de que tienes los siguientes paquetes de Python y sus versiones correspondientes instalados:

- asgiref: 3.7.2
- Django: 4.2.6
- mysqlclient: 2.2.0
- pip: 23.3.1
- PyJWT: 2.8.0
- setuptools: 58.1.0
- sqlparse: 0.4.4
- typing_extensions: 4.8.0
- tzdata: 2023.3

Puedes instalar estos paquetes utilizando `pip`. Por ejemplo, para instalar Django, puedes ejecutar el siguiente comando:

```bash
pip install Django==4.2.6
```

# Documentación de Endpoints

A continuación se describen los endpoints disponibles en este proyecto:

## Login

- **Ruta:** `/auth/login`
- **Método:** POST
- **Descripción:** Ruta de autenticación.

## Usuarios

### Listar Usuarios
- **Ruta:** `/users/`
- **Método:** GET
- **Descripción:** Obtiene una lista de todos los usuarios.

### Crear Usuario
- **Ruta:** `/users/create/`
- **Método:** POST
- **Descripción:** Crea un nuevo usuario.

### Obtener Usuario por ID
- **Ruta:** `/users/<int:user_id>/`
- **Método:** GET
- **Descripción:** Obtiene los detalles de un usuario por su ID.

### Actualizar Usuario
- **Ruta:** `/users/<int:user_id>/update/`
- **Método:** PUT
- **Descripción:** Actualiza la información de un usuario existente.

### Eliminar Usuario
- **Ruta:** `/users/<int:user_id>/delete/`
- **Método:** DELETE
- **Descripción:** Elimina un usuario por su ID.

## Roles

### Listar Roles
- **Ruta:** `/roles/`
- **Método:** GET
- **Descripción:** Obtiene una lista de todos los roles.

### Crear Rol
- **Ruta:** `/roles/create/`
- **Método:** POST
- **Descripción:** Crea un nuevo rol.

### Obtener Rol por ID
- **Ruta:** `/roles/<int:role_id>/`
- **Método:** GET
- **Descripción:** Obtiene los detalles de un rol por su ID.

### Actualizar Rol
- **Ruta:** `/roles/<int:role_id>/update/`
- **Método:** PUT
- **Descripción:** Actualiza la información de un rol existente.

### Eliminar Rol
- **Ruta:** `/roles/<int:role_id>/delete/`
- **Método:** DELETE
- **Descripción:** Elimina un rol por su ID.

## Máquinas

### Listar Máquinas
- **Ruta:** `/machines/`
- **Método:** GET
- **Descripción:** Obtiene una lista de todas las máquinas.

### Crear Máquina
- **Ruta:** `/machines/create/`
- **Método:** POST
- **Descripción:** Crea una nueva máquina.

### Obtener Máquina por ID
- **Ruta:** `/machines/<int:machine_id>/`
- **Método:** GET
- **Descripción:** Obtiene los detalles de una máquina por su ID.

### Actualizar Máquina
- **Ruta:** `/machines/<int:machine_id>/update/`
- **Método:** PUT
- **Descripción:** Actualiza la información de una máquina existente.

### Eliminar Máquina
- **Ruta:** `/machines/<int:machine_id>/delete/`
- **Método:** DELETE
- **Descripción:** Elimina una máquina por su ID.

## Ejercicios

### Listar Ejercicios
- **Ruta:** `/exercises/`
- **Método:** GET
- **Descripción:** Obtiene una lista de todos los ejercicios.

### Crear Ejercicio
- **Ruta:** `/exercises/create/`
- **Método:** POST
- **Descripción:** Crea un nuevo ejercicio.

### Obtener Ejercicio por ID
- **Ruta:** `/exercises/<int:exercise_id>/`
- **Método:** GET
- **Descripción:** Obtiene los detalles de un ejercicio por su ID.

### Actualizar Ejercicio
- **Ruta:** `/exercises/<int:exercise_id>/update/`
- **Método:** PUT
- **Descripción:** Actualiza la información de un ejercicio existente.

### Eliminar Ejercicio
- **Ruta:** `/exercises/<int:exercise_id>/delete/`
- **Método:** DELETE
- **Descripción:** Elimina un ejercicio por su ID.

## Rutinas

### Listar Rutinas
- **Ruta:** `/routines/`
- **Método:** GET
- **Descripción:** Obtiene una lista de todas las rutinas.

### Crear Rutina
- **Ruta:** `/routines/create/`
- **Método:** POST
- **Descripción:** Crea una nueva rutina.

### Obtener Rutina por ID
- **Ruta:** `/routines/<int:routine_id>/`
- **Método:** GET
- **Descripción:** Obtiene los detalles de una rutina por su ID.

### Actualizar Rutina
- **Ruta:** `/routines/<int:routine_id>/update/`
- **Método:** PUT
- **Descripción:** Actualiza la información de una rutina existente.

### Eliminar Rutina
- **Ruta:** `/routines/<int:routine_id>/delete/`
- **Método:** DELETE
- **Descripción:** Elimina una rutina por su ID.

## Horarios de Rutinas

### Listar Horarios de Rutinas
- **Ruta:** `/routineSchedules/`
- **Método:** GET
- **Descripción:** Obtiene una lista de todos los horarios de rutinas.

### Crear Horario de Rutina
- **Ruta:** `/routineSchedules/create/`
- **Método:** POST
- **Descripción:** Crea un nuevo horario de rutina.

### Obtener Horario de Rutina por ID
- **Ruta:** `/routineSchedules/<int:routine_id>/`
- **Método:** GET
- **Descripción:** Obtiene los detalles de un horario de rutina por su ID.

### Actualizar Horario de Rutina
- **Ruta:** `/routineSchedules/<int:routine_id>/update/`
- **Método:** PUT
- **Descripción:** Actualiza la información de un horario de rutina existente.

### Eliminar Horario de Rutina
- **Ruta:** `/routineSchedules/<int:routine_id>/delete/`
- **Método:** DELETE
- **Descripción:** Elimina un horario de rutina por su ID.