class Literal(object):
    def __init__(self):
        pass

    def init(self):
        raise NotImplementedError()

    def __repr__(self):
        return self.__str__()
