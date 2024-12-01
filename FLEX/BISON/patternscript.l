%{
#include "patternscript.tab.h"
#include <stdio.h>
#include <string.h>
%}

%%

"setup"                 { printf("Token: SETUP\n"); return SETUP; }
"{"                     { printf("Token: LBRACE\n"); return LBRACE; }
"}"                     { printf("Token: RBRACE\n"); return RBRACE; }
"frameSize"             { printf("Token: FRAMESIZE\n"); return FRAMESIZE; }
"threadColor"           { printf("Token: THREADCOLOR\n"); return THREADCOLOR; }
"drawLine"              { printf("Token: DRAWLINE\n"); return DRAWLINE; }
"changeThread"          { printf("Token: CHANGETHREAD\n"); return CHANGETHREAD; }
"if"                    { printf("Token: IF\n"); return IF; }
"else"                  { printf("Token: ELSE\n"); return ELSE; }
"="                     { printf("Token: EQUALS\n"); return EQUALS; }
";"                     { printf("Token: SEMICOLON\n"); return SEMICOLON; }
","                     { printf("Token: COMMA\n"); return COMMA; }
"("                     { printf("Token: LPAREN\n"); return LPAREN; }
")"                     { printf("Token: RPAREN\n"); return RPAREN; }
[0-9]+                  { printf("Token: NUMBER (%s)\n", yytext); yylval.num = atoi(yytext); return NUMBER; }
\"[^\"]*\"              { printf("Token: STRING_LITERAL (%s)\n", yytext); yylval.str = strdup(yytext); return STRING_LITERAL; }
[ \t\r]+                ; // Ignora espaços em branco
"\n"                    ; // Ignora novas linhas
<<EOF>>                 { printf("Token: EOF\n"); return END_OF_FILE; }
.                       { printf("Token desconhecido: %c\n", yytext[0]); return yytext[0]; }

%%

int yywrap() {
    return 1;
}
