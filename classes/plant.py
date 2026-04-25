import Gclass
class Plant(Gclass):
    obj = {}
    lst = []
    pos = -1
    sortkey = ''
    att = ['_id', '_comments', '_company_id']
    headers = 'Centrais de Produção'
    des = ['ID Central', 'Comentários', 'ID Empresa Proprietária']

    def __init__(self, id=0, comments="", company_id=0):
        super().__init__()
        self._id = Plant.get_id(id)
        self._comments = comments
        self._company_id = company_id
       
        Plant.obj[self._id] = self
        Plant.lst.append(self._id)

    @property
    def id(self): return self._id

    @property
    def comments(self): return self._comments
    @comments.setter
    def comments(self, value): self._comments = value

    @property
    def company_id(self): return self._company_id
    @company_id.setter
    def company_id(self, value): self._company_id = value


