from abc import ABC, abstractmethod
from enum import Enum
import random
import matplotlib.pyplot as plt

comparisons_amount_for_element = 0


class Dict(ABC):
    MAX_PER_LIST = 1000

    def __init__(self):
        self._size = 16
        self._data = []

    @abstractmethod
    def find(self, key):
        pass

    @abstractmethod
    def insert(self, element):
        pass

    @abstractmethod
    def delete(self, key):
        pass

    def _key(self, element):
        return element

    def __delitem__(self, key):
        self.delete(key)

    def __getitem__(self, item):
        return self.find(item)

    def __len__(self):
        return self._size

    def __contains__(self, item):
        return self.find(item) is not None


class ChainDict(Dict):

    def __init__(self):
        super().__init__()
        for i in range(self._size):
            self._data.append([])

    def __find_index(self, key):
        global comparisons_amount_for_element
        h = hash(key) % len(self._data)
        for i in range(len(self._data[h])):
            comparisons_amount_for_element += 1
            if self._key(self._data[h][i]) == key:
                return h, i
        return h, -1

    def find(self, key):
        global comparisons_amount_for_element
        comparisons_amount_for_element = 0
        h, i = self.__find_index(key)
        if i == -1:
            return None
        return self._data[h][i]

    def insert(self, element):
        h, i = self.__find_index(self._key(element))
        if i == -1:
            self._data[h].append(element)
            self._size += 1
            if self._size > len(self._data) * self.MAX_PER_LIST:
                self._data = self.__new_data(2 * len(self._data))
        else:
            self._data[h][i] = element

    def delete(self, key):
        h, i = self.__find_index(key)
        if i != -1:
            self._data[h][i] = self._data[h][len(self._data[h]) - 1]
            self._data[h].pop()
            self._size -= 1
            if (len(self._data)) > 1 and 4 * self._size < len(self._data) * self.MAX_PER_LIST:
                self._data = self.__new_data(int(len(self._data) / 2))

    def __new_data(self, new_size):
        r = []
        for i in range(new_size):
            r.append([])
        for tab in self._data:
            for e in tab:
                r[hash(self._key(e)) % len(r)].append(e)
        return r


class LinearDict(Dict):
    N = 500
    D = 1000

    def __init__(self):
        super().__init__()
        for i in range(self._size):
            self._data.append(LinearDict.Special.EMPTY)

    def __empty(self, i):
        global comparisons_amount_for_element
        comparisons_amount_for_element += 1
        return self._data[i] == LinearDict.Special.EMPTY

    def __deleted(self, i):
        return self._data[i] == LinearDict.Special.DELETED

    def __scan_for(self, key):
        global comparisons_amount_for_element
        first_index = hash(key) % len(self._data)
        step = 1
        first_deleted_index = -1
        i = first_index
        while not self.__empty(i):
            comparisons_amount_for_element += 1
            if self.__deleted(i):
                comparisons_amount_for_element += 1
                if first_deleted_index == -1:
                    first_deleted_index = i
            elif self._key(self._data[i]) == key:
                comparisons_amount_for_element += 1
                return i
            comparisons_amount_for_element += 1
            i = (i + step) % len(self._data)
            comparisons_amount_for_element += 1
            if i == first_index:
                return first_deleted_index
        comparisons_amount_for_element += 1
        if first_deleted_index != -1:
            return first_deleted_index
        return i

    def find(self, key):
        global comparisons_amount_for_element
        comparisons_amount_for_element = 0
        i = self.__scan_for(key)
        comparisons_amount_for_element += 1
        if i == -1 or self.__empty(i) or self.__deleted(i):
            return None
        return self._data[i]

    def insert(self, element):
        i = self.__scan_for(self._key(element))
        if self.__empty(i) or self.__deleted(i):
            self._data[i] = element
            self._size += 1
            if self._size * self.D > len(self._data) * self.N:
                self._data = self.__new_data(2 * len(self._data))
        else:
            self._data[i] = element

    def delete(self, key):
        i = self.__scan_for(key)
        if not self.__empty(i) and not self.__deleted(i):
            self._data[i] = LinearDict.Special.DELETED
            self._size -= 1
            if len(self._data) > 1 and self._size * 4 * self.D < len(self._data) * self.N:
                self._data = self.__new_data(len(self._data) / 2)

    def __new_data(self, new_size):
        r = []
        for i in range(new_size):
            r.append(LinearDict.Special.EMPTY)
        for src_i in range(len(self._data)):
            if not self.__empty(src_i) and not self.__deleted(src_i):
                key = self._key(self._data[src_i])
                i = hash(key) % len(r)
                step = 1
                while r[i] != LinearDict.Special.EMPTY:
                    i = (i + step) % len(r)
                r[i] = self._data[src_i]
        return r

    class Special(Enum):
        EMPTY = -1
        DELETED = -2


chainDict = ChainDict()
linearDict = LinearDict()

chaindata = [[], []]
lineardata= [[], []]

for i in range(10000):
    chainDict.insert(i)
    linearDict.insert(i)
    if i % 100 == 0 and i != 0:
        average = []
        for j in range(100):
            chainDict.find(random.randrange(0, i))
            average.append(comparisons_amount_for_element)
        chaindata[0].append(len(chainDict))
        chaindata[1].append(int(sum(average)/len(average)))
        average = []
        for j in range(100):
            linearDict.find(-1)
            average.append(comparisons_amount_for_element)
        lineardata[0].append(len(linearDict))
        lineardata[1].append(int(sum(average)/len(average)))

plt.plot(chaindata[0], chaindata[1], label="Lancuchowy")
plt.plot(lineardata[0], lineardata[1], label="Liniowy")
plt.xlabel = "Wielkosc slownika"
plt.ylabel('Liczba porownan')
plt.title('Porownanie lancuchowego i liniowego')
plt.legend()
plt.show()
