from SBVR2ASP.asp.math import MathOperator, Math


class Cardinality:
    def __init__(self, lower_bound=None, upper_bound=None):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def as_guard(self):
        if self.lower_bound is not None and self.upper_bound is not None:
            return (Math(MathOperator.LESS_THAN_OR_EQUAL, self.lower_bound),
                    Math(MathOperator.LESS_THAN_OR_EQUAL, self.upper_bound))
        elif self.lower_bound is not None:
            return Math(MathOperator.GREATER_THAN_OR_EQUAL, self.lower_bound), None
        elif self.upper_bound is not None:
            return None, Math(MathOperator.LESS_THAN_OR_EQUAL, self.upper_bound)

    def __eq__(self, other):
        if not isinstance(other, Cardinality):
            return False
        return self.lower_bound == other.lower_bound and self.upper_bound == other.upper_bound


class ExactCardinality(Cardinality):
    def __init__(self, value):
        super().__init__(value, value)

    def as_guard(self):
        return None, Math(MathOperator.EQUAL, self.upper_bound)
