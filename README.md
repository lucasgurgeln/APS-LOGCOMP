### **Introdução à PatternScript**

A **PatternScript** é uma linguagem de programação criada para facilitar a criação de padrões geométricos e bordados de maneira intuitiva e eficiente. Inspirada nas técnicas tradicionais de bordado, ela permite aos usuários programar seus designs com precisão, reutilizar padrões e personalizá-los dinamicamente.

---

### **Motivação**
Padrões geométricos e bordados manuais seguem uma lógica repetitiva e estruturada, o que é ideal para ser transformado em código. A PatternScript nasceu para unir a arte dos bordados com a programação, oferecendo uma linguagem que simplifica a criação e modificação de designs, especialmente para artistas e programadores interessados em automatizar suas criações.

---

### **Funcionalidades Principais**
1. **Configurações Iniciais:**
   - Defina propriedades como tamanho do bastidor e cor inicial da linha.
   - Exemplo: `setup { frameSize = 20; threadColor = "blue"; };`

2. **Desenho de Formas Geométricas:**
   - Crie linhas e círculos com comandos simples.
   - Exemplo: `drawLine(0, 0, 10, 10);`

3. **Reutilização e Personalização:**
   - Use estruturas de controle como **loops** (`repeat`) para criar padrões repetitivos.
   - Exemplo:
     ```plaintext
     repeat i from 1 to 5 {
       drawCircle(i * 2, i * 2, 3);
     }
     ```

4. **Controle de Fluxo:**
   - Use **condicionais** (`if`, `else`) para personalizar padrões com base em condições.
   - Exemplo:
     ```plaintext
     if (i % 2 == 0) {
       changeThread("red");
     }
     ```

5. **Comentários no Código:**
   - Explique partes do código com `//`.

---

### **Como a PatternScript Funciona**
A PatternScript lê e executa programas em três etapas:
1. **Configuração:** Define o contexto inicial do bordado.
2. **Execução de Comandos:** Processa comandos sequenciais de desenho e configurações.
3. **Interpretação Dinâmica:** Realiza loops e condições para personalizar padrões.

**Exemplo de Entrada:**
```plaintext
setup {
  frameSize = 30;
  threadColor = "green";
};

drawLine(0, 0, 15, 15);
drawCircle(10, 10, 5);
changeThread("blue");
```

**Saída no Console:**
```plaintext
Configuração inicial: frameSize=30, threadColor=green
Desenhando linha de (0, 0) para (15, 15)
Desenhando círculo em (10, 10) com raio 5
Mudando cor para blue
```
