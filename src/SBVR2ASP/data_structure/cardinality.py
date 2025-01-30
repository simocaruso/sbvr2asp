from SBVR2ASP.asp.math import MathOperator, Math


class Cardinality:
    def __init__(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def as_guard(self):
        return (Math(MathOperator.LESS_THAN, self.lower_bound),
                Math(MathOperator.LESS_THAN, self.upper_bound))

    def __eq__(self, other):
        if not isinstance(other, Cardinality):
            return False
        return self.lower_bound == other.lower_bound and self.upper_bound == other.upper_bound


class ExactCardinality(Cardinality):
    def __init__(self, value):
        super().__init__(value, value)

    def as_guard(self):
        return None, Math(MathOperator.EQUAL, self.upper_bound)
