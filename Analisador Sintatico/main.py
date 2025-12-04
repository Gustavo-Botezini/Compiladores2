"""
Sistema Completo de Análise: PDA (Léxico) -> SLR(1) (Sintático + Semântico)
Integra o autômato de pilha de Compiladores/ como analisador léxico

=============================================================================
COMO USAR:
=============================================================================

1. Edite a variável 'code' na função main() com o código que deseja testar
2. Execute: python main.py

EXEMPLOS DE CÓDIGO VÁLIDO:
---------------------------
- Declaração simples:     'FUS x := 10'
- Operações aritméticas:  'FUS soma := 10 + 20 - 5'
- Com parênteses:         'FUS result := ( 10 + 20 )'
- Acesso a membro:        'FUS prop := HIM . atributo'
- Expressão complexa:     'FUS calc := ( 10 + 20 ) - HIM . valor'

MODO VERBOSE:
-------------
- verbose=False  → Saída limpa (apenas resultado final e erros)
- verbose=True   → Saída detalhada (trace completo do parser)

=============================================================================
"""

from SLR import closures
from goto import transitions
from terminais import terminals
from nao_terminais import nonterminals
from follow import FOLLOW
from parser_integrated import SLRParserWithSemantics, Token
from Compiladores.pda import AP
from Compiladores.constants import EPSILON
from Compiladores.delta import DeltaFinal


class PDALexerAdapter:
    """
    Adapta a saída do PDA para gerar tokens compatíveis com o parser SLR
    Mapeia estados finais do PDA para tipos de tokens
    """
    
    # Mapeamento: Estado final do PDA -> Tipo de token
    STATE_TO_TOKEN = {
        'E11,Z': 'KEL',      # Palavra-chave KEL (módulo)
        'D10,Z': 'LOS',      # Palavra-chave LOS (if)
        'E12,Z': 'FOD',      # Palavra-chave FOD (while início)
        'D3,Z': 'FAH',       # Palavra-chave FAH (separador)
        'D5,Z': 'FUS',       # Palavra-chave FUS (declaração)
        'D9,Z': 'HON',       # Palavra-chave HON (input)
        'D4,Z': 'JUN',       # Palavra-chave JUN (return)
        'D6,Z': 'HIM',       # Palavra-chave HIM (this/self)
        'D7,Z': 'NUST',      # Palavra-chave NUST (not)
        'D8,Z': 'ANRK',      # Palavra-chave ANRK (and)
        'D2,Z': 'AAN',       # Palavra-chave AAN (or)
        'B1,Z': 'KO',        # Palavra-chave KO (in)
    }
    
    # Mapeamento reverso: entrada original -> palavra-chave reconhecida
    ORIGINAL_TO_KEYWORD = {
        'KO': 'KO',
        'KEL': 'KEL',
        'LOS': 'LOS',
        'FAH': 'FAH',
        'HIM': 'HIM',
        'JUN': 'JUN',
        'FOD': 'FOD',
        'FUS': 'FUS',
        'HON': 'HON',
        'NUST': 'NUST',
        'AAN': 'AAN',
        'ANRK': 'ANRK',
    }
    
    def __init__(self):
        # Configuração do PDA (copiada de Compiladores/main.py)
        Q = ['A1,B2,Z', 'Z', 'B7,B8,Z', 'B3,B6,Z',
             'B12,Z', 'B4,Z', 'B5,B9,Z', 'B10,B11,Z',
             'B1,Z', 'C2,Z', 'C8,Z', 'C7,Z',
             'B3,Z', 'C6,Z', 'C12,Z', 'C4,Z',
             'C9,Z', 'C5,Z', 'B11,Z', 'B10,Z',
             'D2,Z', 'D8,Z', 'D7,Z', 'C3,Z',
             'D6,Z', 'D12,Z', 'D4,Z', 'D9,Z',
             'D5,Z', 'C11,Z', 'C10,Z', 'D3,Z',
             'E12,Z', 'D11,Z', 'D10,Z', 'E11,Z']
        
        Sigma = ['#', 'K', 'O', 'E', 'L', 'H', 'N', 'J', 
                 'U', 'F', 'S', 'I', 'M', 'D', 'R', 'T', 'A', EPSILON]
        
        gama = ['$', 'K', 'O', 'E', 'L', 'H', 'N', 'J', 
                'U', 'F', 'S', 'I', 'M', 'D', 'R', 'T', 'A', EPSILON]
        
        F = ['E11,Z', 'D10,Z', 'E12,Z', 'D3,Z', 'D5,Z', 'D9,Z', 
             'D10,Z', 'D4,Z', 'D6,Z', 'D7,Z', 'D8,Z', 'D2,Z', 'B1,Z']
        
        self.pda = AP(Sigma, gama, DeltaFinal, 'S', F)
    
    def tokenize(self, source_code):
        """
        Executa PDA e converte saída para tokens
        
        Args:
            source_code: String com código fonte (formato: "KO KEL # LOS")
        
        Returns:
            Lista de objetos Token
        """
        tokens = []
        linha_atual = 1
        
        print("==================================================================")
        print("=          SAÍDA DO PDA (Compiladores/main.py)                  =")
        print("==================================================================")
        
        # Executar PDA original e capturar saída
        print("\n Processando entrada no PDA...")
        print(f"Entrada: {source_code}\n")
        
        # Separar por linhas (delimitadas por '#')
        linhas = source_code.split('#')
        
        pda_results = []  # Armazena resultados do PDA
        
        for linha_texto in linhas:
            linha_texto = linha_texto.strip()
            if not linha_texto:
                linha_atual += 1
                continue
            
            # Processar cada palavra da linha
            palavras = linha_texto.split()
            
            for palavra in palavras:
                palavra = palavra.strip()
                if not palavra:
                    continue
                
                # Primeiro: tentar classificar diretamente (números, operadores, etc)
                token = self._tentar_classificacao_direta(palavra, linha_atual)
                
                if token:
                    # Token reconhecido diretamente (não precisa do PDA)
                    tokens.append(token)
                    print(f"  Linha {linha_atual}: '{palavra}' -> Reconhecido diretamente -> {token.type}")
                else:
                    # Não reconhecido diretamente, tentar PDA (palavras-chave)
                    estado_final = self._reconhecer_palavra(palavra)
                    
                    # Armazenar resultado do PDA
                    pda_result = {
                        'palavra': palavra,
                        'linha': linha_atual,
                        'estado': estado_final,
                        'aceito': estado_final in self.STATE_TO_TOKEN
                    }
                    pda_results.append(pda_result)
                    
                    # Mapear estado final para tipo de token
                    if estado_final in self.STATE_TO_TOKEN:
                        token_type = self.STATE_TO_TOKEN[estado_final]
                        token = Token(token_type, palavra, linha_atual, column=0, value=palavra)
                        tokens.append(token)
                        
                        # Mostrar saída do PDA (similar ao original)
                        print(f"[OK] Linha {linha_atual}: '{palavra}' -> Estado {estado_final} -> {token_type} (ACEITO)")
                    
                    elif estado_final == 'X':
                        # Palavra rejeitada pelo PDA - classificar como ID
                        token = Token("id", palavra, linha_atual, value=palavra)
                        tokens.append(token)
                        print(f"  Linha {linha_atual}: '{palavra}' -> Não reconhecido pelo PDA -> {token.type}")
                    
                    else:
                        # Estado não mapeado - tratar como ID
                        print(f"[!] Linha {linha_atual}: '{palavra}' -> Estado '{estado_final}' não mapeado")
                        token = Token("id", palavra, linha_atual, value=palavra)
                        tokens.append(token)
            
            linha_atual += 1
        
        # Adicionar EOF
        tokens.append(Token("$", "$", linha_atual, column=0, value="$"))
        
        # Mostrar tabela de símbolos do PDA (apenas palavras processadas pelo PDA)
        if pda_results:
            print("\n" + "="*70)
            print(" TABELA DE SÍMBOLOS DO PDA:")
            print("="*70)
            print(f"{'Linha':<8} {'Palavra':<15} {'Estado Final':<15} {'Status':<10}")
            print("="*70)
            
            for result in pda_results:
                status = "[OK] ACEITO" if result['aceito'] else "[X] REJEITADO"
                print(f"{result['linha']:<8} {result['palavra']:<15} {result['estado']:<15} {status:<10}")
            
            print("="*70)
            print(f"\n[OK] PDA processou {len(pda_results)} palavras")
        else:
            print("\n[!] Nenhuma palavra foi processada pelo PDA (todas reconhecidas diretamente)")
        
        print(f"[OK] Gerados {len(tokens)} tokens (incluindo EOF)\n")
        
        return tokens
    
    def _reconhecer_palavra(self, palavra):
        """
        Reconhece palavra pelo PDA e retorna estado final
        Simula a lógica de run() do AP sem impressões
        """
        estado = 'S'  # Estado inicial
        
        for char in palavra:
            if char not in self.pda._Sigma:
                return 'X'  # Caractere inválido
            
            # Busca transição
            transicao = self.pda._delta.get((estado, char, EPSILON))
            if transicao:
                estado = transicao[0]
            else:
                return 'X'  # Sem transição
        
        # Verifica se é estado final
        if estado not in self.pda._F:
            return 'X'
        
        return estado
    
    def _tentar_classificacao_direta(self, palavra, linha):
        """
        Tenta classificar tokens que não precisam do PDA:
        números, operadores, pontuação, palavras-chave extras
        
        Returns:
            Token se reconhecido, None caso contrário
        """
        # Números
        if palavra.isdigit():
            return Token("num", palavra, linha, value=int(palavra))
        
        # Operadores e pontuação
        operadores = {
            ':=', ';', '.', '(', ')', '+', '-'
        }
        
        if palavra in operadores:
            return Token(palavra, palavra, linha, value=palavra)
        
        # Palavras-chave extras não cobertas pelo PDA
        keywords_extras = {
            'assign': 'assign',
            'print': 'print',
        }
        
        if palavra in keywords_extras:
            return Token(keywords_extras[palavra], palavra, linha, value=palavra)
        
        # Não reconhecido diretamente, precisa tentar o PDA
        return None
    
    def _classificar_palavra_desconhecida(self, palavra, linha):
        """
        Classifica palavras não reconhecidas pelo PDA
        Pode ser ID, NUM, operadores, etc.
        """
        # Números
        if palavra.isdigit():
            return Token("num", palavra, linha, value=int(palavra))
        
        # Operadores e pontuação
        operadores = {
            ':=': ':=',
            ';': ';',
            '.': '.',
            '(': '(',
            ')': ')',
            '+': '+',
            '-': '-',
        }
        
        if palavra in operadores:
            return Token(palavra, palavra, linha, value=palavra)
        
        # Palavras-chave não cobertas pelo PDA
        keywords_extras = {
            'assign': 'assign',
            'print': 'print',
        }
        
        if palavra in keywords_extras:
            return Token(keywords_extras[palavra], palavra, linha, value=palavra)
        
        # Padrão: identificador
        return Token("id", palavra, linha, value=palavra)


class CompiladorCompleto:
    """Pipeline completo: PDA Léxico -> SLR Sintático -> Análise Semântica"""
    
    def __init__(self, verbose=True):
        self.lexer = PDALexerAdapter()
        self.parser = SLRParserWithSemantics(verbose=verbose)
        self.verbose = verbose
    
    def compile(self, source_code):
        """
        Executa compilação completa
        
        Args:
            source_code: String com código fonte
        
        Returns:
            bool: True se compilação bem-sucedida
        """
        print("\n" + "="*80)
        print("FASE 1: ANÁLISE LÉXICA (PDA)")
        print("="*80)
        print(f"Código fonte: {source_code}\n")
        
        # Fase 1: Análise Léxica com PDA
        try:
            tokens = self.lexer.tokenize(source_code)
            
            if self.verbose:
                print("\n==================================================================")
                print("=              TOKENS GERADOS PARA O PARSER                      =")
                print("==================================================================")
                for i, token in enumerate(tokens, 1):
                    print(f"{i:3}. {token}")
                print("-" * 80)
        
        except Exception as e:
            print(f"\n[X] ERRO LÉXICO: {e}")
            return False
        
        # Fase 2 & 3: Análise Sintática + Semântica
        print("\n" + "="*80)
        print("FASE 2 & 3: ANÁLISE SINTÁTICA E SEMÂNTICA (SLR)")
        print("="*80 + "\n")
        
        sucesso = self.parser.parse(tokens)
        
        # Relatório final
        self.parser.print_report()
        
        return sucesso
    
    def reset(self):
        """Reinicia compilador"""
        self.parser.reset()


# ============================================================================
# CLASSE ANTIGA (MANTIDA PARA COMPATIBILIDADE)
# ============================================================================

class SLRParser:
    def __init__(self):
        self.stack = [0]
        self.symbols = []
        self.closures = closures
        self.transitions = transitions
        self.terminals = terminals
        self.nonterminals = nonterminals
        self.follow = FOLLOW
        self.productions = self._extract_productions()
    
    def _extract_productions(self):
        prods = {}
        for state, closure in self.closures.items():
            if isinstance(closure, set):
                for item in closure:
                    if len(item) == 2:
                        lhs, rhs = item
                        if len(rhs) > 0 and rhs[-1] == ".":
                            symbols = [s for s in rhs[:-1] if s != "."]
                            if not symbols:
                                symbols = ["ε"]
                            prods[state] = (lhs, symbols)
            elif isinstance(closure, list):
                for item in closure:
                    if "->" in item and item.endswith("."):
                        parts = item.split("->")
                        lhs = parts[0].strip()
                        rhs = parts[1].strip().rstrip(".")
                        if rhs == "ε":
                            symbols = ["ε"]
                        else:
                            symbols = rhs.split()
                        prods[state] = (lhs, symbols)
                        break
        return prods
    
    def parse(self, tokens):
        print("=== Análise Sintática SLR(1) ===\n")
        token_index = 0
        current_token = tokens[token_index] if token_index < len(tokens) else ("$", "$")
        step = 1
        
        while True:
            state = self.stack[-1]
            lookahead = current_token[0]
            
            print(f"Passo {step}: Stack={self.stack}, Estado={state}, Lookahead={lookahead}")
            
            if state == 1 and lookahead == "$":
                print("\n[OK] ACEITO!\n")
                return True
            
            if (state, lookahead) in self.transitions:
                next_state = self.transitions[(state, lookahead)]
                print(f"  SHIFT -> {next_state}\n")
                self.stack.append(next_state)
                self.symbols.append(lookahead)
                token_index += 1
                current_token = tokens[token_index] if token_index < len(tokens) else ("$", "$")
                step += 1
                continue
            
            if (state, "ε") in self.transitions:
                next_state = self.transitions[(state, "ε")]
                print(f"  REDUCE EXPR' -> ε via estado {next_state}")
                # Estado 38 é EXPR' -> ε., então devemos fazer GOTO de volta
                # Não empilhamos ε, fazemos o GOTO diretamente
                if next_state == 38:
                    # Pop do estado ε e faz GOTO com EXPR'
                    if (state, "EXPR'") in self.transitions:
                        expr_state = self.transitions[(state, "EXPR'")]
                        print(f"  GOTO({state}, EXPR') = {expr_state}\n")
                        self.stack.append(expr_state)
                        self.symbols.append("EXPR'")
                        step += 1
                        continue
                else:
                    self.stack.append(next_state)
                    self.symbols.append("ε")
                    step += 1
                    continue
            
            found_goto = False
            for nt in self.nonterminals:
                if (state, nt) in self.transitions and nt == "EXPR'" and lookahead in self.follow.get("EXPR'", set()):
                    print(f"  REDUCE EXPR' -> ε")
                    next_state = self.transitions[(state, nt)]
                    print(f"  GOTO({state}, {nt}) = {next_state}\n")
                    self.stack.append(next_state)
                    self.symbols.append(nt)
                    step += 1
                    found_goto = True
                    break
            
            if found_goto:
                continue
            
            if state in self.productions:
                lhs, rhs = self.productions[state]
                if lookahead in self.follow.get(lhs, set()) or lookahead == "$":
                    print(f"  REDUCE {lhs} -> {' '.join(rhs)}")
                    if rhs != ["ε"]:
                        for _ in range(len(rhs)):
                            if self.stack:
                                self.stack.pop()
                            if self.symbols:
                                self.symbols.pop()
                    state_after = self.stack[-1] if self.stack else 0
                    if (state_after, lhs) in self.transitions:
                        goto_state = self.transitions[(state_after, lhs)]
                        print(f"  GOTO({state_after}, {lhs}) = {goto_state}\n")
                        self.stack.append(goto_state)
                        self.symbols.append(lhs)
                        step += 1
                        continue
                    else:
                        print(f"\n[X] ERRO: GOTO({state_after}, {lhs}) não encontrado!\n")
                        return False
            
            print(f"\n[X] ERRO SINTÁTICO! Estado={state}, Lookahead={lookahead}\n")
            return False
    
    def reset(self):
        self.stack = [0]
        self.symbols = []




def main():
    """
    Modo de teste simplificado - apenas compila e mostra resultado
    """
    # ========== CONFIGURAÇÃO ==========
    # Altere o código aqui para testar diferentes expressões:
    
    # === OPERAÇÕES ARITMÉTICAS ===
    # code = 'FUS soma := 10 + 20'              # Exemplo padrão: adição
    # code = 'FUS x := 10'                    # Declaração simples
    # code = 'FUS diff := 100 - 30'           # Subtração
    code = 'FUS calc := 10 + 20 - 5'        # Múltiplas operações
    # code = 'FUS result := ( 10 + 20 )'      # Com parênteses
    # code = 'FUS nested := ( ( 10 ) )'       # Parênteses aninhados
    # code = 'FUS complex := ( 10 + 20 ) - 5' # Expressão complexa
    
    # === ACESSO A MEMBROS (HIM) ===
    # code = 'FUS prop := HIM . atributo'     # Acesso simples
    # code = 'FUS calc := HIM . valor + 10'   # Operação com membro
    # code = 'FUS mix := ( HIM . x ) + 20'    # Membro com parênteses
    
    # === OUTRAS ESTRUTURAS ===
    # code = 'HON x'                          # Input
    # code = 'print y'                        # Output
    # code = 'JUN 42'                         # Return
    # code = 'assign health := 100'           # Atribuição
    

    modo_verbose = True
    # ==================================
    
    compilador = CompiladorCompleto(verbose=modo_verbose)
    sucesso = compilador.compile(code)
    
    print("\n" + "=" * 70)
    if sucesso:
        print("RESULTADO FINAL: [OK] COMPILACAO BEM-SUCEDIDA")
    else:
        print("RESULTADO FINAL: [X] COMPILACAO FALHOU")
    print("=" * 70)


if __name__ == "__main__":
    main()
