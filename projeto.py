import sqlite3  # Banco de dados SQLite
import tkinter as tk  # Interface gráfica
from tkinter import messagebox
from tkinter import ttk  # Treeview para exibição dos dados em tabela

# Conectar ao banco de dados
def conectar():
    return sqlite3.connect('meu_projeto.db')

# Criar a tabela no banco de dados
def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER,
            peso REAL,
            altura REAL,
            sexo TEXT,
            objetivo TEXT,
            atividade TEXT,
            calorias REAL
        )
    ''')
    conn.commit()
    conn.close()

# Calcular a TMB
def calcular_tmb(peso, altura, idade, sexo, fator_atividade, objetivo):
    if sexo == 'Homem':
        tmb = 88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * idade)
    else:
        tmb = 447.6 + (9.25 * peso) + (3.10 * altura) - (4.33 * idade)

    necessidade_calorica = tmb * fator_atividade
    necessidade_calorica = int(necessidade_calorica)
    
    if objetivo == 'Perder Peso':
        necessidade_calorica -= 400
    elif objetivo == 'Ganhar Peso':
        necessidade_calorica += 300
    
    return necessidade_calorica

# Criar a interface gráfica principal
root = tk.Tk()
root.geometry('1000x500')
root.title('Cadastro de Dados')

# Campos de entrada
tk.Label(root, text='Nome:').grid(row=0, column=0)
input_nome = tk.Entry(root, width=50)
input_nome.grid(row=0, column=1, columnspan=2)

tk.Label(root, text='Idade:').grid(row=1, column=0)
input_idade = tk.Entry(root, width=5)
input_idade.grid(row=1, column=1)

tk.Label(root, text='Peso (kg):').grid(row=1, column=2)
input_peso = tk.Entry(root, width=5)
input_peso.grid(row=1, column=3)

tk.Label(root, text='Altura (cm):').grid(row=1, column=4)
input_altura = tk.Entry(root, width=5)
input_altura.grid(row=1, column=5)

# Seleção de Sexo
tk.Label(root, text="Sexo:").grid(row=2, column=0)
sexo_var = tk.StringVar(value='Homem')
tk.Radiobutton(root, text='Homem', variable=sexo_var, value='Homem').grid(row=2, column=1)
tk.Radiobutton(root, text='Mulher', variable=sexo_var, value='Mulher').grid(row=2, column=2)

# Seleção de Objetivo
tk.Label(root, text="Objetivo:").grid(row=3, column=0)
objetivo_var = tk.StringVar(value='Manter Peso')
tk.OptionMenu(root, objetivo_var, 'Manter Peso', 'Perder Peso', 'Ganhar Peso').grid(row=3, column=1)

# Seleção de Nível de Atividade Física
tk.Label(root, text="Atividade Física:").grid(row=3, column=2)
atividade_var = tk.StringVar(value='Sedentário')
tk.OptionMenu(root, atividade_var, 'Sedentário', 'Moderado', 'Ativo').grid(row=3, column=3)

# Criar a tabela para exibição dos dados
columns = ('ID', 'Nome', 'Idade', 'Peso', 'Altura', 'Sexo', 'Objetivo', 'Atividade', 'Calorias')
tree = ttk.Treeview(root, columns=columns, show='headings', height=10)
tree.grid(row=5, column=0, columnspan=7, pady=10)

# Criar cabeçalhos das colunas
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)

# Função para exibir os dados
def mostrar():
    tree.delete(*tree.get_children())
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, idade, peso, altura, sexo, objetivo, atividade, calorias FROM dado ORDER BY id')
    dados = cursor.fetchall()
    conn.close()
    for dado in dados:
        tree.insert("", "end", values=dado)

# Função para salvar os dados no banco
def salvar():
    nome = input_nome.get()
    idade = input_idade.get()
    peso = input_peso.get()
    altura = input_altura.get()
    sexo = sexo_var.get()
    objetivo = objetivo_var.get()
    atividade = atividade_var.get()

    if not nome or not idade or not peso or not altura:
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos!")
        return

    try:
        idade = int(idade)
        peso = float(peso)
        altura = float(altura)
    except ValueError:
        messagebox.showerror("Erro", "Idade, peso e altura devem ser valores numéricos!")
        return

    fator_atividade = {'Sedentário': 1.2, 'Moderado': 1.55, 'Ativo': 1.9}.get(atividade, 1.2)
    calorias = calcular_tmb(peso, altura, idade, sexo, fator_atividade, objetivo)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO dado (nome, idade, peso, altura, sexo, objetivo, atividade, calorias)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome, idade, peso, altura, sexo, objetivo, atividade, calorias))

    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
    mostrar()

# Função para apagar um registro
def apagar():
    selecao = tree.selection()
    if not selecao:
        messagebox.showwarning("Erro", "Selecione um registro para apagar!")
        return
    
    id_registro = tree.item(selecao)['values'][0]
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM dado WHERE id=?', (id_registro,))
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Sucesso", "Registro apagado!")
    mostrar()

# Função para editar um registro
def editar():
    selecao = tree.selection()
    if not selecao:
        messagebox.showwarning("Erro", "Selecione um registro para editar!")
        return

    id_registro = tree.item(selecao)['values'][0]

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dado WHERE id=?', (id_registro,))
    registro = cursor.fetchone()
    conn.close()

    if registro:
        input_nome.delete(0, tk.END)
        input_nome.insert(0, registro[1])
        input_idade.delete(0, tk.END)
        input_idade.insert(0, registro[2])
        input_peso.delete(0, tk.END)
        input_peso.insert(0, registro[3])
        input_altura.delete(0, tk.END)
        input_altura.insert(0, registro[4])
        sexo_var.set(registro[5])
        objetivo_var.set(registro[6])
        atividade_var.set(registro[7])

# Criar botões
tk.Button(root, text='Salvar', command=salvar).grid(row=4, column=0)
tk.Button(root, text='Editar', command=editar).grid(row=4, column=1)
tk.Button(root, text='Apagar', command=apagar).grid(row=4, column=2)

# Inicializar banco e exibir dados
criar_tabela()
mostrar()

root.mainloop()
