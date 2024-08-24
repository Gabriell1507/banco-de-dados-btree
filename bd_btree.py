import random
import time
import tracemalloc
from faker import Faker
import matplotlib.pyplot as plt

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
    return execution_time, current, peak

def plot_performance(sizes, times, operations, filename="performance.png"):
    plt.figure(figsize=(12, 8))
    
    for operation in operations:
        plt.plot(sizes, times[operation], marker='o', label=operation)
    
    plt.xlabel('Número de registros')
    plt.ylabel('Tempo de execução (segundos)')
    plt.title('Desempenho das operações CRUD em B-Tree')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()

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
            execution_time, current, peak = measure_performance(b_tree, "INSERT", data)
            print(f"Tempo para inserção: {format_time(execution_time)}")
            print(f"Memória utilizada: {current / 10**6:.2f}MB; Memória máxima: {peak / 10**6:.2f}MB")
        
        elif choice == 2:
            search_key = input("Digite a chave para buscar: ")
            node, index = b_tree.search(search_key)
            if node:
                print(f"Chave {search_key} encontrada no nó com chaves: {node.keys}")
            else:
                print(f"Chave {search_key} não encontrada.")
        
        elif choice == 3:
            old_key = input("Digite a chave antiga: ")
            new_key = input("Digite a nova chave: ")
            if b_tree.update(old_key, new_key):
                print(f"Chave {old_key} atualizada para {new_key}.")
            else:
                print(f"Chave {old_key} não encontrada.")
        
        elif choice == 4:
            delete_key = input("Digite a chave para deletar: ")
            b_tree.delete(delete_key)
            print(f"Chave {delete_key} deletada.")
        
        elif choice == 5:
            sizes = [10**i for i in range(1, 6)]
            times = {"INSERT": [], "SELECT": [], "UPDATE": [], "DELETE": []}
            memory_usage = {"INSERT": [], "SELECT": [], "UPDATE": [], "DELETE": []}
            
            for size in sizes:
                print(f"\nAvaliando desempenho com {size} registros:")
                data = generate_random_data(size)
                
                for operation in ["INSERT", "SELECT", "UPDATE", "DELETE"]:
                    key = data[0] if operation != "INSERT" else None
                    new_key = "NovoNome" if operation == "UPDATE" else None
                    execution_time, current, peak = measure_performance(b_tree, operation, data, key, new_key)
                    times[operation].append(execution_time)
                    memory_usage[operation].append(peak / 10**6)
                    print(f"{operation}: Tempo: {format_time(execution_time)}, Memória máxima: {peak / 10**6:.2f}MB")
            
            plot_performance(sizes, times, ["INSERT", "SELECT", "UPDATE", "DELETE"])
            print("Gráfico de desempenho gerado: performance.png")
            
            # Plotar o uso de memória
            plt.figure(figsize=(12, 8))
            for operation in ["INSERT", "SELECT", "UPDATE", "DELETE"]:
                plt.plot(sizes, memory_usage[operation], marker='o', label=operation)
            
            plt.xlabel('Número de registros')
            plt.ylabel('Memória máxima (MB)')
            plt.title('Uso de memória das operações CRUD em B-Tree')
            plt.legend()
            plt.grid(True)
            plt.savefig("memory_usage.png")
            plt.close()
            print("Gráfico de uso de memória gerado: memory_usage.png")
        
        elif choice == 6:
            print("Saindo...")
            break
        
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
