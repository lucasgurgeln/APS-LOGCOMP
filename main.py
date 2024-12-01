import sys
import re

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

class Tokenizer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.current_token = None
        self.select_next()

    def select_next(self):
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

        if self.position >= len(self.source):
            self.current_token = Token('EOF')
        else:
            char = self.source[self.position]

            # Palavras-chave
            keywords = {
                'setup': 'SETUP',
                'frameSize': 'FRAMESIZE',
                'threadColor': 'THREADCOLOR',
                'drawLine': 'DRAWLINE',
                'changeThread': 'CHANGETHREAD',
                'if': 'IF',
                'else': 'ELSE',
                'while': 'WHILE'
            }

            if char.isalpha():
                identifier = ''
                while self.position < len(self.source) and self.source[self.position].isalnum():
                    identifier += self.source[self.position]
                    self.position += 1

                if identifier in keywords:
                    self.current_token = Token(keywords[identifier])
                else:
                    self.current_token = Token('IDENTIFIER', identifier)
            elif char == '{':
                self.current_token = Token('LBRACE', '{')
                self.position += 1
            elif char == '}':
                self.current_token = Token('RBRACE', '}')
                self.position += 1
            elif char == '(':
                self.current_token = Token('LPAREN', '(')
                self.position += 1
            elif char == ')':
                self.current_token = Token('RPAREN', ')')
                self.position += 1
            elif char == ',':
                self.current_token = Token('COMMA', ',')
                self.position += 1
            elif char == ';':
                self.current_token = Token('SEMICOLON', ';')
                self.position += 1
            elif char == '=':
                self.current_token = Token('ASSIGN', '=')
                self.position += 1
            elif char.isdigit():  # Reconhece números
                number = ''
                while self.position < len(self.source) and self.source[self.position].isdigit():
                    number += self.source[self.position]
                    self.position += 1
                self.current_token = Token('NUMBER', int(number))

            elif char == '"':  # Reconhece strings
                self.position += 1
                string_literal = ''
                while self.position < len(self.source) and self.source[self.position] != '"':
                    string_literal += self.source[self.position]
                    self.position += 1
                if self.position >= len(self.source):
                    raise Exception("Erro de sintaxe: String não terminada.")
                self.position += 1  # Avança após a última aspas
                self.current_token = Token('STRING_LITERAL', string_literal)

            else:
                raise Exception(f"Token desconhecido: {char}")

class SymbolTable:
    def __init__(self, parent=None):
        self.variables = {}  # Armazena variáveis
        self.functions = {}   # Armazena funções
        self.parent = parent

    def get_variable(self, name):
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name)
        else:
            raise ValueError(f"Variável '{name}' não definida.")

    def set_variable(self, name, value, var_type, is_declaration=False):
        # Normaliza os tipos para 'int' e 'char*'
        normalized_type = 'int' if var_type == 'INT_TYPE' else 'char*' if var_type == 'STRING_TYPE' else var_type

        # Depuração para verificar o registro da variável e seu tipo
        #print(f"Registrando variável '{name}' com valor '{value}' e tipo '{normalized_type}'.")

        if is_declaration:
            if name in self.variables:
                raise ValueError(f"Erro de semântica: Variável '{name}' já foi declarada.")
            self.variables[name] = (value, normalized_type)
        else:
            if name in self.variables:
                self.variables[name] = (value, normalized_type)
            elif self.parent:
                self.parent.set_variable(name, value, normalized_type)
            else:
                raise ValueError(f"Erro de semântica: Variável '{name}' não declarada antes da atribuição.")

    # Método para definir uma função
    def set_function(self, name, func_node):
        if name in self.functions:
            raise ValueError(f"Erro de semântica: Função '{name}' já foi declarada.")
        #print(f"Definindo nova função '{name}' com parâmetros: {func_node.params}.")
        self.functions[name] = func_node

    # Método para obter uma função
    def get_function(self, name):
        if name in self.functions:
            #print(f"Obtendo definição da função '{name}'.")
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        else:
            raise ValueError(f"Função '{name}' não definida.")

class PrePro:
    @staticmethod
    def filter(code):
        # Ignorar comentários do tipo // e /* */
        #code = re.sub(r'//.*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children or []

class BinOp(Node):
    def __init__(self, value, left, right):
        super().__init__(value, [left, right])

    def evaluate(self, symbol_table, global_table=None):
        # Chama evaluate em children sem global_table
        left_value, left_type = self.children[0].evaluate(symbol_table)
        right_value, right_type = self.children[1].evaluate(symbol_table)

        if self.value == '+':
            if left_type == 'char*' and right_type == 'char*':
                return left_value + right_value, 'char*'
            elif left_type == 'char*' and right_type == 'int':
                return left_value + str(right_value), 'char*'
            elif left_type == 'int' and right_type == 'char*':
                return str(left_value) + right_value, 'char*'
            elif left_type == 'int' and right_type == 'int':
                return left_value + right_value, 'int'
            else:
                raise TypeError(f"Erro de semântica: Operação '+' não permitida entre {left_type} e {right_type}")
        
        # Outros operadores permanecem inalterados

        # Permitir somente inteiros para -, *, e /
        elif self.value == '-' and left_type == 'int' and right_type == 'int':
            return left_value - right_value, 'int'
        elif self.value == '*' and left_type == 'int' and right_type == 'int':
            return left_value * right_value, 'int'
        elif self.value == '/' and left_type == 'int' and right_type == 'int':
            if right_value == 0:
                raise ZeroDivisionError("Erro de semântica: Divisão por zero.")
            return left_value // right_value, 'int'
        else:
            raise TypeError(f"Erro de semântica: Operação '{self.value}' não permitida entre {left_type} e {right_type}")

class UnOp(Node):
    def __init__(self, value, child):
        super().__init__(value, [child])

    def evaluate(self, symbol_table, global_table=None):
        child_value, child_type = self.children[0].evaluate(symbol_table, global_table=global_table)

        if self.value == '!':
            # Verifica se o tipo é válido para a operação de negação
            if child_type != 'int':
                raise TypeError(f"Erro de semântica: Operação de negação '!' só é permitida para inteiros.")
            return 0 if child_value else 1, 'int'
        elif self.value == '+':
            return +child_value, 'int'
        elif self.value == '-':
            return -child_value, 'int'


class IntVal(Node):
    def __init__(self, value):
        super().__init__('INT')
        self.value = value

    def evaluate(self, symbol_table, global_table=None):
        return self.value, 'int'

class NoOp(Node):
    def __init__(self):
        super().__init__('NoOp')

    def evaluate(self, symbol_table, global_table=None):
        pass

class BoolOp(Node):
    def __init__(self, value, left, right=None):
        super().__init__(value, [left, right] if right is not None else [left])

    def evaluate(self, symbol_table, global_table=None):
        left_value, _ = self.children[0].evaluate(symbol_table, global_table=global_table)
        right_value, _ = self.children[1].evaluate(symbol_table, global_table=global_table)
        if self.value == '&&':
            return (1 if left_value and right_value else 0), 'int'
        elif self.value == '||':
            return (1 if left_value or right_value else 0), 'int'
        elif self.value == '!':
            return (0 if left_value else 1), 'int'
class RelOp(Node):
    def __init__(self, value, left, right):
        super().__init__(value, [left, right])

    def evaluate(self, symbol_table, global_table=None):
        left_value, left_type = self.children[0].evaluate(symbol_table, global_table=global_table)
        right_value, right_type = self.children[1].evaluate(symbol_table, global_table=global_table)

        # Permite apenas comparações entre tipos compatíveis (ambos `int` ou ambos `char*`)
        if left_type != right_type:
            raise TypeError(f"Erro de semântica: Comparação não permitida entre {left_type} e {right_type}")

        # Comparações para strings
        if left_type == 'char*' and right_type == 'char*':
            if self.value == '==':
                return (1 if left_value == right_value else 0), 'int'
            elif self.value == '!=':
                return (1 if left_value != right_value else 0), 'int'
            elif self.value == '<':
                return (1 if left_value < right_value else 0), 'int'
            elif self.value == '>':
                return (1 if left_value > right_value else 0), 'int'
        
        # Comparações para inteiros
        elif left_type == 'int' and right_type == 'int':
            if self.value == '==':
                return (1 if left_value == right_value else 0), 'int'
            elif self.value == '!=':
                return (1 if left_value != right_value else 0), 'int'
            elif self.value == '<':
                return (1 if left_value < right_value else 0), 'int'
            elif self.value == '>':
                return (1 if left_value > right_value else 0), 'int'
            elif self.value == '<=':
                return (1 if left_value <= right_value else 0), 'int'
            elif self.value == '>=':
                return (1 if left_value >= right_value else 0), 'int'

        else:
            raise TypeError(f"Erro de semântica: Comparação não permitida para tipo {left_type}")

class StringVal(Node):
    def __init__(self, value):
        super().__init__('STRING')
        self.value = value

    def evaluate(self, symbol_table, global_table=None):
        return self.value, 'char*'


class AssignNode(Node):
    def __init__(self, identifier, expression=None, var_type=None, is_declaration=False):
        super().__init__('assign', [expression] if expression else [])
        self.identifier = identifier
        self.var_type = var_type
        self.is_declaration = is_declaration

    def evaluate(self, symbol_table, global_table=None):
        # Se for uma declaração, registra o valor padrão sem avaliar a expressão
        if self.is_declaration:
            default_value = 0 if self.var_type == 'int' else ""
            symbol_table.set_variable(self.identifier, default_value, self.var_type, is_declaration=True)
            return default_value, self.var_type

        # Se não for uma declaração, avalia a expressão normalmente
        value, expression_type = self.children[0].evaluate(symbol_table, global_table=global_table)

        # Verifica se `scanf()` está sendo atribuído corretamente
        if isinstance(self.children[0], ScanNode) and symbol_table.get_variable(self.identifier)[1] != 'int':
            raise TypeError(f"Erro de tipo: `scanf` só pode ser atribuído a variáveis do tipo `int`, mas '{self.identifier}' é do tipo '{self.var_type}'.")

        # Atualiza o valor da variável existente na tabela de símbolos
        symbol_table.set_variable(self.identifier, value, expression_type)
        return value, expression_type


class VarNode(Node):
    def __init__(self, identifier):
        super().__init__('var')
        self.identifier = identifier

    def evaluate(self, symbol_table, global_table=None):
        try:
            value = symbol_table.get_variable(self.identifier)
            #print(f"Variável '{self.identifier}' acessada com valor '{value[0]}' e tipo '{value[1]}'.")
            return value  # Retorna uma tupla (valor, tipo)
        except ValueError as e:
            if global_table and global_table != symbol_table:
                try:
                    value = global_table.get_variable(self.identifier)
                    #print(f"Variável '{self.identifier}' acessada no escopo global com valor '{value[0]}' e tipo '{value[1]}'.")
                    return value
                except ValueError:
                    pass
            print(f"Erro ao acessar '{self.identifier}': {e}")
            raise


class BlockNode(Node):
    def __init__(self, statements):
        super().__init__('block', statements)

    def evaluate(self, symbol_table, global_table=None):
        #print("Executando bloco de instruções.")
        for statement in self.children:
            # Passa `global_table` apenas se `evaluate` do nó aceitar
            if isinstance(statement, FuncCall) or isinstance(statement, VarNode) or isinstance(statement, BinOp):
                statement.evaluate(symbol_table, global_table=global_table)
            else:
                statement.evaluate(symbol_table)


class IfNode(Node):
    def __init__(self, condition, true_block, false_block=None):
        super().__init__('if', [condition, true_block] if false_block is None else [condition, true_block, false_block])

    def evaluate(self, symbol_table, global_table=None):
        # Chama evaluate em condition sem global_table para RelOp
        condition_value, condition_type = self.children[0].evaluate(symbol_table)
        #print(f"Avaliando 'if' com condição: {condition_value}")
        
        if condition_type != 'int':
            raise TypeError("Erro de semântica: Condição do 'if' deve ser do tipo 'int'")
        
        if condition_value:
            #print("Executando bloco 'true' do 'if'")
            self.children[1].evaluate(symbol_table, global_table=global_table)
        elif len(self.children) > 2:
            #print("Executando bloco 'false' do 'if'")
            self.children[2].evaluate(symbol_table, global_table=global_table)

class WhileNode(Node):
    def __init__(self, condition, block):
        super().__init__('while', [condition, block])

    def evaluate(self, symbol_table, global_table=None):
        # Chama evaluate em condition sem global_table para RelOp
        condition_value, condition_type = self.children[0].evaluate(symbol_table)
        if condition_type != 'int':
            raise TypeError("Erro de semântica: Condição do 'while' deve ser do tipo 'int'")
        while condition_value:
            self.children[1].evaluate(symbol_table, global_table=global_table)
            condition_value, condition_type = self.children[0].evaluate(symbol_table)


class ScanNode(Node):
    def __init__(self):
        super().__init__('scan')

    def evaluate(self, symbol_table, global_table=None):
        user_input = input("")  # Lê a entrada do usuário

        # Tenta converter a entrada para `int`; se falhar, gera um erro
        try:
            value = int(user_input)
            return value, 'int'
        except ValueError:
            raise TypeError("Erro de tipo: `scanf` esperava um valor `int`, mas recebeu uma string.")

class ReturnNode(Node):
    def __init__(self, expression):
        super().__init__('return', [expression])

    def evaluate(self, symbol_table):
        return self.children[0].evaluate(symbol_table)

class FuncDec(Node):
    def __init__(self, func_type, name, params, body):
        # Converte `func_type` para uma string consistente, como 'int' ou 'char*'
        func_type = 'int' if func_type == 'INT_TYPE' else 'char*' if func_type == 'STRING_TYPE' else 'void'
        super().__init__('FuncDec', [body])
        self.func_type = func_type
        self.name = name
        self.params = params

    def evaluate(self, symbol_table):
        symbol_table.set_function(self.name, self)
        return None

class FuncCall(Node):
    def __init__(self, name, args):
        super().__init__('FuncCall', args)
        self.name = name

    def evaluate(self, symbol_table, global_table=None):
        function_scope = global_table if global_table else symbol_table
        func_dec = function_scope.get_function(self.name)

        # Verifica o número de argumentos
        if len(self.children) != len(func_dec.params):
            raise ValueError(f"Erro: Função '{self.name}' esperava {len(func_dec.params)} argumentos, mas {len(self.children)} foram fornecidos.")

        local_table = SymbolTable(parent=function_scope)

        # Atribui os valores dos argumentos aos parâmetros da função
        for (param_name, param_type), arg_node in zip(func_dec.params, self.children):
            arg_value, arg_type = arg_node.evaluate(symbol_table)
            if arg_type != param_type:
                raise TypeError(f"Erro de tipo: Argumento '{param_name}' esperava '{param_type}' mas recebeu '{arg_type}'")
            local_table.set_variable(param_name, arg_value, param_type, is_declaration=True)

        # Executa o corpo da função e captura o retorno se houver um ReturnNode
        result = None
        for statement in func_dec.children[0].children:
            result = statement.evaluate(local_table)
            if isinstance(statement, ReturnNode):
                break  # Interrompe ao encontrar um retorno explícito

        # Se a função é do tipo void, assegure que nenhum valor é retornado
        if func_dec.func_type == 'void':
            return None
        # Se a função tem um tipo de retorno esperado e não há um resultado, define um valor padrão para int
        elif func_dec.func_type == 'int' and result is None:
            result = (0, 'int')
        
        # Verifica se o tipo do resultado coincide com o tipo da função
        elif result is not None and result[1] != func_dec.func_type:
            raise TypeError(f"Erro de tipo: Função '{self.name}' esperava retornar '{func_dec.func_type}' mas retornou '{result[1]}'")

        return result



class PrintNode(Node):
    def __init__(self, expression):
        super().__init__('print', [expression])

    def evaluate(self, symbol_table, global_table=None):
        value, var_type = self.children[0].evaluate(symbol_table, global_table=global_table)
        print(value) if var_type == 'int' else print(value)
        return value, var_type

class SetupNode(Node):
    def __init__(self, frame_size, thread_color):
        super().__init__('setup', [frame_size, thread_color])

    def evaluate(self, symbol_table):
        frame_size, _ = self.children[0].evaluate(symbol_table)
        thread_color, _ = self.children[1].evaluate(symbol_table)
        print(f"Configuração: frameSize={frame_size}, threadColor={thread_color}")


class DrawLineNode(Node):
    def __init__(self, x1, y1, x2, y2):
        super().__init__('drawLine', [x1, y1, x2, y2])

    def evaluate(self, symbol_table):
        x1, _ = self.children[0].evaluate(symbol_table)
        y1, _ = self.children[1].evaluate(symbol_table)
        x2, _ = self.children[2].evaluate(symbol_table)
        y2, _ = self.children[3].evaluate(symbol_table)
        print(f"Desenhando linha de ({x1}, {y1}) para ({x2}, {y2})")


class ChangeThreadNode(Node):
    def __init__(self, color):
        super().__init__('changeThread', [color])

    def evaluate(self, symbol_table):
        color, _ = self.children[0].evaluate(symbol_table)
        print(f"Mudando cor do fio para {color}")

class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def parse_statement(self):
        
        
        #print(f"Parsing statement, token atual: {self.tokenizer.current_token.type}")  # Depuração
        if self.tokenizer.current_token.type == 'SETUP':
            #print("Parsing setup block.")  # Depuração
            self.tokenizer.select_next()
            if self.tokenizer.current_token.type == 'LBRACE':
                self.tokenizer.select_next()
                frame_size = self.parse_assignment('FRAMESIZE')
                thread_color = self.parse_assignment('THREADCOLOR')
                if self.tokenizer.current_token.type == 'RBRACE':
                    self.tokenizer.select_next()
                    if self.tokenizer.current_token.type == 'SEMICOLON':
                        self.tokenizer.select_next()
                        #print("Setup block parsed successfully.")  # Depuração
                        return SetupNode(frame_size, thread_color)
                    else:
                        raise Exception("Erro de sintaxe: ';' esperado após '}'")
                else:
                    raise Exception("Erro de sintaxe: '}' esperado após configurações")
            else:
                raise Exception("Erro de sintaxe: '{' esperado após 'setup'")

        elif self.tokenizer.current_token.type == 'IF':  # Adiciona o caso específico para IF
            #print("Parsing if statement.")  # Depuração
            self.tokenizer.select_next()
            if self.tokenizer.current_token.type == 'LPAREN':
                self.tokenizer.select_next()
                condition = self.parse_expression()
                if self.tokenizer.current_token.type != 'RPAREN':
                    raise Exception("Erro de sintaxe: ')' esperado após a expressão do if")
                self.tokenizer.select_next()

                if self.tokenizer.current_token.type == 'LBRACE':
                    true_block = self.parse_block()
                else:
                    raise Exception("Erro de sintaxe: '{' esperado após a condição do if")

                false_block = None
                if self.tokenizer.current_token.type == 'ELSE':
                    self.tokenizer.select_next()
                    if self.tokenizer.current_token.type == 'LBRACE':
                        false_block = self.parse_block()
                    else:
                        raise Exception("Erro de sintaxe: '{' esperado após else")

                #print("If statement parsed.")  # Depuração
                return IfNode(condition, true_block, false_block)
            else:
                raise Exception("Erro de sintaxe: '(' esperado após 'if'")

        elif self.tokenizer.current_token.type == 'IDENTIFIER':
            #print(f"Parsing identifier: {self.tokenizer.current_token.value}")  # Depuração
            identifier = self.tokenizer.current_token.value
            self.tokenizer.select_next()

            if self.tokenizer.current_token.type == 'ASSIGN':
                self.tokenizer.select_next()
                expression = self.parse_expression()
                if self.tokenizer.current_token.type != 'SEMICOLON':
                    raise Exception("Erro de sintaxe: ';' esperado após a expressão")
                self.tokenizer.select_next()
                #print(f"Assignment parsed for identifier: {identifier}")  # Depuração
                return AssignNode(identifier, expression, None, is_declaration=False)

            elif self.tokenizer.current_token.type == 'LPAREN':
                #print(f"Function call detected: {identifier}")  # Depuração
                args = []
                self.tokenizer.select_next()
                while self.tokenizer.current_token.type != 'RPAREN':
                    args.append(self.parse_expression())
                    if self.tokenizer.current_token.type == 'COMMA':
                        self.tokenizer.select_next()
                if self.tokenizer.current_token.type != 'RPAREN':
                    raise Exception("Erro de sintaxe: ')' esperado após os argumentos da função")
                self.tokenizer.select_next()
                if self.tokenizer.current_token.type != 'SEMICOLON':
                    raise Exception("Erro de sintaxe: ';' esperado após a chamada da função")
                self.tokenizer.select_next()
                #print(f"Function call parsed: {identifier}")  # Depuração
                return FuncCall(identifier, args)

            else:
                raise Exception("Erro de sintaxe: '=' ou '(' esperado após o identificador")

        elif self.tokenizer.current_token.type == 'DRAWLINE':
            #print("Parsing drawLine statement.")  # Depuração
            self.tokenizer.select_next()
            if self.tokenizer.current_token.type == 'LPAREN':
                self.tokenizer.select_next()
                x1 = self.parse_expression()
                if self.tokenizer.current_token.type != 'COMMA':
                    raise Exception("Erro de sintaxe: ',' esperado após o primeiro argumento de drawLine")
                self.tokenizer.select_next()
                y1 = self.parse_expression()
                if self.tokenizer.current_token.type != 'COMMA':
                    raise Exception("Erro de sintaxe: ',' esperado após o segundo argumento de drawLine")
                self.tokenizer.select_next()
                x2 = self.parse_expression()
                if self.tokenizer.current_token.type != 'COMMA':
                    raise Exception("Erro de sintaxe: ',' esperado após o terceiro argumento de drawLine")
                self.tokenizer.select_next()
                y2 = self.parse_expression()
                if self.tokenizer.current_token.type != 'RPAREN':
                    raise Exception("Erro de sintaxe: ')' esperado após o quarto argumento de drawLine")
                self.tokenizer.select_next()
                if self.tokenizer.current_token.type != 'SEMICOLON':
                    raise Exception("Erro de sintaxe: ';' esperado após drawLine")
                self.tokenizer.select_next()
                #print("drawLine statement parsed.")  # Depuração
                return DrawLineNode(x1, y1, x2, y2)
            else:
                raise Exception("Erro de sintaxe: '(' esperado após 'drawLine'")

        elif self.tokenizer.current_token.type == '{':
            #print("Parsing block statement.")  # Depuração
            return self.parse_block()
        
        elif self.tokenizer.current_token.type == 'CHANGETHREAD':
            #print("Parsing changeThread statement.")  # Depuração
            self.tokenizer.select_next()
            if self.tokenizer.current_token.type == 'LPAREN':
                self.tokenizer.select_next()
                color = self.parse_expression()
                if self.tokenizer.current_token.type != 'RPAREN':
                    raise Exception("Erro de sintaxe: ')' esperado após o argumento de changeThread")
                self.tokenizer.select_next()  # Consome ')'
                if self.tokenizer.current_token.type != 'SEMICOLON':
                    raise Exception("Erro de sintaxe: ';' esperado após changeThread")
                self.tokenizer.select_next()  # Consome ';'
                #print("changeThread statement parsed.")  # Depuração
                return ChangeThreadNode(color)
            else:
                raise Exception("Erro de sintaxe: '(' esperado após 'changeThread'")


        else:
            raise Exception(f"Erro de sintaxe: Declaração inválida, token atual: {self.tokenizer.current_token.type}")

    def parse_block(self):
        #print(f"Iniciando parse_block, token atual: {self.tokenizer.current_token.type}")  # Depuração
        if self.tokenizer.current_token.type != 'LBRACE':
            raise Exception(f"Erro de sintaxe: '{{' esperado no início do bloco, token atual: {self.tokenizer.current_token.type}")
        self.tokenizer.select_next()  # Consome '{'

        statements = []
        while self.tokenizer.current_token.type != 'RBRACE' and self.tokenizer.current_token.type != 'EOF':
            #print(f"Parsing statement dentro do bloco, token atual: {self.tokenizer.current_token.type}")  # Depuração
            statements.append(self.parse_statement())

        if self.tokenizer.current_token.type != 'RBRACE':
            raise Exception(f"Erro de sintaxe: '}}' esperado ao final do bloco, token atual: {self.tokenizer.current_token.type}")
        self.tokenizer.select_next()  # Consome '}'

        #print(f"Finalizando parse_block, token atual: {self.tokenizer.current_token.type}")  # Depuração
        return BlockNode(statements)

    def parse_assignment(self, expected_identifier):
        if self.tokenizer.current_token.type != expected_identifier:
            raise Exception(f"Erro de sintaxe: Esperado '{expected_identifier}', mas encontrado '{self.tokenizer.current_token.type}'")
        self.tokenizer.select_next()

        if self.tokenizer.current_token.type != 'ASSIGN':
            raise Exception("Erro de sintaxe: '=' esperado após o identificador")
        self.tokenizer.select_next()

        if self.tokenizer.current_token.type == 'NUMBER':
            value = IntVal(self.tokenizer.current_token.value)
        elif self.tokenizer.current_token.type == 'STRING_LITERAL':
            value = StringVal(self.tokenizer.current_token.value)
        else:
            raise Exception("Erro de sintaxe: Valor esperado após '='")

        self.tokenizer.select_next()
        if self.tokenizer.current_token.type != 'SEMICOLON':
            raise Exception("Erro de sintaxe: ';' esperado após a atribuição")
        self.tokenizer.select_next()
        return value

    def parse_expression(self):
        result = self.parse_term()

        while self.tokenizer.current_token.type in ['+', '-', 'AND', 'OR', 'EQUAL', 'NOT_EQUAL', 'LESS', 'GREATER', 'LESS_EQUAL', 'GREATER_EQUAL']:
            operator = self.tokenizer.current_token.type
            self.tokenizer.select_next()
            next_term = self.parse_term()
            if operator in ['+', '-']:
                result = BinOp(operator, result, next_term)
            elif operator == 'AND':
                result = BoolOp('&&', result, next_term)
            elif operator == 'OR':
                result = BoolOp('||', result, next_term)
            elif operator in ['EQUAL', 'NOT_EQUAL', 'LESS', 'GREATER', 'LESS_EQUAL', 'GREATER_EQUAL']:
                if operator == 'EQUAL':
                    result = RelOp('==', result, next_term)
                elif operator == 'NOT_EQUAL':
                    result = RelOp('!=', result, next_term)
                elif operator == 'LESS':
                    result = RelOp('<', result, next_term)
                elif operator == 'GREATER':
                    result = RelOp('>', result, next_term)
                elif operator == 'LESS_EQUAL':
                    result = RelOp('<=', result, next_term)
                elif operator == 'GREATER_EQUAL':
                    result = RelOp('>=', result, next_term)
        return result


    def parse_term(self):
        result = self.parse_factor()
        while self.tokenizer.current_token.type in ['*', '/']:
            operator = self.tokenizer.current_token.type
            self.tokenizer.select_next()
            next_factor = self.parse_factor()
            result = BinOp(operator, result, next_factor)
        return result


    def parse_factor(self):
        if self.tokenizer.current_token.type == 'NOT':
            self.tokenizer.select_next()
            factor = self.parse_factor()
            return UnOp('!', factor)

        elif self.tokenizer.current_token.type == 'SCANF':
            self.tokenizer.select_next()
            if self.tokenizer.current_token.type == '(':
                self.tokenizer.select_next()
                if self.tokenizer.current_token.type != ')':
                    raise Exception("Erro de sintaxe: ')' esperado após 'scanf'")
                self.tokenizer.select_next()
                return ScanNode()

        elif self.tokenizer.current_token.type == '(':
            self.tokenizer.select_next()
            result = self.parse_expression()
            if self.tokenizer.current_token.type != ')':
                raise Exception("Erro de sintaxe: ')' esperado após a expressão")
            self.tokenizer.select_next()
            return result

        elif self.tokenizer.current_token.type in ['+', '-']:
            operator = self.tokenizer.current_token.type
            self.tokenizer.select_next()
            factor = self.parse_factor()
            return UnOp(operator, factor)

        elif self.tokenizer.current_token.type == 'NUMBER':
            result = IntVal(self.tokenizer.current_token.value)
            self.tokenizer.select_next()
            return result


        elif self.tokenizer.current_token.type == 'STRING_LITERAL':
            result = StringVal(self.tokenizer.current_token.value)
            self.tokenizer.select_next()
            return result


        elif self.tokenizer.current_token.type == 'IDENTIFIER':
            identifier = self.tokenizer.current_token.value
            self.tokenizer.select_next()
            
            # Verificação para chamadas de função
            if self.tokenizer.current_token.type == '(':
                args = []
                self.tokenizer.select_next()
                while self.tokenizer.current_token.type != ')':
                    args.append(self.parse_expression())
                    if self.tokenizer.current_token.type == ',':
                        self.tokenizer.select_next()
                if self.tokenizer.current_token.type != ')':
                    raise Exception("Erro de sintaxe: ')' esperado após os argumentos da função")
                self.tokenizer.select_next()  # Avança após ')'
                return FuncCall(identifier, args)  # Retorna chamada de função como um fator

            return VarNode(identifier)  # Retorna o nó da variável, se não for uma chamada de função

        else:
            raise Exception("Erro de sintaxe: Fator inválido")


    @staticmethod
    def run(code):
        if code.strip() == "":
            raise Exception("Erro de sintaxe: A expressão não pode ser vazia ou consistir apenas de espaços em branco.")

        code = PrePro.filter(code)
        tokenizer = Tokenizer(code)
        parser = Parser(tokenizer)
        statements = []
        while tokenizer.current_token.type != 'EOF':
            statements.append(parser.parse_statement())
        ast = BlockNode(statements)


        if tokenizer.current_token.type != 'EOF':
            raise Exception("Erro de sintaxe: Código após o fim da expressão.")

        return ast

def main():
    if len(sys.argv) != 2:
        print("Uso: python nome_do_arquivo.py arquivo.pattern", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]
    if not filename.endswith('.pattern'):
        print("Erro: O arquivo deve ter a extensão .pattern", file=sys.stderr)
        sys.exit(1)

    try:
        with open(filename, 'r') as file:
            code = file.read()

        # Inicializa o AST e a tabela de símbolos
        ast = Parser.run(code)
        symbol_table = SymbolTable()

        # Executa o bloco global de instruções
        ast.evaluate(symbol_table)

        # Tenta encontrar e executar a função `main` se ela estiver definida
        try:
            main_function = symbol_table.get_function("main")
            main_call = FuncCall("main", [])
            main_call.evaluate(symbol_table, global_table=symbol_table)
        except ValueError:
            # Se `main` não for encontrada, apenas continue com o restante
            pass


    except FileNotFoundError:
        print(f"Erro: O arquivo {filename} não foi encontrado.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
