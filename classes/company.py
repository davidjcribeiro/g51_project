from classes.Gclass import Gclass
class Company(Gclass):
    obj = {}
    lst = []
    pos = -1
    sortkey = ''
    att = ['_id', '_name', '_creation_date']
    headers = 'Empresas de Energia'
    des = ['ID Empresa', 'Nome', 'Data de Criação']

    def __init__(self, id=0, name="", creation_date=""):
        super().__init__()
        self._id = Company.get_id(id)
        self._name = name
        self._creation_date = creation_date
       
        Company.obj[self._id] = self
        Company.lst.append(self._id)

    @property
    def id(self): return self._id
   
    @property
    def name(self): return self._name
    @name.setter
    def name(self, value): self._name = value

    @property
    def creation_date(self): return self._creation_date
    @creation_date.setter
    def creation_date(self, value): self._creation_date = value
