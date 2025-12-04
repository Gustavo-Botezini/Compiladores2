# 🎯 Principais Funções do Compilador - Apresentação

## 📑 Índice Rápido
1. [Análise Léxica](#1-análise-léxica-lexerpy)
2. [Análise Sintática](#2-análise-sintática-parser_integratedpy)
3. [Análise Semântica](#3-análise-semântica-symbol_tablepy)
4. [Pipeline Completo](#4-pipeline-completo-mainpy)
5. [Demonstração Prática](#5-demonstração-prática)

---

## 1. Análise Léxica (lexer.py)

### 🔹 `tokenize()` - Função Principal do Lexer

**O que faz:** Transforma código fonte em uma sequência de tokens

**Algoritmo:**
```python
def tokenize(self):
    """Converte código fonte em lista de tokens"""
    
    ENQUANTO não chegou ao fim:
        1. Pular espaços em branco
        2. Pular comentários (# e /* */)
        3. Identificar tipo de caractere:
           - Dígito → ler número completo
           - Letra → ler palavra (keyword ou ID)
           - Operador → reconhecer operador
           - Outro → gerar erro léxico
    
    ADICIONAR token EOF ($)
    RETORNAR lista de tokens
```

**Exemplo de Entrada:**
```fantasy
FUS health := 100
```

**Exemplo de Saída:**
```python
[
    Token(type='FUS', lexeme='FUS', line=1, column=1),
    Token(type='id', lexeme='health', line=1, column=5),
    Token(type=':=', lexeme=':=', line=1, column=12),
    Token(type='num', lexeme='100', line=1, column=15, value=100),
    Token(type='$', lexeme='$', line=1, column=19)
]
```

**Detecção de Erros:**
```python
# Código com erro: FUS x := @10
# Saída: ERRO LÉXICO (Linha 1, Coluna 14): Caractere inválido '@'
```

---

### 🔹 `read_identifier_or_keyword()` - Reconhecimento de Palavras

**O que faz:** Diferencia palavras-chave de identificadores

**Lógica:**
```python
def read_identifier_or_keyword(self):
    # 1. Ler caracteres alfanuméricos
    text = ""
    while char.isalnum() or char == '_':
        text += char
        avançar()
    
    # 2. Verificar se é palavra reservada
    if text in KEYWORDS:
        return Token(KEYWORDS[text], text, linha, coluna)
    else:
        return Token('id', text, linha, coluna)
```

**Exemplos:**
| Entrada | Tipo Reconhecido | Explicação |
|---------|------------------|------------|
| `LOS` | Palavra-chave | Está em `KEYWORDS` |
| `health` | Identificador | Não está em `KEYWORDS` |
| `FUS` | Palavra-chave | Declaração |
| `x123` | Identificador | Variável válida |

---

## 2. Análise Sintática (parser_integrated.py)

### 🔹 `parse()` - Parser SLR(1) Principal

**O que faz:** Valida estrutura gramatical usando autômato SLR(1)

**Algoritmo Completo:**
```python
def parse(self, tokens):
    stack = [0]              # Pilha de estados
    token_index = 0
    current_token = tokens[0]
    
    LOOP INFINITO:
        state = stack[-1]
        lookahead = current_token.type
        
        # ═══════════════════════════════════════
        # CASO 1: ACEITAÇÃO
        # ═══════════════════════════════════════
        if state == 1 and lookahead == '$':
            verificar_simbolos_nao_usados()
            return True  # ✓ Código aceito
        
        # ═══════════════════════════════════════
        # CASO 2: SHIFT (Empilhar terminal)
        # ═══════════════════════════════════════
        if (state, lookahead) in transitions:
            next_state = transitions[(state, lookahead)]
            
            stack.append(next_state)
            symbols.append(lookahead)
            attributes.append(current_token)
            
            token_index += 1
            current_token = tokens[token_index]
            continue
        
        # ═══════════════════════════════════════
        # CASO 3: REDUCE (Aplicar produção)
        # ═══════════════════════════════════════
        if state in productions:
            lhs, rhs = productions[state]
            
            if lookahead in FOLLOW[lhs]:
                # 1. Coletar atributos dos símbolos
                prod_attributes = attributes[-len(rhs):]
                
                # 2. EXECUTAR AÇÃO SEMÂNTICA ⚡
                synthesized = semantic_action(lhs, rhs, prod_attributes)
                
                # 3. Desempilhar símbolos
                for _ in range(len(rhs)):
                    stack.pop()
                    symbols.pop()
                    attributes.pop()
                
                # 4. GOTO (transição com não-terminal)
                state_after = stack[-1]
                goto_state = transitions[(state_after, lhs)]
                
                stack.append(goto_state)
                symbols.append(lhs)
                attributes.append(synthesized)
                continue
        
        # ═══════════════════════════════════════
        # CASO 4: ERRO SINTÁTICO
        # ═══════════════════════════════════════
        error = f"Token inesperado '{current_token.lexeme}'"
        errors.append(error)
        return False  # ✗ Rejeitar código
```

**Exemplo de Execução Passo a Passo:**

```
Código: FUS x := 10

╔═══════╦════════════════╦═════════╦═════════════╦══════════════════╗
║ Passo ║ Stack          ║ Estado  ║ Token       ║ Ação             ║
╠═══════╬════════════════╬═════════╬═════════════╬══════════════════╣
║   1   ║ [0]            ║    0    ║ FUS         ║ SHIFT → 10       ║
║   2   ║ [0, 10]        ║   10    ║ id          ║ SHIFT → 27       ║
║   3   ║ [0, 10, 27]    ║   27    ║ :=          ║ SHIFT → 51       ║
║   4   ║ [0, 10, 27, 51]║   51    ║ num         ║ SHIFT → 22       ║
║   5   ║ [0,..., 22]    ║   22    ║ $           ║ REDUCE FACTOR    ║
║   6   ║ [0,..., 19]    ║   19    ║ $           ║ REDUCE TERM      ║
║   7   ║ [0,..., 17]    ║   17    ║ $           ║ REDUCE EXPR      ║
║   8   ║ [0, 10, 27, 51]║   51    ║ EXPR        ║ GOTO → 58        ║
║   9   ║ [0, 10, 27, 58]║   58    ║ $           ║ REDUCE CMD       ║
║  10   ║ [0, 2]         ║    2    ║ $           ║ REDUCE S         ║
║  11   ║ [0, 1]         ║    1    ║ $           ║ ✓ ACEITAR        ║
╚═══════╩════════════════╩═════════╩═════════════╩══════════════════╝
```

---

### 🔹 `semantic_action()` - Ações Semânticas Integradas

**O que faz:** Executa verificações semânticas durante as reduções

**Principais Ações:**

#### **1️⃣ Declaração de Variável (FUS id := EXPR)**
```python
# Produção: CMD -> FUS id := EXPR
if production_lhs == "CMD" and rhs == ["FUS", "id", ":=", "EXPR"]:
    var_name = attributes[1].lexeme      # "health"
    expr_value = attributes[3]            # 100
    
    # DECLARAR na tabela de símbolos
    symbol_table.declare(var_name, "variable", line, expr_value)
    
    print(f"✓ Declarando '{var_name}' = {expr_value}")
```

**Exemplo:**
```fantasy
FUS health := 100
→ Tabela de Símbolos: {health: variable, valor=100}
```

---

#### **2️⃣ Atribuição (assign id := EXPR)**
```python
# Produção: CMD -> LHS := EXPR
if production_lhs == "CMD" and rhs[1] == ":=":
    var_name = attributes[0]["name"]     # "health"
    new_value = attributes[2]             # 50
    
    # VERIFICAR se foi declarada
    symbol = symbol_table.lookup(var_name, line)
    
    if symbol:
        symbol.value = new_value  # Atualizar valor
        print(f"✓ Atribuindo '{var_name}' = {new_value}")
    else:
        error = f"✗ '{var_name}' não foi declarado"
        errors.append(error)
```

**Exemplo com Erro:**
```fantasy
assign mana := 50
→ ERRO SEMÂNTICO: 'mana' não foi declarado
```

---

#### **3️⃣ Módulo (KEL id CMD)**
```python
# Produção: CMD -> KEL id CMD
if production_lhs == "CMD" and rhs[0] == "KEL":
    module_name = attributes[1].lexeme    # "player"
    
    # CRIAR novo escopo
    symbol_table.enter_scope(f"KEL_{module_name}")
    
    # DECLARAR módulo no escopo pai
    symbol_table.declare(module_name, "module", line)
    
    print(f"✓ Entrando no módulo '{module_name}'")
```

**Exemplo:**
```fantasy
KEL player FUS strength := 50
→ Escopo criado: KEL_player
→ Variável 'strength' declarada no módulo
```

---

#### **4️⃣ Uso de Variável (FACTOR -> id)**
```python
# Produção: FACTOR -> id
if production_lhs == "FACTOR" and rhs[0] == "id":
    var_name = attributes[0].lexeme       # "health"
    
    # BUSCAR na tabela (marca como usado)
    symbol = symbol_table.lookup(var_name, line)
    
    if symbol:
        return symbol.value  # Retorna valor
    else:
        error = f"✗ '{var_name}' não declarado"
        errors.append(error)
```

**Exemplo:**
```fantasy
JUN health
→ Busca 'health' na tabela
→ Se não existe: ERRO
```

---

## 3. Análise Semântica (symbol_table.py)

### 🔹 `declare()` - Declaração de Símbolos

**O que faz:** Adiciona identificador na tabela, verificando duplicatas

**Algoritmo:**
```python
def declare(self, name, symbol_type='variable', line=None, value=None):
    # 1. Criar símbolo
    symbol = Symbol(name, symbol_type, current_scope, line, value)
    
    # 2. Verificar se já existe no escopo atual
    if name in current_scope.symbols:
        error = f"'{name}' já foi declarado em '{current_scope.name}'"
        errors.append(error)
        return False
    
    # 3. Adicionar à tabela
    current_scope.symbols[name] = symbol
    return True
```

**Exemplo de Sucesso:**
```python
declare("health", "variable", line=1, value=100)
# ✓ Símbolo adicionado ao escopo atual
```

**Exemplo de Erro (Redeclaração):**
```python
declare("health", "variable", line=1, value=100)  # ✓
declare("health", "variable", line=3, value=50)   # ✗
# Erro: 'health' já foi declarado em 'global'
```

---

### 🔹 `lookup()` - Busca de Símbolos

**O que faz:** Procura símbolo no escopo atual e pais (busca hierárquica)

**Algoritmo:**
```python
def lookup(self, name, line=None, mark_used=True):
    # 1. Buscar no escopo atual
    symbol = current_scope.lookup(name, recursive=True)
    
    # 2. Se não encontrou, gerar erro
    if symbol is None:
        error = f"'{name}' não foi declarado"
        errors.append(error)
        return None
    
    # 3. Marcar como usado (para avisos)
    if mark_used:
        symbol.used = True
    
    return symbol
```

**Exemplo com Escopo Aninhado:**
```
Global: {x: 10}
  └─ KEL_player: {health: 100}
  
# Dentro de KEL_player:
lookup("health")  → ✓ Encontra no escopo atual
lookup("x")       → ✓ Encontra no escopo pai (global)
lookup("mana")    → ✗ Não encontrado (erro)
```

---

### 🔹 `enter_scope()` / `exit_scope()` - Gerenciamento de Escopos

**O que faz:** Controla hierarquia de escopos (módulos, funções)

**Lógica:**
```python
def enter_scope(self, scope_name):
    # Criar escopo filho
    new_scope = Scope(scope_name, parent=current_scope)
    current_scope.children.append(new_scope)
    current_scope = new_scope
    return new_scope

def exit_scope(self):
    # Voltar ao escopo pai
    if current_scope.parent:
        current_scope = current_scope.parent
```

**Exemplo de Uso:**
```python
# Código: KEL player FUS health := 100

symbol_table.enter_scope("KEL_player")  # Entra no módulo
declare("health", "variable", 1, 100)    # Declara no módulo
symbol_table.exit_scope()                # Volta ao global

# Estrutura:
# Global
#   └─ KEL_player
#        └─ health: variable
```

---

### 🔹 `check_unused_symbols()` - Detecção de Código Morto

**O que faz:** Encontra variáveis declaradas mas nunca usadas

**Algoritmo:**
```python
def check_unused_symbols(self):
    for scope in all_scopes:
        for name, symbol in scope.symbols.items():
            if symbol.type == 'variable' and not symbol.used:
                warning = f"Aviso: '{name}' declarado mas não usado"
                warnings.append(warning)
```

**Exemplo:**
```fantasy
FUS unused := 0
FUS x := 10
JUN x

→ Aviso: variável 'unused' declarada mas não usada (linha 1)
```

---

## 4. Pipeline Completo (main.py)

### 🔹 `compile()` - Compilação em 3 Fases

**O que faz:** Executa pipeline completo de compilação

**Fluxo:**
```python
def compile(self, source_code):
    # ═══════════════════════════════════════════════
    # FASE 1: ANÁLISE LÉXICA (PDA)
    # ═══════════════════════════════════════════════
    print("FASE 1: ANÁLISE LÉXICA")
    tokens = lexer.tokenize(source_code)
    
    if lexer.has_errors():
        print("✗ Erros léxicos encontrados")
        return False
    
    print(f"✓ Gerados {len(tokens)} tokens")
    
    # ═══════════════════════════════════════════════
    # FASE 2 & 3: SINTÁTICA + SEMÂNTICA (SLR)
    # ═══════════════════════════════════════════════
    print("\nFASE 2 & 3: ANÁLISE SINTÁTICA E SEMÂNTICA")
    sucesso = parser.parse(tokens)
    
    # ═══════════════════════════════════════════════
    # RELATÓRIO FINAL
    # ═══════════════════════════════════════════════
    parser.print_report()
    
    return sucesso
```

---

### 🔹 `PDALexerAdapter.tokenize()` - Integração com PDA

**O que faz:** Usa autômato de pilha para reconhecer palavras-chave

**Algoritmo:**
```python
def tokenize(self, source_code):
    # Separar por linhas (#) e palavras
    for palavra in palavras:
        # 1. Executar PDA caractere por caractere
        estado_final = _reconhecer_palavra(palavra)
        
        # 2. Mapear estado final para tipo de token
        if estado_final in STATE_TO_TOKEN:
            token_type = STATE_TO_TOKEN[estado_final]
            tokens.append(Token(token_type, palavra, linha))
        
        # 3. Se rejeitado, classificar manualmente
        elif estado_final == 'X':
            token = _classificar_palavra_desconhecida(palavra)
            tokens.append(token)
    
    return tokens
```

**Mapeamento de Estados:**
```python
STATE_TO_TOKEN = {
    'E11,Z': 'KEL',     # PDA reconheceu "KEL"
    'D10,Z': 'LOS',     # PDA reconheceu "LOS"
    'D5,Z': 'FUS',      # PDA reconheceu "FUS"
    # ... 13 mapeamentos
}
```

---

## 5. Demonstração Prática

### 📋 Exemplo Completo: Declaração com Uso

**Código:**
```fantasy
FUS health := 100 ; assign health := health - 10 ; JUN health
```

**Execução Detalhada:**

#### **FASE 1: Léxica**
```
Tokens gerados:
1. FUS (palavra-chave)
2. health (identificador)
3. := (operador)
4. 100 (número)
5. ; (separador)
6. assign (palavra-chave)
7. health (identificador)
8. := (operador)
9. health (identificador)
10. - (operador)
11. 10 (número)
12. ; (separador)
13. JUN (palavra-chave)
14. health (identificador)
15. $ (EOF)
```

#### **FASE 2: Sintática**
```
Parser SLR(1):
- CMD -> FUS id := EXPR        ✓ Estrutura válida
- CMD -> assign id := EXPR      ✓ Estrutura válida
- CMD -> JUN EXPR               ✓ Estrutura válida
- S -> CMD ; CMD ; CMD          ✓ Aceito
```

#### **FASE 3: Semântica**
```
Ação 1: FUS health := 100
  → Declarar 'health' no escopo global
  → Valor inicial: 100
  
Ação 2: assign health := health - 10
  → Buscar 'health' (✓ encontrado)
  → Marcar como usado
  → Atualizar valor: 90
  
Ação 3: JUN health
  → Buscar 'health' (✓ encontrado)
  → Marcar como usado
  → Retornar valor: 90
```

#### **Tabela de Símbolos Final:**
```
Escopo: global
  [✓] health: variable (valor=90, usado=true)
```

#### **Relatório:**
```
✓ Compilação bem-sucedida
✓ Nenhum erro encontrado
✓ Nenhum aviso
```

---

### 📋 Exemplo com Erro: Variável Não Declarada

**Código:**
```fantasy
assign mana := 50
```

**Execução:**

#### **FASE 1: Léxica** ✓
```
Tokens: [assign, mana, :=, 50, $]
```

#### **FASE 2: Sintática** ✓
```
Parser: CMD -> assign id := EXPR (estrutura correta)
```

#### **FASE 3: Semântica** ✗
```
Ação: assign mana := 50
  → Buscar 'mana' na tabela
  → ✗ NÃO ENCONTRADO
  → GERAR ERRO SEMÂNTICO
```

#### **Relatório:**
```
✗ ERROS ENCONTRADOS:
  - Erro semântico (linha 1): 'mana' não foi declarado

Tabela de Símbolos:
  Escopo: global
    (vazia)
```

---

## 🎯 Resumo das Funções-Chave

| Módulo | Função | Responsabilidade |
|--------|--------|------------------|
| **lexer.py** | `tokenize()` | Converter código em tokens |
| **lexer.py** | `read_identifier_or_keyword()` | Diferenciar keywords de IDs |
| **parser_integrated.py** | `parse()` | Validar sintaxe (SLR) |
| **parser_integrated.py** | `semantic_action()` | Executar análise semântica |
| **symbol_table.py** | `declare()` | Adicionar símbolo à tabela |
| **symbol_table.py** | `lookup()` | Buscar símbolo (hierárquico) |
| **symbol_table.py** | `check_unused_symbols()` | Detectar código morto |
| **main.py** | `compile()` | Pipeline completo (3 fases) |

---

## 📊 Estatísticas do Projeto

- **Linhas de código:** ~2.500
- **Módulos:** 8 principais
- **Funções documentadas:** 25+
- **Estados SLR:** 60
- **Transições GOTO:** 200+
- **Palavras-chave:** 14
- **Produções gramaticais:** 25

---

## 🚀 Como Demonstrar

### 1️⃣ Demonstração Básica (2 minutos)
```python
from main import CompiladorCompleto

compilador = CompiladorCompleto(verbose=True)
compilador.compile("FUS health := 100")
```

### 2️⃣ Demonstração com Erro (3 minutos)
```python
compilador.compile("assign mana := 50")  # Erro semântico
```

### 3️⃣ Demonstração Completa (5 minutos)
```python
code = """
KEL player
FUS health := 100
FUS mana := 50
assign health := health - 10
JUN health
"""
compilador.compile(code)
```

---

**Preparado para apresentação! 🎤**
