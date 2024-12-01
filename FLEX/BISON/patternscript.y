%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Prototipo da função yylex gerada pelo Flex
int yylex();
void yyerror(const char *s);

// Variáveis globais
int frameSize = 0;
char* threadColor = NULL;

%}

%union {
    int num;
    char* str;
}

%token <num> NUMBER
%token <str> STRING_LITERAL
%token SETUP LBRACE RBRACE FRAMESIZE THREADCOLOR DRAWLINE CHANGETHREAD IF ELSE
%token EQUALS SEMICOLON LPAREN RPAREN COMMA END_OF_FILE
%type <num> condition expression
%type <num> statement

%left '+' '-'
%left '*' '/'

%%

program:
    setup_block statement_list END_OF_FILE
    {
        printf("Parsing concluído com sucesso.\n");
    }
;

setup_block:
    SETUP LBRACE setup_commands RBRACE SEMICOLON
    {
        printf("Bloco de configuração processado: frameSize=%d, threadColor=%s\n", frameSize, threadColor);
    }
;

setup_commands:
    setup_command
    | setup_commands setup_command
;

setup_command:
    FRAMESIZE EQUALS NUMBER SEMICOLON
    {
        frameSize = $3;
        printf("frameSize configurado para %d\n", frameSize);
    }
    | THREADCOLOR EQUALS STRING_LITERAL SEMICOLON
    {
        threadColor = strdup($3);
        printf("threadColor configurado para %s\n", threadColor);
    }
;

statement_list:
    statement
    | statement_list statement
;

statement:
    DRAWLINE LPAREN expression COMMA expression COMMA expression COMMA expression RPAREN SEMICOLON
    {
        printf("Desenhando linha de (%d, %d) para (%d, %d)\n", $3, $5, $7, $9);
    }
    | CHANGETHREAD LPAREN STRING_LITERAL RPAREN SEMICOLON
    {
        printf("Mudando cor do fio para %s\n", $3);
    }
    | IF LPAREN condition RPAREN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE
    {
        if ($3) {
            printf("Condição verdadeira, executando bloco 'if'.\n");
        } else {
            printf("Condição falsa, executando bloco 'else'.\n");
        }
    }
;

condition:
    expression
    {
        $$ = $1;
        printf("Condição avaliada: %d\n", $1);
    }
;

expression:
    NUMBER
    {
        $$ = $1;
        printf("Expressão avaliada: %d\n", $1);
    }
    | expression '+' expression
    {
        $$ = $1 + $3;
        printf("Somando: %d + %d = %d\n", $1, $3, $$);
    }
    | expression '-' expression
    {
        $$ = $1 - $3;
        printf("Subtraindo: %d - %d = %d\n", $1, $3, $$);
    }
    | expression '*' expression
    {
        $$ = $1 * $3;
        printf("Multiplicando: %d * %d = %d\n", $1, $3, $$);
    }
    | expression '/' expression
    {
        if ($3 == 0) {
            yyerror("Divisão por zero!");
            $$ = 0;
        } else {
            $$ = $1 / $3;
            printf("Dividindo: %d / %d = %d\n", $1, $3, $$);
        }
    }
    | LPAREN expression RPAREN
    {
        $$ = $2;
        printf("Parênteses: %d\n", $2);
    }
;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Erro sintático: %s\n", s);
}

int main(int argc, char** argv) {
    if (argc < 2) {
        fprintf(stderr, "Erro: Arquivo de entrada não especificado.\n");
        return 1;
    }

    FILE* input = fopen(argv[1], "r");
    if (!input) {
        fprintf(stderr, "Erro: Não foi possível abrir o arquivo %s\n", argv[1]);
        return 1;
    }

    extern FILE* yyin;
    yyin = input;

    printf("Lendo arquivo: %s\n", argv[1]);
    if (yyparse() == 0) {
        printf("Parsing concluído com sucesso.\n");
    } else {
        printf("Falha no parsing.\n");
    }

    fclose(input);
    return 0;
}
