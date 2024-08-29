import random
import time
import tracemalloc
from faker import Faker
import matplotlib.pyplot as plt
import json

fake = Faker()

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t
        self.leaf = leaf
        self.keys = []
        self.children = []

    def __str__(self):
        return f"Chaves: {self.keys}, Filhos: {len(self.children)}"

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(t, leaf=True)
        self.t = t

    def insert(self, key):
        root = self.root
        if len(root.keys) == (2 * self.t) - 1:
            temp = BTreeNode(self.t)
            self.root = temp
            temp.children.append(root)
            self._split_child(temp, 0)
            self._insert_non_full(temp, key)
        else:
            self._insert_non_full(root, key)

    def _split_child(self, parent, i):
        t = self.t
        y = parent.children[i]
        z = BTreeNode(t, leaf=y.leaf)

        parent.children.insert(i + 1, z)
        parent.keys.insert(i, y.keys[t - 1])

        z.keys = y.keys[t:]
        y.keys = y.keys[:t - 1]

        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]

    def _insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.t) - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)

    def search(self, key, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return node, i
        if node.leaf:
            return None, -1
        return self.search(key, node.children[i])

    def update(self, old_key, new_key):
        node, i = self.search(old_key)
        if node is not None:
            node.keys[i] = new_key
            return True
        return False

    def delete(self, key, node=None):
        if node is None:
            node = self.root

        self._delete_from_node(node, key)
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    def _delete_from_node(self, node, key):
        t = self.t
        if node.leaf:
            if key in node.keys:
                node.keys.remove(key)
                return True
            return False
        
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            if len(node.children[i].keys) >= t:
                pred = self._get_predecessor(node.children[i])
                node.keys[i] = pred
                self._delete_from_node(node.children[i], pred)
            elif len(node.children[i + 1].keys) >= t:
                succ = self._get_successor(node.children[i + 1])
                node.keys[i] = succ
                self._delete_from_node(node.children[i + 1], succ)
            else:
                self._merge_children(node, i)
                self._delete_from_node(node.children[i], key)
        else:
            if i < len(node.children) and len(node.children[i].keys) == t - 1:
                self._fill_child(node, i)
            if i >= len(node.children):
                i = len(node.children) - 1
            self._delete_from_node(node.children[i], key)

    def _get_predecessor(self, node):
        while not node.leaf:
            node = node.children[-1]
        return node.keys[-1]

    def _get_successor(self, node):
        while not node.leaf:
            node = node.children[0]
        return node.keys[0]

    def _merge_children(self, parent, i):
        t = self.t
        y = parent.children[i]
        z = parent.children[i + 1]
        y.keys.append(parent.keys[i])
        y.keys.extend(z.keys)
        if not y.leaf:
            y.children.extend(z.children)
        parent.keys.pop(i)
        parent.children.pop(i + 1)

    def _fill_child(self, parent, i):
        t = self.t
        if i > 0 and len(parent.children[i - 1].keys) >= t:
            self._borrow_from_prev(parent, i)
        elif i < len(parent.children) - 1 and len(parent.children[i + 1].keys) >= t:
            self._borrow_from_next(parent, i)
        else:
            if i < len(parent.children) - 1:
                self._merge_children(parent, i)
            else:
                self._merge_children(parent, i - 1)

    def _borrow_from_prev(self, parent, i):
        t = self.t
        child = parent.children[i]
        sibling = parent.children[i - 1]

        child.keys.insert(0, parent.keys[i - 1])
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())
        parent.keys[i - 1] = sibling.keys.pop()

    def _borrow_from_next(self, parent, i):
        t = self.t
        child = parent.children[i]
        sibling = parent.children[i + 1]

        child.keys.append(parent.keys[i])
        if not child.leaf:
            child.children.append(sibling.children.pop(0))
        parent.keys[i] = sibling.keys.pop(0)

    def print_tree(self, node=None, level=0, indent="    "):
        if node is None:
            node = self.root
        print(f"{indent * level}Nível {level} Chaves: {node.keys}")
        for i, child in enumerate(node.children):
            self.print_tree(child, level + 1, indent)

    def inorder_traversal(self, node=None, result=None):
        if node is None:
            node = self.root
        if result is None:
            result = []
        i = 0
        while i < len(node.keys):
            if not node.leaf:
                self.inorder_traversal(node.children[i], result)
            result.append(node.keys[i])
            i += 1
        if not node.leaf:
            self.inorder_traversal(node.children[i], result)
        return result

class Table:
    def __init__(self, name, btree_order):
        self.name = name
        self.btree = BTree(btree_order)

    def insert(self, key):
        self.btree.insert(key)

    def search(self, key):
        return self.btree.search(key)

    def update(self, old_key, new_key):
        return self.btree.update(old_key, new_key)

    def delete(self, key):
        self.btree.delete(key)

    def print_tree(self):
        self.btree.print_tree()

    def inorder_traversal(self):
        return self.btree.inorder_traversal()

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.inorder_traversal(), f)
        print(f"Dados salvos em {filename}")

class Database:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, btree_order):
        if name not in self.tables:
            self.tables[name] = Table(name, btree_order)
            print(f"Tabela '{name}' criada com sucesso.")
        else:
            print(f"Tabela '{name}' já existe.")

    def get_table(self, name):
        return self.tables.get(name, None)

def generate_random_data(n):
    return [fake.unique.name() for _ in range(n)]

def format_time(seconds):
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.2f} microssegundos"
    elif seconds < 1:
        return f"{seconds * 1_000:.2f} milissegundos"
    elif seconds < 60:
        return f"{seconds:.2f} segundos"
    else:
        return f"{seconds / 60:.2f} minutos"

def measure_performance(table, operation, data, key=None, new_key=None):
    tracemalloc.start()
    start_time = time.time()
    
    if operation == "INSERT":
        for item in data:
            table.insert(item)
    elif operation == "SELECT":
        for item in data:
            table.search(item)
    elif operation == "UPDATE":
        for item in data:
            table.update(item, new_key)
    elif operation == "DELETE":
        for item in data:
            table.delete(item)
    
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    execution_time = end_time - start_time
    return execution_time, current, peak

def plot_performance(sizes, times, operations):
    plt.figure(figsize=(10, 6))
    for operation in operations:
        plt.plot(sizes, times[operation], label=operation)
    plt.xlabel('Número de Registros')
    plt.ylabel('Tempo (segundos)')
    plt.title('Desempenho das Operações CRUD')
    plt.legend()
    plt.grid(True)
    plt.savefig('performance.png')
    plt.show()

def main():
    db = Database()
    
    # Cria uma tabela padrão para avaliação de desempenho
    default_table_name = "default_table"
    default_btree_order = 3
    db.create_table(default_table_name, default_btree_order)
    
    while True:
        print("\nEscolha uma operação:")
        print("1. Criar Tabela")
        print("2. Inserir em Tabela")
        print("3. Selecionar (Exibir a árvore)")
        print("4. Atualizar em Tabela")
        print("5. Deletar de Tabela")
        print("6. Avaliar Desempenho")
        print("7. Salvar dados da tabela em arquivo")
        print("8. Sair")
        
        choice = int(input("Digite o número da operação: "))
        
        if choice == 1:
            table_name = input("Digite o nome da tabela: ")
            btree_order = int(input("Digite a ordem da Árvore B: "))
            db.create_table(table_name, btree_order)
        
        elif choice in [2, 3, 4, 5]:
            table_name = input("Digite o nome da tabela: ")
            table = db.get_table(table_name)
            if table is None:
                print("Tabela não encontrada.")
                continue

            if choice == 2:
                insert_choice = input("Deseja inserir nomes gerados automaticamente pelo Faker? (s/n): ")
                if insert_choice.lower() == 's':
                    n = int(input("Quantos registros deseja inserir? "))
                    data = generate_random_data(n)
                    for item in data:
                        table.insert(item)
                    print(f"{n} registros inseridos com sucesso.")
                else:
                    while True:
                        name = input("Digite o nome para inserir (ou 'sair' para parar): ")
                        if name.lower() == 'sair':
                            break
                        table.insert(name)
                        print(f"Nome '{name}' inserido com sucesso.")
                        
            elif choice == 3:
                print("Estrutura da Árvore B da tabela:")
                table.print_tree()
                print("Dados ordenados na tabela:")
                print(table.inorder_traversal())
                
            elif choice == 4:
                old_key = input("Digite o valor antigo: ")
                new_key = input("Digite o novo valor: ")
                if table.update(old_key, new_key):
                    print(f"Registro {old_key} atualizado para {new_key}.")
                else:
                    print("Registro não encontrado.")
                    
            elif choice == 5:
                key = input("Digite o valor a ser deletado: ")
                table.delete(key)
                print(f"Registro {key} deletado.")
        
        elif choice == 6:
            # Usa a tabela padrão para avaliação de desempenho
            table = db.get_table(default_table_name)
            sizes = [100, 500, 1000, 5000, 10000]
            times = {"INSERT": [], "SELECT": [], "UPDATE": [], "DELETE": []}
            operations = ["INSERT", "SELECT", "UPDATE", "DELETE"]

            for size in sizes:
                data = generate_random_data(size)
                new_data = generate_random_data(size)
                
                for operation in operations:
                    if operation == "INSERT":
                        execution_time, current, peak = measure_performance(table, operation, data)
                    elif operation == "SELECT":
                        execution_time, current, peak = measure_performance(table, operation, data)
                    elif operation == "UPDATE":
                        execution_time, current, peak = measure_performance(table, operation, data, new_key=new_data[0])
                    elif operation == "DELETE":
                        execution_time, current, peak = measure_performance(table, operation, data)
                    
                    times[operation].append(execution_time)
                    print(f"Operação {operation} para {size} registros: {format_time(execution_time)} - Memória usada: {current / 1024:.2f} KB, Pico: {peak / 1024:.2f} KB")

            plot_performance(sizes, times, operations)
            print("Avaliação de desempenho concluída. Gráfico salvo como 'performance.png'.")
        
        elif choice == 7:
            table_name = input("Digite o nome da tabela: ")
            table = db.get_table(table_name)
            if table is None:
                print("Tabela não encontrada.")
            else:
                filename = input("Digite o nome do arquivo para salvar os dados (com extensão .json): ")
                table.save_to_file(filename)
        
        elif choice == 8:
            print("Saindo...")
            break
        else:
            print("Escolha inválida. Tente novamente.")

if __name__ == "__main__":
    main()