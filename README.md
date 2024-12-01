### Introdução à PatternScript

**PatternScript** é uma linguagem de programação criada para facilitar a criação de padrões geométricos e bordados de maneira intuitiva e eficiente. Inspirada nas técnicas tradicionais de bordado, ela permite aos usuários programar designs com precisão e personalizá-los dinamicamente.

---

### Motivação

Os padrões geométricos e bordados manuais seguem uma lógica repetitiva e estruturada, ideal para ser representada por meio de código. A **PatternScript** nasceu para unir a arte dos bordados com a programação, simplificando a criação de designs e automatizando o processo criativo.

---
### EBNF
```
Program      ::= { Statement }

Statement    ::= SetupStatement
               | DrawLineStatement
               | ChangeThreadStatement
               | IfStatement
               | Block
               | ";"

SetupStatement   ::= "setup" "{" SetupAssignment ";" SetupAssignment ";" "}"
SetupAssignment  ::= "frameSize" "=" Number | "threadColor" "=" String

DrawLineStatement ::= "drawLine" "(" Expression "," Expression "," Expression "," Expression ")" ";"

ChangeThreadStatement ::= "changeThread" "(" String ")" ";"

IfStatement      ::= "if" "(" Expression ")" Block [ "else" Block ]

Block            ::= "{" { Statement } "}"

Expression       ::= Term { ("+" | "-") Term }
Term             ::= Factor { ("*" | "/") Factor }
Factor           ::= Number
                  | String
                  | "(" Expression ")"
                  | "!" Factor
                  | Identifier
                  | FunctionCall

FunctionCall     ::= Identifier "(" [ Expression { "," Expression } ] ")"

Identifier       ::= Letter { Letter | Digit }
Number           ::= Digit { Digit }
String           ::= '"' { Character } '"'
Letter           ::= "a" | "b" | ... | "z" | "A" | "B" | ... | "Z"
Digit            ::= "0" | "1" | ... | "9"
Character        ::= qualquer caractere Unicode, exceto aspas duplas (")
```

### Explicação das Regras

1. **Program**: Um programa consiste em zero ou mais **Statements** (instruções), que podem ser comandos de configuração, desenhos, ou controles de fluxo.

2. **Statements**:
   - **SetupStatement**: Define as configurações iniciais (`frameSize` e `threadColor`) dentro de chaves (`{}`).
   - **DrawLineStatement**: Comando para desenhar uma linha entre dois pontos definidos pelas coordenadas `(x1, y1)` e `(x2, y2)`.
   - **ChangeThreadStatement**: Comando para alterar a cor da linha durante o design.
   - **IfStatement**: Controle de fluxo que executa blocos de código com base em condições.
   - **Block**: Representa um conjunto de **Statements** delimitado por `{}`.

3. **Expressions**:
   - Suportam operações aritméticas básicas (`+`, `-`, `*`, `/`).
   - Podem incluir números, strings, identificadores, ou chamadas de função.
   - Permitem agrupamento com parênteses.

4. **FunctionCall**: Uma chamada de função pode conter zero ou mais expressões como argumentos, separados por vírgulas.

5. **Tipos de Dados**:
   - **Number**: Representa inteiros (por exemplo, `10`, `42`).
   - **String**: Representa textos entre aspas duplas (por exemplo, `"blue"`, `"red"`).

---

### Funcionalidades Implementadas

#### Configurações Iniciais
Defina propriedades como o tamanho do bastidor e a cor inicial da linha.

**Exemplo:**
```pattern
setup {
  frameSize = 20;
  threadColor = "blue";
};
```

#### Desenho de Linhas
Crie linhas com coordenadas específicas.

**Exemplo:**
```pattern
drawLine(0, 0, 10, 10);
```

#### Controle de Fluxo
Use condicionais (`if`, `else`) para personalizar padrões com base em condições.

**Exemplo:**
```pattern
if (1) {
  drawLine(0, 0, 15, 15);
} else {
  drawLine(10, 10, 30, 30);
}
```

#### Alteração de Cor
Mude dinamicamente a cor do fio.

**Exemplo:**
```pattern
changeThread("red");
```

#### Comentários no Código
Explique partes do código com `//`.

**Exemplo:**
```pattern
// Esta linha muda a cor para azul
changeThread("blue");
```

---

### Como a PatternScript Funciona

1. **Configuração:** Define o contexto inicial do bordado.
2. **Execução de Comandos:** Processa comandos sequenciais de desenho e configurações.
3. **Interpretação Dinâmica:** Realiza condicionais para personalizar padrões.

---

### Exemplo de Entrada

```pattern
setup {
  frameSize = 30;
  threadColor = "green";
};

drawLine(0, 0, 15, 15);
changeThread("blue");
```

### Saída no Console

```plaintext
Configuração inicial: frameSize=30, threadColor=green
Desenhando linha de (0, 0) para (15, 15)
Mudando cor para blue
```

