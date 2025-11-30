import tkinter as tk
from tkinter import messagebox, ttk
import mariadb
import bcrypt
from tkcalendar import DateEntry
from datetime import datetime

# --- Configuración de la Base de Datos ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '', # ¡Cambia esto a con la contraseña de acceso a MariaDB!
    'database': 'crud_db'
}

# --- Funciones de la Base de Datos ---
def get_db_connection():
    try:
        conn = mariadb.connect(**DB_CONFIG)
        return conn
    except mariadb.Error as e:
        messagebox.showerror("Error de Conexión a DB", f"Error al conectar a MariaDB: {e}")
        return None

def create_table():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tipo_id VARCHAR(255) NOT NULL,
                    nombre VARCHAR(255) NOT NULL,
                    apellido VARCHAR(255) NOT NULL,
                    direccion VARCHAR(255) NOT NULL,
                    telefono VARCHAR(255) NOT NULL,
                    fecha_nacimiento DATE NOT NULL,
                    correo VARCHAR(255) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                );
            """)
            conn.commit()
            print("Tabla 'users' creada o ya existe.")
        except mariadb.Error as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            cursor.close()
            conn.close()

def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def insert_user(tipo_id, nombre, apellido, direccion, telefono, fecha_nacimiento, correo, password):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO users (tipo_id, nombre, apellido, direccion, telefono, fecha_nacimiento, correo, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (tipo_id, nombre, apellido, direccion, telefono, fecha_nacimiento,correo, hashed_password)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario insertado correctamente.")
            return True
        except mariadb.Error as e:
            messagebox.showerror("Error", f"Error al insertar usuario: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

def get_users():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # cursor.execute("SELECT id, nombre, fecha_nacimiento FROM users")
            cursor.execute("SELECT ID, tipo_id, nombre, apellido, direccion, telefono, fecha_nacimiento, correo FROM users")
            users = cursor.fetchall()
            return users
        except mariadb.Error as e:
            messagebox.showerror("Error", f"Error al obtener usuarios: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, nombre, fecha_nacimiento, password_hash FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            return user
        except mariadb.Error as e:
            messagebox.showerror("Error", f"Error al obtener usuario por ID: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

def update_user(user_id, nombre, fecha_nacimiento, password=None):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if password:
                hashed_password = hash_password(password)
                cursor.execute(
                    "UPDATE users SET nombre = ?, fecha_nacimiento = ?, password_hash = ? WHERE id = ?",
                    (nombre, fecha_nacimiento, hashed_password, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET nombre = ?, fecha_nacimiento = ? WHERE id = ?",
                    (nombre, fecha_nacimiento, user_id)
                )
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario actualizado correctamente.")
            return True
        except mariadb.Error as e:
            messagebox.showerror("Error", f"Error al actualizar usuario: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

def delete_user(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
            return True
        except mariadb.Error as e:
            messagebox.showerror("Error", f"Error al eliminar usuario: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

# --- Interfaz Gráfica con Tkinter ---
class UserApp:
    def __init__(self, master):
        self.master = master
        master.title("CRUD de Usuarios")
        master.geometry("900x800")

        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        # Frame para entrada de datos
        input_frame = tk.LabelFrame(self.master, text="Gestión de Usuarios", padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(input_frame, text="ID (Solo para actualizar/eliminar):").grid(row=0, column=0, pady=5, sticky="w")
        self.id_entry = tk.Entry(input_frame)
        self.id_entry.grid(row=0, column=1, pady=5, sticky="ew")

        tk.Label(input_frame, text="Tipo Id:").grid(row=1, column=0, pady=5, sticky="w")
        self.tipo_id_entry = tk.Entry(input_frame)
        self.tipo_id_entry.grid(row=1, column=1, pady=5, sticky="ew")

        tk.Label(input_frame, text="Nombre:").grid(row=2, column=0, pady=5, sticky="w")
        self.nombre_entry = tk.Entry(input_frame)
        self.nombre_entry.grid(row=2, column=1, pady=5, sticky="ew")

        tk.Label(input_frame, text="Apellido:").grid(row=3, column=0, pady=5, sticky="w")
        self.apellido_entry = tk.Entry(input_frame)
        self.apellido_entry.grid(row=3, column=1, pady=5, sticky="ew")

        tk.Label(input_frame, text="Direccion:").grid(row=4, column=0, pady=5, sticky="w")
        self.direccion_entry = tk.Entry(input_frame)
        self.direccion_entry.grid(row=4, column=1, pady=5, sticky="ew")

        tk.Label(input_frame, text="Num.Telef.:").grid(row=5, column=0, pady=5, sticky="w")
        self.telefono_entry = tk.Entry(input_frame)
        self.telefono_entry.grid(row=5, column=1, pady=5, sticky="ew")

        tk.Label(input_frame, text="Fecha de Nacimiento:").grid(row=6, column=0, pady=5, sticky="w")
        self.fecha_nacimiento_entry = DateEntry(input_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.fecha_nacimiento_entry.grid(row=6, column=1, pady=5, sticky="ew")

        tk.Label(input_frame, text="Correo:").grid(row=7, column=0, pady=5, sticky="w")
        self.correo_entry = tk.Entry(input_frame)
        self.correo_entry.grid(row=7, column=1, pady=5, sticky="ew")

        tk.Label(input_frame, text="Contraseña:").grid(row=8, column=0, pady=5, sticky="w")
        self.password_entry = tk.Entry(input_frame, show="*") # Oculta la contraseña
        self.password_entry.grid(row=8, column=1, pady=5, sticky="ew")

        # Botones de acción
        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Crear Usuario", command=self.add_user).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Actualizar Usuario", command=self.update_selected_user).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Eliminar Usuario", command=self.delete_selected_user).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Limpiar Campos", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        # --- Botón para salir ---
        tk.Button(button_frame, text="Salir", command=self.master.destroy, bg="red", fg="white").pack(side=tk.RIGHT, padx=15)


        # Treeview para mostrar usuarios
        self.tree = ttk.Treeview(self.master, columns=("ID","Tipo_iD","Nombre", "Apellido", "Direccion","Telefono", "FechaNac","Correo"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Tipo_iD", text="Tipo_iD")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Apellido", text="Apellido")
        self.tree.heading("Direccion", text="Direccion")
        self.tree.heading("Telefono", text="Telefono")
        self.tree.heading("FechaNac", text="Fecha de Nacimiento")
        self.tree.heading("Correo", text="Correo")
        

        # Configuración de columnas (ancho)
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Tipo_iD", width=60)
        self.tree.column("Nombre", width=130)
        self.tree.column("Apellido", width=130)
        self.tree.column("Direccion", width=130)
        self.tree.column("Telefono", width=120)
        self.tree.column("FechaNac", width=150, anchor="center")
        self.tree.column("Correo", width=100)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        users = get_users()
        for user in users:
            self.tree.insert("", "end", values=user)

    def add_user(self):
        tipo_id = self.tipo_id_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        apellido = self.apellido_entry.get().strip()
        direccion = self.direccion_entry.get().strip()
        telefono = self.telefono_entry.get().strip()
        fecha_nacimiento_str = self.fecha_nacimiento_entry.get_date().strftime('%Y-%m-%d')
        correo = self.correo_entry.get().strip()
        password = self.password_entry.get()

        if not tipo_id or not nombre or not apellido or not direccion or not telefono or not fecha_nacimiento_str or not correo or not password:
            messagebox.showwarning("Campos Requeridos", "Por favor, complete todos los campos.")
            return

        if insert_user(tipo_id, nombre, apellido, direccion, telefono, fecha_nacimiento_str, correo, password):
            self.load_users()
            self.clear_fields()

    def update_selected_user(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione un usuario de la tabla para actualizar.")
            return

        user_id = self.tree.item(selected_item)['values'][0]
        nombre = self.nombre_entry.get().strip()
        fecha_nacimiento_str = self.fecha_nacimiento_entry.get_date().strftime('%Y-%m-%d')
        password = self.password_entry.get() # Obtener la nueva contraseña (si se ingresó)

        if not nombre or not fecha_nacimiento_str:
            messagebox.showwarning("Campos Requeridos", "Por favor, complete Nombre y Fecha de Nacimiento.")
            return

        if password:
            if update_user(user_id, nombre, fecha_nacimiento_str, password):
                self.load_users()
                self.clear_fields()
        else:
            if update_user(user_id, nombre, fecha_nacimiento_str):
                self.load_users()
                self.clear_fields()

    def delete_selected_user(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione un usuario de la tabla para eliminar.")
            return

        user_id = self.tree.item(selected_item)['values'][0]
        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar al usuario con ID {user_id}?"):
            if delete_user(user_id):
                self.load_users()
                self.clear_fields()

    def on_tree_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, values[0])

            self.tipo_id_entry.delete(0, tk.END)
            self.tipo_id_entry.insert(0, values[1])

            self.nombre_entry.delete(0, tk.END)
            self.nombre_entry.insert(0, values[2])

            self.apellido_entry.delete(0, tk.END)
            self.apellido_entry.insert(0, values[3])

            self.direccion_entry.delete(0, tk.END)
            self.direccion_entry.insert(0, values[4])

            self.telefono_entry.delete(0, tk.END)
            self.telefono_entry.insert(0, values[5])
            
            date_obj = datetime.strptime(str(values[6]), '%Y-%m-%d').date()
            self.fecha_nacimiento_entry.set_date(date_obj)

            self.correo_entry.delete(0, tk.END)
            self.correo_entry.insert(0, values[7])

            self.password_entry.delete(0, tk.END)
            
            self.id_entry.config(state='disabled')
        else:
            self.clear_fields()
            self.id_entry.config(state='normal')

    def clear_fields(self):
        self.id_entry.config(state='normal')
        self.id_entry.delete(0, tk.END)
        self.tipo_id_entry.delete(0, tk.END)
        self.nombre_entry.delete(0, tk.END)
        self.apellido_entry.delete(0, tk.END)
        self.direccion_entry.delete(0, tk.END)
        self.telefono_entry.delete(0, tk.END)
        self.fecha_nacimiento_entry.set_date(datetime.now().date())
        self.correo_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

# --- Ejecutar la Aplicación ---
if __name__ == "__main__":
    create_table()

    root = tk.Tk()
    app = UserApp(root)
    root.mainloop()