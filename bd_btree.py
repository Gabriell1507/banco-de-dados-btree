import random
import time
import tracemalloc
from faker import Faker

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

        z.keys = y.keys[t:(2 * t) - 1]
        y.keys = y.keys[0:t - 1]

        if not y.leaf:
            z.children = y.children[t:(2 * t)]
            y.children = y.children[0:t]

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
        node, idx = self.search(key)
        if node:
            node.keys.pop(idx)
            return True
        return False

    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        print(f"Nível {level} Chaves:", node.keys)
        for child in node.children:
            self.print_tree(child, level + 1)

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

def measure_performance(tree, operation, data, key=None, new_key=None):
    tracemalloc.start()
    start_time = time.time()
    
    if operation == "INSERT":
        for item in data:
            tree.insert(item)
    elif operation == "SELECT":
        for item in data:
            tree.search(item)
    elif operation == "UPDATE":
        for item in data:
            tree.update(item, new_key)
    elif operation == "DELETE":
        for item in data:
            tree.delete(item)
    
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    execution_time = end_time - start_time
    return format_time(execution_time), current, peak

def main():
    b_tree = BTree(3)
    
    while True:
        print("\nEscolha uma operação CRUD:")
        print("1. Inserir")
        print("2. Selecionar")
        print("3. Atualizar")
        print("4. Deletar")
        print("5. Avaliar Desempenho")
        print("6. Sair")
        
        choice = int(input("Digite o número da operação: "))
        
        if choice == 1:
            num_records = int(input("Quantos dados deseja inserir? "))
            data = generate_random_data(num_records)
            formatted_time, current, peak = measure_performance(b_tree, "INSERT", data)
            print(f"{num_records} registros inseridos em {formatted_time}")
        elif choice == 2:
            print("Exibindo todos os dados:")
            b_tree.print_tree()
        elif choice == 3:
            old_key = input("Digite o nome atual: ")
            new_key = fake.unique.name()
            if b_tree.update(old_key, new_key):
                print(f"Registro {old_key} atualizado para {new_key}")
            else:
                print(f"Registro {old_key} não encontrado")
        elif choice == 4:
            key = input("Digite o nome a ser deletado: ")
            if b_tree.delete(key):
                print(f"Registro {key} deletado")
            else:
                print(f"Registro {key} não encontrado")
        elif choice == 5:
            sizes = [100, 1000, 10000]
            operations = ["INSERT", "SELECT", "UPDATE", "DELETE"]
            for size in sizes:
                data = generate_random_data(size)
                for operation in operations:
                    print(f"\nAvaliando desempenho para {operation} com {size} registros:")
                    if operation == "UPDATE":
                        formatted_time, current, peak = measure_performance(b_tree, operation, data, new_key=fake.unique.name())
                    else:
                        formatted_time, current, peak = measure_performance(b_tree, operation, data)
                    print(f"Tempo de execução: {formatted_time}")
                    print(f"Memória atual: {current / 1024:.2f} KB; Pico de memória: {peak / 1024:.2f} KB")
        elif choice == 6:
            break
        else:
            print("Escolha inválida. Tente novamente.")

if __name__ == "__main__":
    main()
