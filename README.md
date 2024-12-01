### Introdução à PatternScript

**PatternScript** é uma linguagem de programação criada para facilitar a criação de padrões geométricos e bordados de maneira intuitiva e eficiente. Inspirada nas técnicas tradicionais de bordado, ela permite aos usuários programar designs com precisão e personalizá-los dinamicamente.

---

### Motivação

Os padrões geométricos e bordados manuais seguem uma lógica repetitiva e estruturada, ideal para ser representada por meio de código. A **PatternScript** nasceu para unir a arte dos bordados com a programação, simplificando a criação de designs e automatizando o processo criativo.

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

