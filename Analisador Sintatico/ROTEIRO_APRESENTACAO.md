# 🎯 Roteiro de Apresentação - Analisador Sintático SLR(1)

## ⏱️ Duração Estimada: 15-20 minutos

---

## 📋 ESTRUTURA DA APRESENTAÇÃO

### 1. INTRODUÇÃO (2 minutos)
### 2. ARQUITETURA DO SISTEMA (3 minutos)
### 3. DEMONSTRAÇÃO PRÁTICA (5 minutos)
### 4. ANÁLISE TÉCNICA (5 minutos)
### 5. CONCLUSÃO (2 minutos)

---

## 🎬 1. INTRODUÇÃO (2 minutos)

### O que é o projeto?
*"Desenvolvemos um compilador completo em 3 fases para uma linguagem de programação customizada com temática de RPG/Skyrim."*

### Objetivos principais:
- ✅ Implementar um **analisador léxico** usando Autômato de Pilha (PDA)
- ✅ Implementar um **analisador sintático SLR(1)** (bottom-up parser)
- ✅ Integrar **análise semântica** com tabela de símbolos
- ✅ Criar pipeline completo: Léxico → Sintático → Semântico

### Linguagem customizada:
*"A linguagem usa palavras-chave inspiradas em Skyrim/Elder Scrolls:"*

| Keyword | Significado | Exemplo |
|---------|-------------|---------|
| `FUS` | Declaração com atribuição | `FUS x := 10` |
| `LOS` | Estrutura condicional (if) | `LOS x > 0 CMD` |
| `FOD...FAH` | Loop while | `FOD x < 10 FAH CMD` |
| `KEL` | Módulo/namespace | `KEL main CMD` |
| `HIM` | Acesso a membro (this/self) | `HIM . atributo` |
| `HON` | Input | `HON x` |
| `print` | Output | `print x` |
| `JUN` | Return | `JUN 42` |

---

## 🏗️ 2. ARQUITETURA DO SISTEMA (3 minutos)

### 2.1 Visão Geral do Pipeline

```
┌─────────────────┐
│  CÓDIGO FONTE   │  "FUS soma := 10 + 20"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FASE 1: PDA    │  Análise Léxica
│  (Léxico)       │  → Lista de Tokens
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FASE 2: SLR(1) │  Análise Sintática
│  (Sintático)    │  → Validação Gramática
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FASE 3: Tabela │  Análise Semântica
│  de Símbolos    │  → Declarações, Escopos
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RESULTADO      │  [OK] ou [X] + Erros
└─────────────────┘
```

### 2.2 Componentes Principais

#### **A) Analisador Léxico (PDA)**
- **Arquivo:** `Compiladores/pda.py`
- **Técnica:** Autômato de Pilha (Pushdown Automaton)
- **Estados:** 36 estados (Q), 13 estados finais (F)
- **Função:** Reconhecer palavras-chave da linguagem (KEL, LOS, FOD, etc)
- **Saída:** Lista de tokens tipados

```python
# Exemplo de saída do PDA:
[OK] 'FUS' -> Estado D5,Z -> FUS (ACEITO)
[OK] 'KEL' -> Estado E11,Z -> KEL (ACEITO)
```

#### **B) Analisador Sintático (SLR)**
- **Arquivos:** `SLR.py`, `goto.py`, `first.py`, `follow.py`
- **Técnica:** SLR(1) - Simple LR Parser (bottom-up)
- **Estados:** 60 estados (closures 0-59)
- **Transições:** 200+ entradas na tabela GOTO
- **Gramática:** 25 regras de produção (BNF)

**Arquivos de configuração:**
- `SLR.py` → 60 LR(0) closures (máquina de estados)
- `goto.py` → Tabela de transições SHIFT/GOTO
- `first.py` → Conjuntos FIRST para não-terminais
- `follow.py` → Conjuntos FOLLOW (decisões de redução)
- `regrasSintáticas.txt` → Gramática BNF (25 produções)

#### **C) Análise Semântica**
- **Arquivo:** `symbol_table.py`
- **Recursos:**
  - Tabela de símbolos com escopos hierárquicos
  - Detecção de variáveis não declaradas
  - Detecção de redeclaração
  - Detecção de variáveis não utilizadas
  - Suporte a módulos (`KEL`)

---

## 💻 3. DEMONSTRAÇÃO PRÁTICA (5 minutos)

### 3.1 Preparação
*"Vamos executar o compilador e ver todas as fases em ação."*

```powershell
python main.py
```

### 3.2 Exemplo 1: Código Simples (SUCESSO)
*Mostrar no arquivo `main.py` linha ~340:*

```python
code = 'FUS soma := 10 + 20'
```

**O que esperar:**
1. **FASE 1 (PDA):** Reconhece `FUS`, gera tokens
2. **FASE 2 (SLR):** Valida sintaxe com SHIFT/REDUCE
3. **FASE 3:** Declara variável `soma` na tabela de símbolos
4. **Resultado:** `[OK] COMPILACAO BEM-SUCEDIDA`

### 3.3 Exemplo 2: Expressão Complexa
*Modificar código:*

```python
code = 'FUS calc := ( 10 + 20 ) - HIM . valor'
```

**Destacar:**
- Parênteses: `( 10 + 20 )`
- Acesso a membro: `HIM . valor`
- Operações aninhadas
- Parser trata precedência corretamente

### 3.4 Exemplo 3: Erro Semântico
*Modificar código:*

```python
code = 'FUS x := y + 10'  # 'y' não declarado
```

**Mostrar:**
```
[X] ERRO SEMÂNTICO (Linha 1): Variável 'y' não declarada
TABELA DE SÍMBOLOS:
  [OK] x : unknown (Linha 1) - USADO
```

### 3.5 Exemplo 4: Módulo com Escopo
*Criar exemplo mais complexo:*

```python
code = 'KEL modulo FUS x := 10'
```

**Mostrar:**
- Entrada de escopo: `[OK] Entrando no escopo 'modulo'`
- Declaração dentro do módulo
- Hierarquia de escopos

---

## 🔬 4. ANÁLISE TÉCNICA (5 minutos)

### 4.1 Como funciona o Parser SLR(1)?

#### **Conceitos fundamentais:**

1. **Bottom-Up Parsing:**
   - Começa dos tokens (folhas) e constrói até o símbolo inicial (raiz)
   - Contrasta com Top-Down (LL, Recursive Descent)

2. **Ações do Parser:**
   - **SHIFT:** Empilha token e muda de estado
   - **REDUCE:** Aplica regra de produção (substitui símbolos)
   - **GOTO:** Transição após redução
   - **ACCEPT:** Reconhece entrada válida

#### **Exemplo de trace:**

```
Passo 1: Stack=[0], Estado=0, Lookahead=FUS
  SHIFT -> 28

Passo 2: Stack=[0, 28], Estado=28, Lookahead=id
  SHIFT -> 26

Passo 3: Stack=[0, 28, 26], Estado=26, Lookahead=:=
  SHIFT -> 27

Passo 4: Stack=[0, 28, 26, 27], Estado=27, Lookahead=num
  SHIFT -> 29
  
[... continua até ACCEPT ...]
```

### 4.2 Tabelas LR - Os "Cérebros" do Parser

#### **A) Closures (SLR.py) - 60 estados**

**Estado 0** (Inicial):
```python
{
  ("S'", (".", "S")),
  ("S", (".", "CMD", ";", "S")),
  ("S", (".", "CMD")),
  ("CMD", (".", "LOS", "EXPR", "CMD")),
  # ... mais itens
}
```

**Estados de redução** (ex: Estado 38):
```python
["EXPR' -> ε."]  # Redução para produção vazia
```

#### **B) Tabela GOTO (goto.py) - 200+ transições**

```python
transitions = {
  (0, 'FUS'): 28,      # Estado 0 + FUS → Estado 28
  (0, 'CMD'): 2,       # Estado 0 + CMD → Estado 2
  (27, 'num'): 29,     # Estado 27 + num → Estado 29
  # ...
}
```

#### **C) Conjuntos FIRST (first.py)**

*"FIRST(X) = primeiros símbolos que podem iniciar X"*

```python
FIRST = {
  'EXPR': {'+', '-', 'num', 'id', 'HIM', '('},
  'CMD': {'LOS', 'FOD', 'FAH', 'JUN', 'KEL', 'FUS', 'HON', 'print', 'assign'},
  'EXPR\'': {'ε'},  # Pode ser vazio
}
```

#### **D) Conjuntos FOLLOW (follow.py)**

*"FOLLOW(X) = símbolos que podem aparecer após X"*

```python
FOLLOW = {
  'EXPR': {';', '$', ')'},
  'CMD': {';', '$'},
  'EXPR\'': {';', '$', ')'},
}
```

### 4.3 Gramática BNF (regrasSintáticas.txt)

**25 regras de produção:**

```bnf
S' ::= S

# Sequência de comandos
S ::= CMD ; S
S ::= CMD

# Comandos individuais
CMD ::= LOS EXPR CMD               # Condicional
CMD ::= FOD EXPR FAH CMD           # While loop
CMD ::= FAH EXPR FAH CMD EXPR      # For loop
CMD ::= JUN EXPR                   # Return
CMD ::= KEL id CMD                 # Módulo
CMD ::= FUS LHS := EXPR            # Declaração
CMD ::= HON id                     # Input
CMD ::= print id                   # Output
CMD ::= assign LHS := EXPR         # Atribuição

# Atribuição (lado esquerdo)
LHS ::= id
LHS ::= HIM . id

# Expressões
EXPR ::= FACTOR + EXPR'
EXPR ::= FACTOR - EXPR'
EXPR ::= FACTOR EXPR'

EXPR' ::= + FACTOR EXPR'
EXPR' ::= - FACTOR EXPR'
EXPR' ::= ε                        # Produção vazia

# Fatores
FACTOR ::= num
FACTOR ::= id
FACTOR ::= ( EXPR )
FACTOR ::= HIM . id
FACTOR ::= NUST EXPR               # Operador NOT
```

### 4.4 Decisões de Projeto

#### **Por que SLR(1)?**
- ✅ Mais poderoso que LL(1)
- ✅ Trata recursão à esquerda e à direita
- ✅ Tabelas menores que LR(1) canônico
- ✅ Eficiente: O(n) onde n = número de tokens

#### **Tratamento de ε (Epsilon)**
- Usado em `EXPR'` para finalizar expressões
- Não consome tokens, apenas muda estado
- Crítico para precedência de operadores

#### **Integração PDA + SLR**
- PDA: reconhecimento de padrões (palavras-chave)
- SLR: validação estrutural (gramática)
- Separação clara de responsabilidades

---

## 🎓 5. CONCLUSÃO (2 minutos)

### 5.1 Resultados Alcançados

✅ **Compilador funcional em 3 fases:**
- Análise Léxica (PDA) com 36 estados
- Análise Sintática (SLR) com 60 estados, 200+ transições
- Análise Semântica com tabela de símbolos e escopos

✅ **Linguagem customizada:**
- Sintaxe criativa (temática RPG)
- 14 palavras-chave reconhecidas
- Suporte a módulos, loops, condicionais

✅ **Detecção robusta de erros:**
- Erros léxicos (caracteres inválidos)
- Erros sintáticos (violação de gramática)
- Erros semânticos (variáveis não declaradas)
- Warnings (variáveis não utilizadas)

### 5.2 Destaques Técnicos

🔹 **Arquitetura modular:**
- Componentes independentes e testáveis
- Fácil manutenção e extensão

🔹 **Documentação completa:**
- 6 arquivos Markdown detalhados
- Comentários extensivos no código
- Exemplos práticos em `EXEMPLOS_TESTE.md`

🔹 **Ferramentas auxiliares:**
- `debug_parenteses.py` → Debugger de expressões com parênteses
- `demo_completa.py` → Suite de 8 exemplos pré-configurados
- `compilador_completo.py` → Menu interativo

### 5.3 Possíveis Extensões

💡 **Funcionalidades futuras:**
1. **Geração de código intermediário** (Three-Address Code)
2. **Otimizações** (constant folding, dead code elimination)
3. **Tipos de dados** (int, float, string, bool)
4. **Funções** (declaração, chamada, parâmetros)
5. **Arrays e estruturas** de dados complexas

---

## 📊 SLIDES SUGERIDOS

### Slide 1: Título
```
ANALISADOR SINTÁTICO SLR(1)
Compilador para Linguagem Customizada

[Seus nomes]
[Disciplina/Curso]
```

### Slide 2: Objetivos
```
✓ Implementar compilador em 3 fases
✓ Linguagem com sintaxe criativa (Skyrim)
✓ Parser SLR(1) (bottom-up)
✓ Análise semântica com escopos
```

### Slide 3: Pipeline
[Diagrama de blocos do item 2.1]

### Slide 4: Exemplo de Código
```
FUS health := 100
KEL player FUS x := HIM . health + 50
```

### Slide 5: Tabelas LR
[Exemplo de Closure + GOTO]

### Slide 6: Demo ao Vivo
[Terminal com execução]

### Slide 7: Resultados
[Estatísticas: 60 estados, 25 produções, etc]

### Slide 8: Conclusão
[Destaques + Extensões futuras]

---

## 🎤 DICAS PARA APRESENTAÇÃO

### Gerenciamento de Tempo
- ⏰ Pratique com cronômetro
- 🎯 Priorize a demonstração prática
- ⚡ Tenha exemplos prontos (use `demo_completa.py`)

### Postura
- 🗣️ Fale pausadamente e com clareza
- 👀 Mantenha contato visual com a banca
- 🙌 Use gestos para enfatizar pontos importantes

### Respostas a Perguntas
- 🤔 Respire antes de responder
- 📝 Se não souber, seja honesto: *"Não implementamos isso ainda, mas seria possível com X"*
- 🔄 Redirecione para pontos fortes: *"Não temos tipos, mas nossa análise de escopo é robusta"*

### O que NÃO fazer
- ❌ Ler slides/código diretamente
- ❌ Usar jargão sem explicar
- ❌ Correr na explicação técnica
- ❌ Desculpar-se por limitações (seja confiante!)

---

## 📚 PERGUNTAS FREQUENTES (Prepare-se!)

### 1. "Por que SLR e não LR(1) ou LALR?"
*"SLR(1) oferece o melhor balanço entre poder de parsing e eficiência. Nossa gramática não tem conflitos shift-reduce que exigiriam lookahead mais sofisticado."*

### 2. "Como tratam precedência de operadores?"
*"Usamos fatoração de gramática. A produção EXPR' cuida da recursão à direita, garantindo associatividade correta. Parênteses têm prioridade na produção FACTOR."*

### 3. "Por que usar PDA ao invés de expressões regulares?"
*"O PDA reconhece a estrutura das palavras-chave de forma mais elegante. Além disso, foi requisito pedagógico para demonstrar autômatos de pilha."*

### 4. "O código gera assembly/bytecode?"
*"Não, paramos na análise semântica. O foco foi validação léxica/sintática/semântica. Geração de código seria uma extensão futura natural."*

### 5. "Suportam todos os recursos de uma linguagem real?"
*"Não. É uma linguagem demonstrativa. Não temos: arrays, funções com parâmetros, strings, tipos de dados. Mas a arquitetura permite essas extensões."*

### 6. "Quantas horas de desenvolvimento?"
*Seja honesto! Mencione desafios: debug de conflitos SHIFT/REDUCE, integração PDA+SLR, tratamento de epsilon.*

---

## 🚀 DEMONSTRAÇÃO AVANÇADA (Se sobrar tempo)

### Exemplo Completo com Escopo

```python
KEL player
  FUS health := 100
  FUS mana := 50
  
KEL inventory
  FUS gold := 1000
```

**Mostrar:**
- 2 escopos criados (player, inventory)
- Variáveis isoladas por escopo
- Tabela de símbolos hierárquica

### Debug Mode (Modo Verbose)

```python
compilador = CompiladorCompleto(verbose=True)
```

**Mostrar:**
- Trace completo do parser (SHIFT/REDUCE)
- Pilha de estados a cada passo
- Transições na tabela GOTO

---

## ✅ CHECKLIST PRÉ-APRESENTAÇÃO

- [ ] Código rodando sem erros
- [ ] Exemplos testados em `main.py`
- [ ] Terminal configurado (fonte legível)
- [ ] Slides preparados
- [ ] Cronômetro testado
- [ ] Perguntas frequentes ensaiadas
- [ ] Backup do código (pen drive/GitHub)
- [ ] Modo verbose desligado (ou explicar antes)
- [ ] Conhecer números: 60 estados, 25 produções, 200+ transições
- [ ] Ter exemplo de erro pronto

---

## 🎯 MENSAGEM FINAL

**Você construiu um compilador de verdade!** 

Isso envolve:
- Teoria formal (autômatos, gramáticas)
- Algoritmos sofisticados (SLR parsing)
- Estruturas de dados complexas (tabelas de símbolos)
- Engenharia de software (arquitetura modular)

**Apresente com orgulho. Você dominou conceitos que a maioria dos programadores nunca vê na prática!**

---

*Boa sorte na apresentação! 🍀*

---

**Contato para dúvidas:** [Adicione seu email/GitHub]

**Repositório:** https://github.com/Gustavo-Botezini/Compiladores
