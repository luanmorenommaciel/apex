# PR #185 — sobreposição com o backlog e efeito na entrega

Consulta pública de 19/10/2026. Autor: Agmar (`agmarcastro`). Head `a5c2ca45bda8e0898dc20460901fe2e83ab7ae8b`, branch `feat/dev-lane-hardening`, base main. A main permanece `c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874`. A API retornou 38 arquivos, quatro checks verdes no head e zero reviews formais. A PR permanece aberta; mudanças propostas não são estado integrado.

## Por que importa

A branch propõe correções DEV, S3, runners e fingerprint. Parte do que antes aparecia apenas como backlog agora tem implementação candidata de outro colaborador. A próxima ação é reconciliar essa contribuição com as issues existentes, preservando autoria e prova, em vez de criar uma segunda implementação.

Esta é triagem de corpo/lista de arquivos e leitura focal dos patches `Makefile`, `common/paths.py`, `common/session.py`, `spark-defaults.conf`, runners .sh/.ps1, `ensure_env.py` e testes dos runners/R9D. Não é revisão integral dos 38 arquivos, verificação de disponibilidade das imagens MinIO, aceite de todas as Task-Specs citadas ou reprodução de Spark/Windows/benchmark.

## Mapa de alcance

| Origem já mapeada | O que a #185 demonstra no diff / relata | O que continua separado | Próximo passo mínimo |
|---|---|---|---|
| #167 / E16 — interface R9D ON/OFF | Runner ON passa a declarar EnvFile/AdditionalComposeFile; inclui-os ao construir Compose; testes estáticos fixam as declarações | Critérios de equivalência dos braços, preflight sem secrets e prova discriminante do comando completo exigem revisão; benchmark não foi reproduzido | Revisar esta contribuição como candidata à #167 antes de escolher/publicar variante local duplicada |
| #174 / E08 — preservar dev/.env do operador | ensure_env não reescreve destino existente, e a interface EnvFile dá alternativa à cópia | A issue cita Sync-DevEnvForCanonicalScript em scripts/apex.ps1. Esse arquivo NÃO é alterado pela #185; a mudança de ensure_env não encerra o caminho de Copy-Item -Force do pacote | Manter o critério #174 e comparar uma adaptação do pacote à nova interface do runner; não fechar por associação |
| N06 — credenciais S3A DEV | Remove literais do spark-defaults e passa submits pelo wrapper; body relata secrets e provider SDKv2 | Revisão do wrapper/Compose/perfis e alcance das provas; isso não define credencial ClickHouse #176 ou token API #171 | Reenquadrar N06 como conferência da implementação candidata e seus limites, não nova tarefa de remover os mesmos literais |
| #178 / L09 — endpoint OTLP escolhido | Makefile continua passando endpoint literal em c3/c4; runner define o default canônico | Retirar plumbing morto da variável não implementa precedência/forwarding do override pedido na #178 | Manter #178 e revisar qual interface efetiva deve ser propagada; não atribuir correção à #185 sem controle do comando |
| #169 — seleção de população/tentativa | Autor relata canonical_e2e_assert com successful_task_* e fallback | Não ratifica política entre todos os consumidores; relatórios de uma execução não resolvem consistência global | Incluir esse consumidor no mapa de decisão #169 e preservar escopo/SHA |
| #123 — gate tail-outlier | Runner continua aceitando tail_outlier e recebe melhorias operacionais | Relato live lista skew_join/spill/bad_shuffle/driver_oom; não é uma prova nova do tail-outlier nem da associação stage/snapshot exigida no critério escolhido | Reusar o que ajuda o runner e manter a garantia específica de #123 separada |
| #113 — overhead | OFF/ON e scripts mudam; drain passa a depender do plugin | Melhorar o launcher não ratifica protocolo/limiares nem comprova overhead. Mudança de waits deve constar do desenho de medição | Conferir comparabilidade dos braços antes da próxima medição, sem iniciar benchmark |
| #175 — identidade/ownership | Preflights consultam containers/redes por nomes conhecidos | Nomes e disponibilidade não demonstram ownership entre checkouts ou contexts | Manter a decisão de identidade e o controle de recusa de recurso alheio |

## Limites da alegação de paridade dos runners

A exposição dos knobs é mais próxima, mas o teste novo `test_powershell_runner_exposes_the_bash_knobs` afirma presença de textos. Isso não é equivalência completa do comportamento Bash/PowerShell. No código lido, Bash inicia a stack por default salvo REUSE_DEV, enquanto PowerShell depende de StartDev para iniciar; pode ser convenção intencional dos chamadores. Antes de chamar isso de defeito, escolher contrato/default e conferir como o orquestrador os invoca. Não foi executado binding PowerShell.

Os testes de R9D adicionados exercitam funções e parse de relatórios; não são benchmark real. O corpo declara 106 testes locais e runtime Spark4.1.2, ambos preservados como relatos; quatro checks do head são observação separada. Não converter aceites locais declarados de Task-Spec em aprovação humana da PR.

## Recomendação

1. Acrescentar a #185 ao material de coordenação, mantendo a autoria do Agmar.
2. Revisar primeiro a interface que se sobrepõe à #167 e a mudança de credencial S3A; só depois escolher qualquer implementação paralela dos mesmos itens.
3. Manter #174/#175/#178/#113 com critérios próprios. Não criar um bloqueio global para a #185 nem fechar essas issues automaticamente.

A triagem original foi somente leitura; a publicação documental e os encaminhamentos posteriores têm recibos próprios. Fontes: [PR #185](https://github.com/luanmorenommaciel/apex/pull/185), [diff](https://github.com/luanmorenommaciel/apex/pull/185/files), [#167](https://github.com/luanmorenommaciel/apex/issues/167), [#174](https://github.com/luanmorenommaciel/apex/issues/174), [#178](https://github.com/luanmorenommaciel/apex/issues/178); recibos exatos em `fontes/` desta Parte08.
