# 📚 Documentação Completa - Analisador Sintático SLR(1)

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Módulos e Funções](#módulos-e-funções)
4. [Exemplos de Uso](#exemplos-de-uso)
5. [Gramática da Linguagem](#gramática-da-linguagem)

---

## 🎯 Visão Geral

Este projeto implementa um **compilador completo em três fases** para uma linguagem de programação com sintaxe inspirada em Skyrim/Elder Scrolls:

1. **Análise Léxica (Scanner)** - Tokenização do código fonte
2. **Análise Sintática SLR(1)** - Validação da estrutura gramatical
3. **Análise Semântica** - Verificação de tipos, escopos e tabela de símbolos

### Palavras-chave da Linguagem

| Palavra-chave | Significado | Exemplo |
|---------------|-------------|---------|
| `FUS` | Declaração com atribuição | `FUS x := 10` |
| `LOS` | Condicional (if) | `LOS x CMD` |
| `FOD ... FAH` | Laço while | `FOD CMD FAH EXPR` |
| `FAH ... FAH` | Laço for | `FAH CMD FAH EXPR` |
| `KEL` | Módulo/namespace | `KEL player CMD` |
| `HON` | Input | `HON var` |
| `print` | Output | `print var` |
| `JUN` | Return | `JUN x` |
| `HIM` | This/self (acesso a membro) | `HIM . health` |
| `assign` | Atribuição | `assign x := 5` |
| `NUST` | Negação lógica (NOT) | `NUST x` |
| `ANRK` | E lógico (AND) | `x ANRK y` |
| `AAN` | OU lógico (OR) | `x AAN y` |
| `KO` | Pertencimento (IN) | `x KO y` |

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    CÓDIGO FONTE                          │
│           (Linguagem Fantasy - Skyrim Style)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         FASE 1: ANÁLISE LÉXICA (lexer.py)               │
│  • Tokenização                                           │
│  • Identificação de palavras-chave                       │
│  • Detecção de erros léxicos                             │
└────────────────────┬────────────────────────────────────┘
                     │ [Lista de Tokens]
                     ▼
┌─────────────────────────────────────────────────────────┐
│    FASE 2: ANÁLISE SINTÁTICA (parser_integrated.py)     │
│  • Parsing SLR(1)                                        │
│  • Validação de estrutura gramatical                     │
│  • Stack e transições de estado                          │
└────────────────────┬────────────────────────────────────┘
                     │ [Árvore Sintática]
                     ▼
┌─────────────────────────────────────────────────────────┐
│      FASE 3: ANÁLISE SEMÂNTICA (symbol_table.py)        │
│  • Tabela de símbolos                                    │
│  • Verificação de declarações                            │
│  • Análise de escopo                                     │
│  • Detecção de variáveis não usadas                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              ✅ CÓDIGO VALIDADO
```

---

## 📦 Módulos e Funções

### 1️⃣ **lexer.py** - Analisador Léxico

#### Classe `TokenType`
Enumeração com todos os tipos de tokens suportados.

```python
class TokenType(Enum):
    LOS = "LOS"      # if
    FOD = "FOD"      # while início
    FAH = "FAH"      # separador
    # ... 23 tipos no total
```

#### Classe `Token`
Representa um token com seus atributos.

**Atributos:**
- `type`: Tipo do token (ex: "id", "num", "LOS")
- `lexeme`: Texto literal do token
- `line`: Linha no código fonte
- `column`: Coluna no código fonte
- `value`: Valor semântico (para números)

#### Classe `Lexer`

##### `__init__(self, source_code: str)`
**Descrição:** Inicializa o analisador léxico com o código fonte.

**Lógica:**
1. Armazena código fonte na variável `self.source`
2. Inicializa ponteiro de posição (`self.position = 0`)
3. Configura rastreamento de linha e coluna
4. Cria listas vazias para tokens e erros

**Exemplo:**
```python
code = "FUS x := 10"
lexer = Lexer(code)
```

##### `current_char(self) -> str | None`
**Descrição:** Retorna o caractere atual sem avançar o ponteiro.

**Lógica:**
```python
if self.position >= len(self.source):
    return None
return self.source[self.position]
```

**Saída:** Caractere na posição atual ou `None` se fim do arquivo.

##### `advance(self)`
**Descrição:** Avança o ponteiro para o próximo caractere e atualiza linha/coluna.

**Lógica:**
1. Se caractere é `\n`: incrementa linha, reseta coluna
2. Caso contrário: incrementa coluna
3. Incrementa posição

##### `skip_whitespace(self)`
**Descrição:** Pula espaços em branco, tabs e quebras de linha.

**Lógica:**
```python
while current_char() in ' \t\n\r':
    advance()
```

##### `skip_comment(self) -> bool`
**Descrição:** Pula comentários de linha (#) e bloco (/* */).

**Lógica:**
- **Comentário de linha:** `# texto até \n`
  - Avança até encontrar `\n`
- **Comentário de bloco:** `/* texto */`
  - Avança até encontrar `*/`
  - Gera erro se não fechado

**Retorna:** `True` se pulou comentário, `False` caso contrário.

**Exemplo:**
```python
# Este é um comentário de linha
FUS x := 10  /* comentário de bloco */
```

##### `read_number(self) -> Token`
**Descrição:** Lê uma sequência de dígitos e cria token numérico.

**Lógica:**
1. Coleta todos os dígitos consecutivos
2. Converte string para inteiro
3. Cria token do tipo `NUM`

**Entrada:** `"123abc"`
**Saída:** `Token(NUM, "123", linha, coluna, 123)`

##### `read_identifier_or_keyword(self) -> Token`
**Descrição:** Lê identificador ou palavra-chave.

**Lógica:**
1. Coleta caracteres alfanuméricos e underscore
2. Verifica se texto está no dicionário `KEYWORDS`
3. Se sim: retorna token de palavra-chave
4. Se não: retorna token `ID`

**Exemplo:**
```python
# Entrada: "LOS"
# Saída: Token(LOS, "LOS", 1, 1, "LOS")

# Entrada: "health"
# Saída: Token(id, "health", 1, 1, "health")
```

##### `read_operator(self) -> Token | None`
**Descrição:** Lê operadores e pontuação.

**Lógica:**
- Operador composto `:=`: verifica dois caracteres
- Operadores simples: `+`, `-`, `;`, `.`, `(`, `)`

**Exemplo:**
```python
# Entrada: ":="
# Saída: Token(":=", ":=", 1, 1, ":=")
```

##### `tokenize(self) -> List[Token]`
**Descrição:** **Função principal** - Converte código fonte em lista de tokens.

**Algoritmo:**
```
ENQUANTO não chegou ao fim do arquivo:
    1. Pular espaços em branco
    2. Pular comentários
    3. Tentar ler número
    4. Tentar ler identificador/palavra-chave
    5. Tentar ler operador
    6. Se nenhum caso: gerar erro léxico
    
ADICIONAR token EOF ($) no final
RETORNAR lista de tokens
```

**Exemplo completo:**
```python
code = """
FUS health := 100
assign health := health - 10
JUN health
"""

lexer = Lexer(code)
tokens = lexer.tokenize()

# Resultado:
# [
#   Token(FUS, "FUS", 2, 1),
#   Token(id, "health", 2, 5),
#   Token(:=, ":=", 2, 12),
#   Token(num, "100", 2, 15, 100),
#   Token(assign, "assign", 3, 1),
#   ...
#   Token($, "$", 5, 1)
# ]
```

##### `print_tokens(self)`
**Descrição:** Imprime tabela formatada de tokens.

**Saída:**
```
================================================================================
FITA DE TOKENS
================================================================================
#     Tipo            Lexema               Linha    Coluna   Valor
--------------------------------------------------------------------------------
1     FUS             FUS                  1        1        FUS
2     id              health               1        5        health
3     :=              :=                   1        12       :=
4     num             100                  1        15       100
5     $               $                    1        19       $
================================================================================
Total de tokens: 5
```

##### `has_errors(self) -> bool`
**Descrição:** Verifica se houve erros léxicos.

**Retorna:** `True` se `len(self.errors) > 0`

##### `print_errors(self)`
**Descrição:** Imprime erros léxicos formatados.

**Exemplo de saída:**
```
================================================================================
ERROS LÉXICOS
================================================================================
  ✗ ERRO LÉXICO (Linha 3, Coluna 15): Caractere inválido '@'
  ✗ ERRO LÉXICO (Linha 5, Coluna 1): Comentário de bloco não fechado
================================================================================
```

---

### 2️⃣ **parser_integrated.py** - Analisador Sintático SLR(1)

#### Classe `Token`
Mesma estrutura do lexer, usada para representar tokens com atributos semânticos.

#### Classe `SemanticError`
Exceção personalizada para erros semânticos.

**Atributos:**
- `message`: Mensagem de erro
- `line`: Linha do erro
- `column`: Coluna do erro
- `error_type`: Tipo do erro (ex: "SEMANTIC")

#### Classe `SLRParserWithSemantics`

##### `__init__(self, verbose=True)`
**Descrição:** Inicializa o parser com análise semântica integrada.

**Atributos inicializados:**
- `stack`: Pilha de estados (inicia com [0])
- `symbols`: Pilha de símbolos sintáticos
- `attributes`: Pilha de atributos semânticos
- `symbol_table`: Tabela de símbolos (instância de `SymbolTable`)
- `closures`: Closures LR(0) importados de `SLR.py`
- `transitions`: Tabela GOTO importada de `goto.py`
- `follow`: Conjuntos FOLLOW importados de `follow.py`

**Lógica:**
```python
self.stack = [0]              # Estado inicial
self.symbols = []             # Vazia
self.attributes = []          # Vazia
self.symbol_table = SymbolTable()
```

##### `_extract_productions(self) -> dict`
**Descrição:** Extrai produções gramaticais dos closures.

**Lógica:**
1. Percorre todos os estados nos closures
2. Identifica produções completas (ponto no final)
3. Armazena no formato `{estado: (lhs, [rhs])}`

**Exemplo:**
```python
# Closure 11: ["IO -> HON."]
# Produção extraída:
productions[11] = ("IO", ["HON"])
```

##### `semantic_action(self, production_lhs, production_rhs, attributes) -> Any`
**Descrição:** **FUNÇÃO CENTRAL** - Executa ações semânticas durante reduções.

**Lógica por tipo de produção:**

**1. FUS id := EXPR (Declaração)**
```python
if production_lhs == "CMD" and len(production_rhs) == 4:
    if production_rhs[0] == "FUS":
        var_token = attributes[1]      # Token do identificador
        expr_value = attributes[3]     # Valor da expressão
        
        # DECLARA na tabela de símbolos
        self.symbol_table.declare(
            var_token.lexeme,
            symbol_type="variable",
            line=var_token.line,
            value=expr_value
        )
        
        return {"type": "declaration", "name": var_token.lexeme, "value": expr_value}
```

**Exemplo:**
```python
# Código: FUS health := 100
# Ação: Declara 'health' com valor 100 no escopo atual
```

**2. assign id := EXPR (Atribuição)**
```python
if production_lhs == "CMD" and production_rhs[1] == ":=":
    lhs_info = attributes[0]       # Informações do LHS
    expr_value = attributes[2]     # Novo valor
    
    # VERIFICA se variável foi declarada
    symbol = self.symbol_table.lookup(var_name, line=var_line)
    if symbol:
        symbol.value = expr_value  # Atualiza valor
```

**Exemplo:**
```python
# Código: assign health := 50
# Ação: Verifica se 'health' existe e atualiza para 50
```

**3. KEL id CMD (Módulo)**
```python
if production_lhs == "CMD" and production_rhs[0] == "KEL":
    module_token = attributes[1]
    
    # ENTRA em novo escopo
    self.symbol_table.enter_scope(f"KEL_{module_token.lexeme}")
    
    # DECLARA módulo
    self.symbol_table.declare(
        module_token.lexeme,
        symbol_type="module",
        line=module_token.line
    )
```

**Exemplo:**
```python
# Código: KEL player FUS health := 100
# Ação: Cria escopo "KEL_player" e declara 'health' dentro dele
```

**4. FACTOR -> id (Uso de variável)**
```python
if production_lhs == "FACTOR" and production_rhs[0] == "id":
    id_token = attributes[0]
    
    # BUSCA na tabela de símbolos
    symbol = self.symbol_table.lookup(id_token.lexeme, line=id_token.line)
    
    if symbol:
        return symbol.value  # Retorna valor armazenado
    else:
        # ERRO: variável não declarada
```

**Exemplo:**
```python
# Código: JUN health
# Ação: Busca 'health' na tabela, retorna erro se não encontrada
```

**5. EXPR -> TERM EXPR' (Expressão aritmética)**
```python
if production_lhs == "EXPR":
    term_value = attributes[0]
    expr_prime = attributes[1]
    
    if expr_prime and "op" in expr_prime:
        # Síntese: combina termo e operador
        return f"({term_value} {expr_prime['op']} {expr_prime['right']})"
    else:
        return term_value
```

**Exemplo:**
```python
# Código: 10 + 20 - 5
# Síntese: "(10 + (20 - 5))"
```

##### `parse(self, tokens: List[Token]) -> bool`
**Descrição:** **FUNÇÃO PRINCIPAL** - Realiza parsing SLR(1) com análise semântica.

**Algoritmo completo:**
```
INICIALIZAR:
    stack = [0]
    token_index = 0
    current_token = tokens[0]

LOOP INFINITO:
    state = stack[-1]
    lookahead = current_token.type
    
    # CASO 1: ACEITAÇÃO
    SE state == 1 E lookahead == "$":
        Verificar símbolos não usados
        RETORNAR sucesso
    
    # CASO 2: SHIFT
    SE (state, lookahead) ∈ transitions:
        next_state = transitions[(state, lookahead)]
        Empilhar: state, symbol, attribute
        Avançar para próximo token
        CONTINUAR
    
    # CASO 3: EPSILON TRANSITION
    SE (state, "epsilon") ∈ transitions:
        Tratar EXPR' -> ε
        Fazer GOTO
        CONTINUAR
    
    # CASO 4: REDUCE
    SE state tem produção E lookahead ∈ FOLLOW(lhs):
        lhs, rhs = productions[state]
        
        # Coletar atributos
        prod_attributes = attributes[-len(rhs):]
        
        # EXECUTAR AÇÃO SEMÂNTICA
        synthesized = semantic_action(lhs, rhs, prod_attributes)
        
        # Desempilhar símbolos
        POP len(rhs) símbolos da pilha
        
        # GOTO
        state_after = stack[-1]
        goto_state = transitions[(state_after, lhs)]
        
        Empilhar: goto_state, lhs, synthesized
        CONTINUAR
    
    # CASO 5: ERRO SINTÁTICO
    Registrar erro
    RETORNAR False
```

**Exemplo de execução:**

```python
# Código: FUS x := 10

tokens = [
    Token("FUS", "FUS", 1),
    Token("id", "x", 1),
    Token(":=", ":=", 1),
    Token("num", "10", 1, value=10),
    Token("$", "$", 1)
]

parser = SLRParserWithSemantics(verbose=True)
sucesso = parser.parse(tokens)

# Saída (verbose):
# Passo 1: Stack=[0], Estado=0, Token=FUS
#   SHIFT -> 10
# 
# Passo 2: Stack=[0, 10], Estado=10, Token=id
#   SHIFT -> 27
#
# Passo 3: Stack=[0, 10, 27], Estado=27, Token=:=
#   SHIFT -> 51
#
# Passo 4: Stack=[0, 10, 27, 51], Estado=51, Token=num
#   SHIFT -> 22
#
# Passo 5: Stack=[0, 10, 27, 51, 22], Estado=22, Token=$
#   REDUCE FACTOR -> num
#   [Semântico] Valor: 10
#   GOTO(51, FACTOR) = 19
#
# ... (continua até aceitação)
#
# [OK] ANALISE SINTATICA ACEITA!
```

##### `has_errors(self) -> bool`
**Descrição:** Verifica se há erros sintáticos ou semânticos.

**Lógica:**
```python
return len(self.errors) > 0 or self.symbol_table.has_errors()
```

##### `print_report(self)`
**Descrição:** Imprime relatório completo com erros, avisos e tabela de símbolos.

**Saída:**
```
======================================================================
RELATORIO DE ANALISE
======================================================================

[X] ERROS ENCONTRADOS:
  - ERRO SINTATICO (Linha 3): Token inesperado 'num'
  - Erro semântico (linha 5): 'y' não foi declarado

[!] AVISOS:
  - Aviso (linha 2): variável 'z' declarada mas não usada

======================================================================
TABELA DE SIMBOLOS
======================================================================
Escopo: global
  [✓] health: variable
  [ ] z: variable
  Escopo: KEL_player
    [✓] strength: variable
======================================================================
```

##### `reset(self)`
**Descrição:** Reinicia o parser para nova análise.

**Lógica:**
```python
self.stack = [0]
self.symbols = []
self.attributes = []
self.symbol_table = SymbolTable()
self.errors = []
self.warnings = []
```

---

### 3️⃣ **symbol_table.py** - Tabela de Símbolos

#### Classe `Symbol`
**Descrição:** Representa um identificador na tabela de símbolos.

**Atributos:**
- `name`: Nome do identificador (ex: "health")
- `symbol_type`: Tipo ("variable", "module", "parameter")
- `scope`: Escopo onde foi declarado (ex: "global")
- `line`: Linha de declaração
- `value`: Valor atribuído (opcional)
- `used`: Boolean - marca se foi referenciado no código

**Exemplo:**
```python
symbol = Symbol(
    name="health",
    symbol_type="variable",
    scope="global",
    line=1,
    value=100
)
```

#### Classe `Scope`
**Descrição:** Representa um escopo (bloco de código).

**Atributos:**
- `name`: Nome do escopo (ex: "global", "KEL_player")
- `parent`: Escopo pai (para aninhamento)
- `symbols`: Dicionário `{nome: Symbol}`
- `children`: Lista de escopos filhos

##### `define(self, symbol: Symbol) -> bool`
**Descrição:** Define um novo símbolo neste escopo.

**Lógica:**
```python
if symbol.name in self.symbols:
    return False  # Já existe (erro de redeclaração)
self.symbols[symbol.name] = symbol
return True
```

##### `lookup(self, name: str, recursive=True) -> Symbol | None`
**Descrição:** Procura símbolo neste escopo (e nos pais se recursive=True).

**Algoritmo:**
```
SE nome ∈ symbols deste escopo:
    RETORNAR symbol
    
SE recursive E há escopo pai:
    RETORNAR parent.lookup(name, recursive=True)
    
RETORNAR None (não encontrado)
```

**Exemplo:**
```python
# Escopo: KEL_player (filho de global)
# global: {x: Symbol("x")}
# KEL_player: {health: Symbol("health")}

# Busca 'health' em KEL_player
scope.lookup("health")        # ✓ Retorna Symbol("health")

# Busca 'x' em KEL_player (recursiva)
scope.lookup("x", recursive=True)  # ✓ Encontra em global

# Busca 'mana' (não existe)
scope.lookup("mana")          # ✗ Retorna None
```

#### Classe `SymbolTable`

##### `__init__(self)`
**Descrição:** Inicializa tabela com escopo global.

**Estrutura:**
```python
self.global_scope = Scope("global")
self.current_scope = self.global_scope
self.errors = []
self.warnings = []
```

##### `enter_scope(self, scope_name: str) -> Scope`
**Descrição:** Entra em novo escopo (cria escopo filho).

**Lógica:**
```python
new_scope = Scope(scope_name, parent=self.current_scope)
self.current_scope.children.append(new_scope)
self.current_scope = new_scope
return new_scope
```

**Exemplo:**
```python
st = SymbolTable()
# Escopo atual: global

st.enter_scope("KEL_player")
# Escopo atual: KEL_player (filho de global)
```

##### `exit_scope(self)`
**Descrição:** Sai do escopo atual, voltando ao pai.

**Lógica:**
```python
if self.current_scope.parent:
    self.current_scope = self.current_scope.parent
```

##### `declare(self, name, symbol_type='variable', line=None, value=None) -> bool`
**Descrição:** **FUNÇÃO CHAVE** - Declara novo símbolo no escopo atual.

**Algoritmo:**
```
CRIAR Symbol(name, symbol_type, current_scope.name, line, value)

SE current_scope.define(symbol) falhar:
    ADICIONAR erro: "'{name}' já foi declarado em '{current_scope.name}'"
    RETORNAR False

RETORNAR True
```

**Exemplo:**
```python
st = SymbolTable()

# Declaração bem-sucedida
st.declare("health", "variable", line=1, value=100)  # ✓ True

# Redeclaração (erro)
st.declare("health", "variable", line=3, value=50)   # ✗ False
# Erro: "Erro semântico (linha 3): 'health' já foi declarado em 'global'"
```

##### `lookup(self, name, line=None, mark_used=True) -> Symbol | None`
**Descrição:** Busca símbolo (marca como usado se encontrado).

**Lógica:**
```python
symbol = self.current_scope.lookup(name, recursive=True)

if symbol is None:
    self.errors.append(f"Erro semântico (linha {line}): '{name}' não foi declarado")
    return None

if mark_used:
    symbol.used = True  # Marca como referenciado

return symbol
```

**Exemplo:**
```python
# Declaração: FUS x := 10
st.declare("x", "variable", line=1, value=10)

# Uso: JUN x
symbol = st.lookup("x", line=3)  # ✓ Retorna Symbol, marca como usado

# Uso de variável não declarada
st.lookup("y", line=5)  # ✗ Retorna None, gera erro
```

##### `check_unused_symbols(self)`
**Descrição:** Verifica símbolos declarados mas nunca usados.

**Algoritmo:**
```
PARA CADA escopo (recursivamente):
    PARA CADA symbol em escopo.symbols:
        SE symbol.used == False E symbol.type == "variable":
            ADICIONAR warning: "variável '{name}' declarada mas não usada"
```

**Exemplo:**
```python
# Código:
# FUS x := 10
# FUS y := 20
# JUN x

st.check_unused_symbols()
# Aviso: "Aviso (linha 2): variável 'y' declarada mas não usada"
```

##### `print_table(self, scope=None, indent=0)`
**Descrição:** Imprime tabela de símbolos hierárquica.

**Saída:**
```
Escopo: global
  [✓] x: variable
  [ ] y: variable
  Escopo: KEL_player
    [✓] health: variable
    [✓] strength: variable
```

##### `has_errors(self) -> bool`
**Descrição:** Verifica se há erros semânticos.

##### `print_errors(self)`
**Descrição:** Imprime erros e avisos formatados.

---

### 4️⃣ **main.py** - Pipeline Completo (PDA + SLR)

#### Classe `PDALexerAdapter`
**Descrição:** Adapta o Autômato de Pilha (PDA) para funcionar como analisador léxico.

##### Mapeamento de Estados para Tokens
```python
STATE_TO_TOKEN = {
    'E11,Z': 'KEL',      # Reconheceu palavra "KEL"
    'D10,Z': 'LOS',      # Reconheceu palavra "LOS"
    'E12,Z': 'FOD',      # Reconheceu palavra "FOD"
    'D3,Z': 'FAH',       # Reconheceu palavra "FAH"
    'D5,Z': 'FUS',       # Reconheceu palavra "FUS"
    # ... 13 mapeamentos total
}
```

##### `__init__(self)`
**Descrição:** Inicializa PDA com alfabeto e estados finais.

**Lógica:**
```python
Q = ['A1,B2,Z', 'Z', 'B7,B8,Z', ...]  # 36 estados
Sigma = ['#', 'K', 'O', 'E', 'L', ...]  # 18 símbolos
gama = ['$', 'K', 'O', 'E', 'L', ...]   # Alfabeto de pilha
F = ['E11,Z', 'D10,Z', ...]             # 13 estados finais

self.pda = AP(Sigma, gama, DeltaFinal, 'S', F)
```

##### `tokenize(self, source_code: str) -> List[Token]`
**Descrição:** **FUNÇÃO PRINCIPAL** - Processa código via PDA e gera tokens.

**Algoritmo:**
```
SEPARAR código por '#' (quebras de linha)

PARA CADA linha:
    SEPARAR linha por espaços (palavras)
    
    PARA CADA palavra:
        estado_final = _reconhecer_palavra(palavra)
        
        SE estado_final ∈ STATE_TO_TOKEN:
            token_type = STATE_TO_TOKEN[estado_final]
            CRIAR Token(token_type, palavra, linha)
        
        SENÃO SE estado_final == 'X':
            # Palavra rejeitada pelo PDA
            token = _classificar_palavra_desconhecida(palavra)
        
        SENÃO:
            # Estado não mapeado, tratar como ID
            CRIAR Token("id", palavra, linha)

ADICIONAR Token("$", "$", linha_final)  # EOF
RETORNAR tokens
```

**Exemplo:**
```python
adapter = PDALexerAdapter()
code = "KEL player # FUS health := 100"
tokens = adapter.tokenize(code)

# Saída do PDA:
# [OK] Linha 1: 'KEL' -> Estado E11,Z -> KEL (ACEITO)
# [OK] Linha 1: 'player' -> Não reconhecido pelo PDA -> id
# [OK] Linha 2: 'FUS' -> Estado D5,Z -> FUS (ACEITO)
# [OK] Linha 2: 'health' -> Não reconhecido pelo PDA -> id
# ...
```

##### `_reconhecer_palavra(self, palavra: str) -> str`
**Descrição:** Simula execução do PDA para reconhecer palavra.

**Algoritmo:**
```
estado = 'S'  # Estado inicial

PARA CADA caractere em palavra:
    SE caractere ∉ Sigma:
        RETORNAR 'X'  # Rejeitar
    
    transicao = delta[(estado, caractere, EPSILON)]
    
    SE transicao existe:
        estado = transicao[0]
    SENÃO:
        RETORNAR 'X'  # Sem transição

SE estado ∈ estados_finais:
    RETORNAR estado
SENÃO:
    RETORNAR 'X'
```

**Exemplo:**
```python
# Palavra: "KEL"
# Caminho: S -> (K) -> B1,B2,Z -> (E) -> C2,Z -> (L) -> E11,Z (ACEITO)

# Palavra: "health"
# Caminho: S -> (h) -> Z -> (e) -> Z -> ... -> Z (NÃO FINAL) -> X
```

##### `_classificar_palavra_desconhecida(self, palavra: str, linha: int) -> Token`
**Descrição:** Classifica palavras não reconhecidas pelo PDA.

**Lógica:**
1. Se todos caracteres são dígitos → `Token(NUM)`
2. Se é operador (`:=`, `;`, etc.) → `Token(OPERADOR)`
3. Se é palavra-chave extra (`assign`, `print`) → `Token(KEYWORD)`
4. Padrão → `Token(ID)`

#### Classe `CompiladorCompleto`

##### `__init__(self, verbose=True)`
**Descrição:** Inicializa pipeline completo.

```python
self.lexer = PDALexerAdapter()
self.parser = SLRParserWithSemantics(verbose=verbose)
```

##### `compile(self, source_code: str) -> bool`
**Descrição:** **FUNÇÃO PRINCIPAL** - Executa compilação em 3 fases.

**Fluxo completo:**
```
╔════════════════════════════════════════════════════════════╗
║              FASE 1: ANÁLISE LÉXICA (PDA)                  ║
╚════════════════════════════════════════════════════════════╝
    ↓ [Processa cada palavra pelo PDA]
    ↓ [Gera lista de tokens]
    
╔════════════════════════════════════════════════════════════╗
║        FASE 2 & 3: SINTÁTICA + SEMÂNTICA (SLR)            ║
╚════════════════════════════════════════════════════════════╝
    ↓ [Parser SLR valida estrutura]
    ↓ [Ações semânticas atualizam tabela de símbolos]
    ↓ [Verifica declarações e escopos]
    
╔════════════════════════════════════════════════════════════╗
║                   RELATÓRIO FINAL                          ║
╚════════════════════════════════════════════════════════════╝
    ↓ [Imprime erros/avisos]
    ↓ [Mostra tabela de símbolos]
```

**Exemplo:**
```python
compilador = CompiladorCompleto(verbose=True)
code = "FUS health := 100 ; JUN health"
sucesso = compilador.compile(code)

# Saída:
# ==================================================================
# =          SAÍDA DO PDA (Compiladores/main.py)                  =
# ==================================================================
# [OK] Linha 1: 'FUS' -> Estado D5,Z -> FUS (ACEITO)
# [OK] Linha 1: 'health' -> Não reconhecido pelo PDA -> id
# ...
# 
# ==================================================================
# =              TOKENS GERADOS PARA O PARSER                      =
# ==================================================================
# 1. Token(FUS, 'FUS', L1)
# 2. Token(id, 'health', L1)
# ...
#
# === Analise Sintatica e Semantica SLR(1) ===
# [Semântico] Declarando 'health' = 100 (linha 1)
# ...
# [OK] ANALISE SINTATICA ACEITA!
#
# ======================================================================
# RELATORIO DE ANALISE
# ======================================================================
# [OK] Nenhum erro encontrado
```

---

### 5️⃣ **SLR.py, goto.py, first.py, follow.py** - Tabelas do Parser

#### **SLR.py** - Closures LR(0)
**Descrição:** Define 60 closures (estados) do autômato SLR(1).

**Estrutura:**
```python
closures = {
    0: {  # Estado inicial
        ("S'", (".", "S")),
        ("S", (".", "CMD", ";", "S")),
        ("CMD", (".", "LOS", "EXPR", "CMD")),
        # ... 15 itens LR(0)
    },
    
    11: ["IO -> HON."],  # Estado de redução
    12: ["IO -> print."],
    # ...
}
```

**Lógica:**
- Estados 0-10: Formato tupla com múltiplos itens (kernel + closure)
- Estados 11-59: Formato string com produções prontas para redução

**Exemplo de uso:**
```python
# No parser:
if state in self.productions:
    lhs, rhs = self.productions[state]
    # state=11 → lhs="IO", rhs=["HON"]
```

#### **goto.py** - Tabela de Transições
**Descrição:** 200+ entradas mapeando `(estado, símbolo) → próximo_estado`.

**Estrutura:**
```python
transitions = {
    (0, "S"): 1,       # Do estado 0, com 'S' vai para estado 1
    (0, "CMD"): 2,     # Do estado 0, com 'CMD' vai para estado 2
    (0, "LOS"): 3,     # Do estado 0, com 'LOS' vai para estado 3
    # ... 200+ transições
}
```

**Uso em SHIFT:**
```python
if (state, lookahead) in transitions:
    next_state = transitions[(state, lookahead)]
    stack.append(next_state)
```

**Uso em GOTO:**
```python
# Após redução para não-terminal 'lhs'
state_after_pop = stack[-1]
if (state_after_pop, lhs) in transitions:
    goto_state = transitions[(state_after_pop, lhs)]
    stack.append(goto_state)
```

#### **first.py** - Conjuntos FIRST
**Descrição:** FIRST sets para cada não-terminal (usado para parsing preditivo).

```python
FIRST = {
    "S'": {"LOS","FOD","FAH","JUN","KEL","FUS","HON","print","assign","HIM"},
    "EXPR": {"NUST","id","num","HIM","("},
    "EXPR'": {"ε","+","-","ANRK","AAN","KO"},
    # ...
}
```

**Interpretação:**
- `FIRST["EXPR"]`: Conjunto de tokens que podem iniciar uma expressão
- `"ε"` indica que pode derivar vazio (epsilon)

#### **follow.py** - Conjuntos FOLLOW
**Descrição:** FOLLOW sets para cada não-terminal (usado para decidir reduções).

```python
FOLLOW = {
    "S'": {"$"},
    "CMD": {";","$","FAH"},
    "EXPR": {"LOS","FOD","FAH","JUN","KEL",";","$",")"},
    # ...
}
```

**Uso no parser:**
```python
if state in self.productions:
    lhs, rhs = self.productions[state]
    
    # Reduz se lookahead está em FOLLOW(lhs)
    if lookahead in self.follow.get(lhs, set()):
        # Executar redução
```

---

### 6️⃣ **Compiladores/** - Autômato de Pilha (PDA)

#### **pda.py** - Classe `AP`

##### `__init__(self, Sigma, gama, delta, q0, F)`
**Descrição:** Inicializa autômato de pilha.

**Parâmetros:**
- `Sigma`: Alfabeto de entrada (caracteres)
- `gama`: Alfabeto de pilha
- `delta`: Função de transição (dicionário)
- `q0`: Estado inicial
- `F`: Estados finais

##### `run(self, entrada: str) -> bool`
**Descrição:** Executa PDA na entrada e retorna se aceita.

**Algoritmo:**
```
SEPARAR entrada por '#' (linhas)

PARA CADA linha:
    PARA CADA palavra:
        estado = q0  # Reset para cada palavra
        
        PARA CADA caractere em palavra:
            transicao = delta[(estado, caractere, EPSILON)]
            
            SE transicao existe:
                estado = transicao[0]
            SENÃO:
                estado = 'X'  # Rejeitar
                BREAK
        
        SE estado ∉ estados_finais:
            estado = 'X'
        
        ADICIONAR caminho à FITA
        ADICIONAR (linha, estado, palavra) à TS

RETORNAR True SE todos estados finais válidos
```

**Exemplo:**
```python
pda = AP(Sigma, gama, DeltaFinal, 'S', F)
entrada = "KEL # FOD"
resultado = pda.run(entrada)

# Saída:
# ==================================================
# FITA (Caminhos Completos): ['S -> B1,B2,Z -> C2,Z -> E11,Z', 'S -> B5,B7,B9,Z -> Z -> D5,Z']
# 
# Tabela de Simbolos (TS):
#   1. Linha 1: 'KEL' -> E11,Z
#   2. Linha 2: 'FOD' -> D5,Z
```

#### **delta.py** - `DeltaFinal`
**Descrição:** Dicionário com 687 transições do PDA.

```python
DeltaFinal = {
    ('S', 'K', EPSILON): ('B1,B2,Z', 'K'),
    ('S', 'L', EPSILON): ('B7,B8,Z', 'L'),
    # ... 687 transições
}
```

**Formato:** `(estado_atual, símbolo_entrada, topo_pilha) : (próximo_estado, símbolo_pilha)`

#### **constants.py**
```python
EPSILON = None  # Representa símbolo vazio
```

---

## 📝 Exemplos de Uso Completos

### Exemplo 1: Declaração Simples

**Código:**
```fantasy
FUS health := 100
```

**Execução:**
```python
from lexer import Lexer
from parser_integrated import SLRParserWithSemantics

# Fase 1: Léxico
lexer = Lexer("FUS health := 100")
tokens = lexer.tokenize()
# [Token(FUS), Token(id, "health"), Token(:=), Token(num, "100", value=100), Token($)]

# Fase 2 & 3: Sintático + Semântico
parser = SLRParserWithSemantics(verbose=True)
sucesso = parser.parse(tokens)

# Resultado:
# [Semântico] Declarando 'health' = 100 (linha 1)
# [OK] ANALISE SINTATICA ACEITA!
#
# Tabela de Símbolos:
# Escopo: global
#   [✓] health: variable (valor=100)
```

### Exemplo 2: Sequência de Comandos

**Código:**
```fantasy
FUS x := 10 ; FUS y := 20 ; assign x := x + y
```

**Análise:**
1. **Léxico:** Gera 13 tokens
2. **Sintático:** Valida estrutura `CMD ; CMD ; CMD`
3. **Semântico:**
   - Declara `x = 10`
   - Declara `y = 20`
   - Verifica se `x` e `y` existem
   - Atualiza `x = (10 + 20)`

**Tabela de Símbolos Final:**
```
global:
  [✓] x: variable (valor=30)
  [✓] y: variable (valor=20)
```

### Exemplo 3: Módulo KEL

**Código:**
```fantasy
KEL player FUS strength := 50
```

**Análise Semântica:**
```python
# 1. Parser encontra "KEL player"
symbol_table.enter_scope("KEL_player")

# 2. Declara módulo
symbol_table.declare("player", symbol_type="module", line=1)

# 3. Dentro do escopo, declara strength
symbol_table.declare("strength", symbol_type="variable", line=1, value=50)

# 4. Ao sair do módulo
symbol_table.exit_scope()
```

**Estrutura de Escopos:**
```
global:
  [✓] player: module
    KEL_player:
      [✓] strength: variable (valor=50)
```

### Exemplo 4: Erro Semântico - Variável Não Declarada

**Código:**
```fantasy
assign mana := 100
```

**Resultado:**
```
[X] ERROS ENCONTRADOS:
  - Erro semântico (linha 1): 'mana' não foi declarado

TABELA DE SIMBOLOS
Escopo: global
  (vazia)
```

**Explicação:** Tentou atribuir valor a `mana` sem declará-la primeiro com `FUS`.

### Exemplo 5: Aviso - Variável Não Usada

**Código:**
```fantasy
FUS unused_var := 10 ; FUS x := 20 ; JUN x
```

**Resultado:**
```
[OK] Nenhum erro encontrado

[!] AVISOS:
  - Aviso (linha 1): variável 'unused_var' declarada mas não usada

TABELA DE SIMBOLOS
Escopo: global
  [ ] unused_var: variable
  [✓] x: variable
```

### Exemplo 6: Expressão Aritmética Complexa

**Código:**
```fantasy
FUS result := 10 + 20 - 5
```

**Síntese de Atributos:**
```
FACTOR -> num (10)       → atributo: 10
TERM -> FACTOR           → atributo: 10
OP -> +                  → atributo: "+"
FACTOR -> num (20)       → atributo: 20
TERM -> FACTOR           → atributo: 20
EXPR' -> OP TERM EXPR'   → atributo: {"op": "+", "right": 20}
OP -> -                  → atributo: "-"
FACTOR -> num (5)        → atributo: 5
TERM -> FACTOR           → atributo: 5
EXPR' -> OP TERM EXPR'   → atributo: {"op": "-", "right": 5}
EXPR -> TERM EXPR'       → atributo: "(10 + (20 - 5))"
```

**Valor Final:** `result = "(10 + (20 - 5))"` (representação da expressão)

### Exemplo 7: Pipeline Completo com PDA

**Código:**
```fantasy
KEL dragon # FUS health := 500 # JUN health
```

**Saída Completa:**
```
==================================================================
=          SAÍDA DO PDA (Compiladores/main.py)                  =
==================================================================

 Processando entrada no PDA...
Entrada: KEL dragon # FUS health := 500 # JUN health

[OK] Linha 1: 'KEL' -> Estado E11,Z -> KEL (ACEITO)
  Linha 1: 'dragon' -> Não reconhecido pelo PDA -> id
[OK] Linha 2: 'FUS' -> Estado D5,Z -> FUS (ACEITO)
  Linha 2: 'health' -> Não reconhecido pelo PDA -> id
  Linha 2: ':=' -> Não reconhecido pelo PDA -> :=
  Linha 2: '500' -> Não reconhecido pelo PDA -> num
[OK] Linha 3: 'JUN' -> Estado D4,Z -> JUN (ACEITO)
  Linha 3: 'health' -> Não reconhecido pelo PDA -> id

==================================================================
 TABELA DE SÍMBOLOS DO PDA:
==================================================================
Linha    Palavra         Estado Final    Status    
==================================================================
1        KEL             E11,Z           [OK] ACEITO
1        dragon          X               [X] REJEITADO
2        FUS             D5,Z            [OK] ACEITO
2        health          X               [X] REJEITADO
...

[OK] PDA processou 7 palavras
[OK] Gerados 8 tokens (incluindo EOF)

==================================================================
=              TOKENS GERADOS PARA O PARSER                      =
==================================================================
  1. Token(KEL, 'KEL', L1)
  2. Token(id, 'dragon', L1)
  3. Token(FUS, 'FUS', L2)
  4. Token(id, 'health', L2)
  5. Token(:=, ':=', L2)
  6. Token(num, '500', L2)
  7. Token(JUN, 'JUN', L3)
  8. Token(id, 'health', L3)

================================================================================
FASE 2 & 3: ANÁLISE SINTÁTICA E SEMÂNTICA (SLR)
================================================================================

=== Analise Sintatica e Semantica SLR(1) ===

[Semântico] Definindo módulo 'dragon' (linha 1)
[Semântico] Declarando 'health' = 500 (linha 2)
[Semântico] I/O com 'health' (linha 3)

[OK] ANALISE SINTATICA ACEITA!

======================================================================
RELATORIO DE ANALISE
======================================================================

[OK] Nenhum erro encontrado

======================================================================
TABELA DE SIMBOLOS
======================================================================
Escopo: global
  [✓] dragon: module
  Escopo: KEL_dragon
    [✓] health: variable
======================================================================
```

---

## 📖 Gramática da Linguagem

### Produções BNF

```bnf
S ::= CMD ; S
    | CMD

CMD ::= LOS EXPR CMD                    # if
     | FOD CMD FAH EXPR                 # while
     | FAH CMD FAH EXPR                 # for
     | IO id                            # input/output
     | JUN EXPR                         # return
     | LHS := EXPR                      # atribuição
     | KEL id CMD                       # módulo
     | FUS id := EXPR                   # declaração

IO ::= HON | print

LHS ::= assign id
      | HIM . id

EXPR ::= TERM EXPR'

EXPR' ::= OP TERM EXPR'
        | ε

OP ::= + | - | ANRK | AAN | KO

TERM ::= UNARY | FACTOR

UNARY ::= NUST TERM

FACTOR ::= id
         | num
         | HIM . id
         | ( EXPR )
```

### Conjuntos FIRST e FOLLOW

**FIRST:**
```
FIRST(S) = {LOS, FOD, FAH, JUN, KEL, FUS, HON, print, assign, HIM}
FIRST(EXPR) = {NUST, id, num, HIM, (}
FIRST(EXPR') = {ε, +, -, ANRK, AAN, KO}
FIRST(TERM) = {NUST, id, num, HIM, (}
FIRST(FACTOR) = {id, num, HIM, (}
```

**FOLLOW:**
```
FOLLOW(S) = {$}
FOLLOW(CMD) = {;, $, FAH}
FOLLOW(EXPR) = {LOS, FOD, FAH, JUN, KEL, ;, $, )}
FOLLOW(EXPR') = {LOS, FOD, FAH, JUN, KEL, ;, $, )}
FOLLOW(TERM) = {+, -, ANRK, AAN, KO, ...}
FOLLOW(FACTOR) = {+, -, ANRK, AAN, KO, ...}
```

---

## 🚀 Como Usar

### Instalação
```powershell
# Clonar repositório
git clone <repo-url>
cd "Analisador Sintatico"
```

### Uso Básico

#### 1. Análise Léxica Apenas
```python
from lexer import Lexer

code = "FUS health := 100"
lexer = Lexer(code)
tokens = lexer.tokenize()
lexer.print_tokens()
```

#### 2. Compilação Completa
```python
from main import CompiladorCompleto

compilador = CompiladorCompleto(verbose=True)
code = "FUS x := 10 ; JUN x"
sucesso = compilador.compile(code)
```

#### 3. Parser Direto (sem PDA)
```python
from lexer import Lexer
from parser_integrated import SLRParserWithSemantics, Token

lexer = Lexer("FUS x := 10")
tokens = lexer.tokenize()

parser = SLRParserWithSemantics(verbose=True)
sucesso = parser.parse(tokens)
parser.print_report()
```

### Executar Exemplos
```powershell
# Exemplos do lexer
python lexer.py

# Exemplos do parser
python parser_integrated.py

# Compilador completo
python main.py

# Testes de semântica
python teste_semantica.py
```

---

## 🧪 Casos de Teste

### Teste 1: Declaração Válida ✓
```fantasy
FUS health := 100
```
**Esperado:** Aceito, `health` declarado com valor 100

### Teste 2: Erro Sintático ✗
```fantasy
FUS x 10
```
**Esperado:** Erro - falta operador `:=`

### Teste 3: Erro Semântico ✗
```fantasy
assign y := 50
```
**Esperado:** Erro - `y` não foi declarado

### Teste 4: Programa Complexo ✓
```fantasy
KEL player FUS health := 100 ; FUS mana := 50 ; assign health := health - 10
```
**Esperado:** Aceito
- Módulo `player` criado
- Variáveis `health` e `mana` declaradas
- `health` atualizado para 90

### Teste 5: Aviso - Variável Não Usada ⚠
```fantasy
FUS unused := 0 ; FUS x := 10 ; JUN x
```
**Esperado:** Aviso - `unused` declarado mas não usado

---

## 🛠️ Estrutura de Arquivos

```
Analisador Sintatico/
│
├── lexer.py                    # Analisador léxico
├── parser_integrated.py        # Parser SLR(1) + semântica
├── symbol_table.py             # Tabela de símbolos
├── main.py                     # Pipeline PDA + SLR
├── SLR.py                      # Closures LR(0)
├── goto.py                     # Tabela de transições
├── first.py                    # Conjuntos FIRST
├── follow.py                   # Conjuntos FOLLOW
├── terminais.py                # Símbolos terminais
├── nao_terminais.py            # Símbolos não-terminais
├── regrasSintáticas.txt        # Gramática BNF
├── teste_semantica.py          # Suite de testes
│
└── Compiladores/
    ├── pda.py                  # Autômato de pilha
    ├── delta.py                # Transições do PDA
    ├── constants.py            # Constantes (EPSILON)
    └── main.py                 # Executável do PDA
```

---

## 📚 Referências

- **Compiladores: Princípios, Técnicas e Ferramentas** (Aho, Sethi, Ullman)
- **Modern Compiler Implementation** (Appel)
- **SLR Parsing:** Simple LR Parser
- **Análise Sintática Bottom-Up:** Shift-Reduce Parsing

---

## 👥 Contribuidores

Projeto desenvolvido como parte do curso de Compiladores.

---

## 📄 Licença

Este projeto é de código aberto para fins educacionais.

---

**Última atualização:** 02/12/2025
