from abc import ABC, abstractmethod


class AbstractOperation(ABC):

    def __init__(self, operand_a, operand_b):
        self.operand_a = operand_a
        self.operand_b = operand_b
        super(AbstractOperation, self).__init__()

    #@abstractmethod
    def execute(self):
        return self.operand_a + self.operand_b


class AddOperation(AbstractOperation):
    #pass
    def __init__(self, operand_a, operand_b, c=6):
        self.operand_c = c
        super().__init__(operand_a, operand_b)
    def execute(self):
        return self.operand_a * self.operand_b

