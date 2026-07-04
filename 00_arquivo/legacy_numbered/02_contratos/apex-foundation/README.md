# Apex — estrutura do repositório

> Apex: peak performance para Apache Spark & Databricks.
> Pega o que o code review deixa passar; corrige o que a produção revela.

## Como este repositório está organizado (e por quê)

A regra de ouro: **um componente = uma pasta = um dono.** Como cada pod trabalha numa
pasta diferente, dois pods conseguem mandar mudanças ao mesmo tempo sem pisar um no outro.
A fronteira entre as pastas é sempre um **contrato** (veja `contracts/`), nunca uma chamada
direta de uma pasta na outra. Foi isso que o Commander quis dizer com
"componentização por contrato, sem dependências diretas".

```
apex/
├── contracts/          # A COSTURA. Formatos e interfaces que todos respeitam.
│                       #   -> mergeia PRIMEIRO. Ninguém constrói antes disto existir.
│
├── platform/           # Ambiente local compartilhado (o "lab platform" do Gabriel:
│                       #   Spark + MinIO + ClickHouse). Todo pod roda os testes aqui.
│
├── collector/          # Move a telemetria do Spark até o banco. Escrito em Go.
│
├── watchers/
│   ├── shuffle/        # Detector de shuffle/skew  (Pod A1)
│   └── memory/         # Detector de memória/custo  (Pod A2)
│
├── classifier/         # Lê o código e classifica o anti-pattern (Pod A3)
├── coordinator/        # Junta os achados dos watchers (Pod A4)
├── judge/              # Revisor adversarial, dispara quando a confiança é baixa (Pod A4)
├── recommendation/     # Transforma achado em recomendação acionável
│
├── scenarios/          # Os "golden fixtures": cada cenário declara um anti-pattern,
│                       #   gera o código com o bug E o log do Spark correspondente.
│                       #   É contra eles que os watchers são testados.
│
├── CLAUDE.md           # Contexto pros agentes (Claude Code) entenderem o projeto.
├── CONTRIBUTING.md     # Como contribuir: branch, PR, e os gates de merge.
├── CODEOWNERS          # Mapeia cada pasta ao dono — o GitHub pede review certo sozinho.
└── .github/workflows/  # CI: roda os gates a cada push (os cenários têm que passar).
```

## A ordem importa

Construir na ordem errada é a causa nº1 de retrabalho. A ordem certa:

1. **contracts/** mergeia primeiro — a costura existe e está estável.
2. **platform/** integrado — todo mundo roda contra o mesmo Spark/dados.
3. Os **pods constroem em paralelo** contra o contrato, cada um na sua pasta.
