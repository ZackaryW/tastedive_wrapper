from dataclasses import dataclass
from typing import overload
import typing

from tastediveW.auth.request import makeRequest

class TasteListMeta(type):
    _instances = {}
    _list_titles = {}


    def __call__(cls, *args, **kwargs):
        id = kwargs.get("id", None)
        if id is None:
            raise ValueError("id must be set")

        if id not in cls._instances:
            cls._instances[id] = super().__call__(*args, **kwargs)

        if id not in cls._list_titles:
            cls._list_titles[id] = []

        return cls._instances[id]


    def _resolveAssociateTitles(cls,title, *tastelists):
        for id, titles in cls._list_titles.items():
            not_in_list = not any(id == tl.id for tl in tastelists)
            in_list = not not_in_list
            if not_in_list and title in titles:
                cls._list_titles[id].remove(title)
        
            elif in_list and title not in titles:
                cls._list_titles[id].append(title)

                

    @overload
    def _setAssociateTitle(cls, id :int, title):
        pass

    def _setAssociateTitle(cls, tastelist, title):
        if isinstance(tastelist, TasteList):
            tastelist = tastelist.id

        if tastelist not in cls._instances:
            raise ValueError("list with id {} does not exist".format(id))

        if title not in cls._list_titles[tastelist]:
            cls._list_titles[tastelist].append(title)

    def _delAssociateTitle(cls, tasteList, title):
        if isinstance(tasteList, TasteList):
            tasteList = tasteList.id

        if tasteList not in cls._instances:
            raise ValueError("list with id {} does not exist".format(id))

        if title not in cls._list_titles[tasteList]:
            return

        cls._list_titles[tasteList].remove(title)

    def _getAssociateTitle(cls, tastelist : typing.Union['TasteList', int]):
        if isinstance(tastelist, TasteList):
            tastelist = tastelist.id

        if tastelist not in cls._instances:
            raise ValueError("list with id {} does not exist".format(id))

        return cls._list_titles[tastelist]

@dataclass(frozen=True)
class TasteList(metaclass=TasteListMeta):
    id : int
    name : str

    def rename(self, name):
        raise NotImplementedError("rename")

    @property
    def titles(self):
        data = self.__class__._getAssociateTitle(self.id)
        return tuple(data)

    @overload
    @classmethod
    def getList(cls, id : int):
        pass

    @overload
    @classmethod
    def getList(cls, title : str):
        pass

    @classmethod
    def getList(cls, id_or_title : typing.Union[int, str]):
        if isinstance(id_or_title, int):
            return cls._instances.get(id_or_title, None)
        elif isinstance(id_or_title, str):
            for list in cls._instances.values():
                list : TasteList
                if list.name == id_or_title:
                    return list
        else:
            raise ValueError("id_or_title must be int or str")

    def __eq__(self, other):
        if isinstance(other, TasteList):
            return self.id == other.id
        else:
            return False

    def remove(self, title):
        if title not in self.titles:
            return

        title.ratings.toggle_list(self)