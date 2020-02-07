class Trie:
    def __init__(self, letter=None):
        self.letter = letter
        self._video = set()
        self._children = []

    def add(self, key, value):
        if len(key) == 0:
            self._video.add(value)
            return
        for child in self._children:
            if child.letter == key[0]:
                child.add_video(key[1:], value)
                return
        missing_node = Trie(key[0])
        self._children.append(missing_node)
        missing_node.add(key[1:], value)

    def find(self, key):
        if len(key) == 0:
            return self._video
        for child in self._children:
            if child.letter == key[0]:
                return child.find(key[1:])
        return set()
