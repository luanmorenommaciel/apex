# Metodologia — quando divergir, e quando não

Duas formas de atacar um problema foram usadas neste trabalho. A escolha entre
elas não é estilo: é uma leitura sobre **quanto se sabe da causa antes de
começar**.

---

## O critério

> Se a mensagem de erro (ou o próprio código) já contém a causa, o laço direto
> é o caminho certo. Se o sintoma é real mas a causa não está em lugar nenhum
> do que você já tem em mãos, aí o diamante se paga.

Aplicar as quatro fases a um `Target table ... doesn't exists` não descobre
nada que o erro não esteja dizendo — só produz cerimônia e a aparência de
rigor. E atacar em laço direto um sintoma cuja causa você não tem produz a
falha oposta: você "conserta" a primeira hipótese plausível e para de olhar.

---

## Duplo Diamante — quando a causa é incerta

Quatro fases, duas divergências:

```
Descobrir ──▶ Definir ──▶ Desenvolver ──▶ Entregar
 (alarga)    (fecha)      (alarga)        (fecha)
```

- **Descobrir** — levantar mecanicamente, sem escolher ainda. Ler o código dos
  dois lados, rodar o que já existe, bisseccionar.
- **Definir** — fechar num critério de aceitação **escrito antes de rodar o
  teste**, nunca derivado depois olhando o resultado.
- **Desenvolver** — mais de uma implementação ou mais de uma hipótese, testadas
  de verdade, não avaliadas no papel.
- **Entregar** — fechar em evidência documentada, com comando de reprodução.

### Exemplo real — #71

Sintoma: `mv_spark_events` parecia perder ~1 em 5 inserts. Não havia erro
nenhum: os inserts retornavam `exit 0` e chegavam na tabela de origem.

- **Descobrir** — bissecção da query inteira: cada coluna, cada função, cada
  cláusula do `WHERE`, isoladamente. Nenhuma peça sozinha quebra.
- **Definir** — se não é estrutural na query, é temporal. O critério vira:
  a linha some, ou só demora?
- **Desenvolver** — três hipóteses testadas separadamente
  (com `ts` / sem `ts` / merges desligados), 30 iterações cada, com releitura
  depois de uma janela maior.
- **Entregar** — a releitura com janela maior mostrou as linhas "perdidas"
  presentes. Era TTL do ambiente de teste, não perda de propagação.
  **Retratação**, não correção.

Nenhum laço direto teria chegado nisso: não havia erro para ler.

---

## Laço direto — quando a causa já está no erro

```
erro ──▶ causa ──▶ correção ──▶ reexecutar
```

Sem divergência, porque não há o que divergir. A disciplina aqui é outra:
reexecutar de verdade depois de cada correção, e não empilhar suposições.

### Exemplo real — #72

Mesmo sintoma superficial do #71 (insert não aparece no destino), mas com uma
diferença decisiva: **havia mensagem de erro**, e ela dizia a causa.

```
Target table ... doesn't exists
```

Ordem de bootstrap. A correção — checar a ordem antes de criar a MV — foi
direta, e testada duas vezes contra o stack real. Divergir aqui não teria
produzido nada além de tempo gasto.

### Exemplo real — #62, seis vezes seguidas

Os 6 defeitos encontrados rodando o pacote operacional pela primeira vez contra
o stack real foram todos assim: `"unhealthy"`, `Connection refused`,
`403 Forbidden`, `AUTHENTICATION_FAILED`, `A parameter cannot be found that
matches parameter name 'EnvFile'`. Em cada caso a mensagem continha a causa.
Oito tentativas de `bootstrap` até verde, seis correções, zero diamantes.

Ver [`LINEAGE.md`](LINEAGE.md#o-caso-62-em-detalhe--6-correções-em-laço-direto)
para a lista completa.

---

## Regras que valeram para os dois modos

Independente do caminho escolhido, estas não mudaram:

**Critério de aceitação antes do teste.** Escrito antes de rodar, nunca
derivado depois olhando o resultado. É o que impede o teste de virar
justificativa.

**Passar não é prova — falhar sem a mudança é.** O fallback do #61 só foi
considerado validado depois de **reverter** a correção e confirmar que o teste
novo falha sem ela. Passar com a mudança aplicada não bastava: um teste que
passa dos dois jeitos não está testando nada.

**Evidência é saída literal, não descrição.** Toda afirmação em
[`evidence/`](evidence/) tem a saída de terminal correspondente, sem edição.

**O que não foi exercitado é declarado.** No pacote operacional, `e2e`,
`pilot-clean` e `install` não foram rodados — e isso está escrito no PR e na
evidência, em vez de ficar implícito. Silêncio sobre um teste não rodado lê
como teste passado.

**Um achado tem que sobreviver a ser reexaminado.** O #71 foi publicado, depois
derrubado por uma forense melhor, e a retratação foi postada com a evidência
que derruba a leitura anterior. Reverter uma conclusão à luz de dado melhor faz
parte do método, não é falha dele.

**Refusar é um resultado.** O bench do `verify` confirmou o mecanismo (3/3) mas
se recusou a certificar a magnitude, porque o delta caiu dentro do piso de
ruído medido. `runtime_unresolved` é a resposta honesta, não um teste que
falhou.
