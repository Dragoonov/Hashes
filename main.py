from abc import ABC, abstractmethod
from enum import Enum


class Dict(ABC):
    MAX_PER_LIST = 20

    def __init__(self):
        self.__size = 16
        self.__data = []

    @abstractmethod
    def find(self, key):
        pass

    @abstractmethod
    def insert(self, element):
        pass

    @abstractmethod
    def delete(self, key):
        pass

    def __find_index(self, key):
        h = hash(key) % len(self.__data)
        for i in range(len(self.__data[h])):
            if self.__key(self.__data[h][i]) == key:
                return h, i
        return h, -1

    def __key(self, element):
        return element

    def __delitem__(self, key):
        self.delete(key)

    def __getitem__(self, item):
        return self.find(item)

    def __len__(self):
        return self.__size

    def __contains__(self, item):
        return self.find(item) is not None


class ChainDict(Dict):

    def __init__(self):
        super().__init__()
        for i in range(self.__size):
            self.__data[i] = []

    def find(self, key):
        h, i = self.__find_index(key)
        if i == -1:
            return None
        return self.__data[h][i]

    def insert(self, element):
        h, i = self.__find_index(self.__key(element))
        if i == -1:
            self.__data[h].append(element)
            self.__size += 1
            if self.__size > len(self.__data) * self.MAX_PER_LIST:
                self.__data = self.__new_data(2 * len(self.__data))
        else:
            self.__data[h][i] = element

    def delete(self, key):
        h, i = self.__find_index(key)
        if i != -1:
            self.__data[h][i] = self.__data[h].pop()
            self.__size -= 1
            if (len(self.__data)) > 1 and 4 * self.__size < len(self.__data) * self.MAX_PER_LIST:
                self.__data = self.__new_data(len(self.__data) / 2)

    def __new_data(self, new_size):
        r = []
        for i in range(new_size):
            r[i] = []
        for tab in self.__data:
            for e in tab:
                r[hash(self.__key(e)) % len(r)].append(e)
        return r


class LinearDict(Dict):
    N = 8
    D = 10

    def __init__(self):
        super().__init__()
        for i in range(self.__size):
            self.__data[i] = LinearDict.Special.EMPTY

    def __empty(self, i):
        return self.__data[i] == LinearDict.Special.EMPTY

    def __deleted(self, i):
        return self.__data[i] == LinearDict.Special.DELETED

    def __scan_for(self, key):
        first_index = hash(key) % len(self.__data)
        step = 1
        first_deleted_index = -1
        i = first_index
        while not self.__empty(i):
            if self.__deleted(i):
                if first_deleted_index == -1:
                    first_deleted_index = i
            elif self.__key(self.__data[i]) == key:
                return i
            i = (i + step) % len(self.__data)
            if i == first_index:
                return first_deleted_index
        if first_deleted_index != -1:
            return first_deleted_index
        return i

    def find(self, key):
        i = self.__scan_for(key)
        if i == -1 or self.__empty(i) or self.__deleted(i):
            return None
        return self.__data[i]

    def insert(self, element):
        i = self.__scan_for(self.__key(element))
        if self.__empty(i) or self.__deleted(i):
            self.__data[i] = element
            self.__size += 1
            if self.__size * self.D > len(self.__data) * self.N:
                self.__data = self.__new_data(2 * len(self.__data))
        else:
            self.__data[i] = element

    def delete(self, key):
        i = self.__scan_for(key)
        if not self.__empty(i) and not self.__deleted(i):
            self.__data[i] = LinearDict.Special.DELETED
            self.__size -= 1
            if len(self.__data) > 1 and self.__size * 4 * self.D < len(self.__data) * self.N:
                self.__data = self.__new_data(len(self.__data)/2)

    def __new_data(self, new_size):
        r = []
        for i in range(new_size):
            r[i] = LinearDict.Special.EMPTY
        for src_i in range(len(self.__data)):
            if not self.__empty(src_i) and not self.__deleted(src_i):
                key = self.__key(self.__data[src_i])
                i = hash(key) % len(r)
                step = 1
                while r[i] != LinearDict.Special.EMPTY:
                    i = (i + step) % len(r)
                r[i] = self.__data[src_i]
        return r

    class Special(Enum):
        EMPTY = -1
        DELETED = -2
