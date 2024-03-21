import pickle
from flask import Flask, render_template, request
from flask import jsonify

app = Flask(__name__, template_folder='template')

class TNode:
    def __init__(self):
        self.is_end = False 
        self.children = [None] * 26

class Trie:
    def __init__(self):
        self.root = TNode()

    def insertNode(self, word):
        current_node = self.root 
        for character in word:
            idx = ord(character) - ord('a')
            if current_node.children[idx] is None:
                current_node.children[idx] = TNode()
            current_node = current_node.children[idx]
        current_node.is_end = True 

    def searchWord(self, word):
        current_node = self.root
        for character in word:
            idx = ord(character) - ord('a')
            if current_node.children[idx] is None:
                return False
            current_node = current_node.children[idx]
        return current_node.is_end

    def _dfs_print_words(self, node, prefix, result):
        if node.is_end:
            result.append(prefix)
        for i, child in enumerate(node.children):
            if child:
                self._dfs_print_words(child, prefix + chr(i + ord('a')), result)
    
    def _dfs(self, node, prefix, result):
        # If the current node is the end of a word, append it to the result
        if node.is_end:
            result.append(prefix)
        
        # Traverse through all children of the current node
        for i, child in enumerate(node.children):
            if child:
                # Recursively call _dfs for each child node
                self._dfs(child, prefix + chr(i + ord('a')), result)

    def print_word_with_prefix(self, prefix):
        current_node = self.root
        
        # Traverse to the node representing the prefix
        for char in prefix:
            idx = ord(char) - ord('a')
            if not current_node.children[idx]:
                # Prefix doesn't exist in the trie
                return []
    
            current_node = current_node.children[idx]

        # Now, current_node points to the node representing the prefix
        # We'll perform a depth-first search to print all words with this prefix
        result = []
        self._dfs(current_node, prefix, result)
        return result 

    def get_all_words(self):
        result=[]
        self._dfs_print_words(self.root, '', result)
        return result

def save_trie(trie, filename):
    with open(filename, 'wb') as file:
        pickle.dump(trie.root, file)

def load_trie(filename):
    with open(filename, 'rb') as file:
        root = pickle.load(file)
        trie = Trie()
        trie.root = root
        return trie

# Load trie from file or create a new one if the file doesn't exist
trie_filename = 'trie_data.pkl'
try:
    worddict = load_trie(trie_filename)
except FileNotFoundError:
    worddict = Trie()
    dictionary_file = 'Dictionary_Words_github.txt'
    with open(dictionary_file, 'r') as file:
        for line in file:
            word = line.strip().lower()  # Convert to lowercase and remove leading/trailing spaces
            worddict.insertNode(word)
    save_trie(worddict, trie_filename)  # Save trie data to file


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save_data():
    if request.method == 'POST':
        word = request.form['word'].lower()
        worddict.insertNode(word)
        save_trie(worddict, trie_filename)  # Save trie data to file
        message = '{} saved to trie'.format(word)
    else:
        message = ''
    return render_template('index.html', message=message)

@app.route('/search', methods=['POST'])
def search_word():
    if request.method == 'POST':
        search_word = request.form['search_word'].strip().lower()  # Remove leading/trailing spaces
        if not search_word:
            # If search word is empty, return to the index without performing the search
            return render_template('index.html')
        
        search_result = worddict.searchWord(search_word)
        return render_template('index.html', search_result=search_result, search_word=search_word)

@app.route('/getallwords', methods=['POST'])
def get_all_words():
    all_words = worddict.get_all_words()
    return render_template('index.html', all_words=all_words)

from flask import jsonify

@app.route('/getprefixes', methods=['POST'])
def get_prefixes():
    prefix = request.form['suggestions_prefix'].lower()
    suggestions = worddict.print_word_with_prefix(prefix)
    return {'suggestions': suggestions}


if __name__ == '__main__':
    app.run(debug=True)
