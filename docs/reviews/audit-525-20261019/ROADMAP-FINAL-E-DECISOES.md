> Corte histórico da consolidação. Consulte o adendo de 19/10 no diretório Pod3 para os objetos atualizados; contagens antigas abaixo são preservadas como origem.

# Roadmap integrado e decisões — proposta para o time

Corte documental histórico `c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874`, complementado pelos recibos posteriores citados em cada ficha. Não é consulta implícita do GitHub neste instante. Responsáveis, prioridades e capacidade são propostas a confirmar; nenhuma data de execução foi prometida.

## Cobertura completa

O [mapa dos 525 IDs](MAPA-ACOES-E-LINHAGEM-525.json) contém linhagem, dependência, plano, comunicação e próxima ação individual, incluindo histórico, substituições, trilhas externas e decisões. O resumo abaixo organiza esses planos; não substitui suas fichas. A [matriz por ID](MATRIZ-VALIDACAO-POR-ID.csv) preserva trabalho existente, falta de prova e controle proposto sem transferir CI entre árvores.

## Marcos e condições

| Marco proposto | Entrada e menor resultado revisável | Saída verificável / ganho | Dependências e paralelismo |
|---|---|---|---|
| M0 — Entregar conhecimento auditável | Inventário original, fontes e fichas recebidas | Cobertura por ID, divergências corrigidas, manifesto e limites explícitos; reduz retrabalho e perda de autoria | Documental, pode concluir sem executar produto |
| M1 — Decidir as fronteiras que afetam a próxima mudança | #122 Ask/HTTP, #171 perfis de exposição, #117 piso/atribuição, #115 consumidor; N07 ADR-004 e N09 governança | Decisão ou adiamento com motivo, responsável confirmado e critério; reduz contratos incompatíveis | Cada decisão bloqueia somente a mudança que dela depende. Estudos e documentação podem avançar |
| M2 — Revisar a fila técnica existente | Diffs e provas dos heads das #155/#157/#158/#159/#161/#162/#163/#164 no corte preservado | Reviews humanas e integração da árvore escolhida com prova correspondente; aproveita trabalho pronto | #157 fornece helpers à #163; demais independências descritas nas fichas. Coordenar #158/#159 com #182 e docs com #183, conforme recibos Pod3 |
| M3 — Provar a integração que ainda falta | Árvore definida, ambiente com ownership e critérios do caso | Recibos de nginx/navegador #172, pós-integração #156, cenários #123/#124 e Verify conforme escopo; reduz falsa certificação | CI disponível não substitui runtime; preservar dev/.env e recursos alheios #174/#175. Plano de execução depende do ambiente, sem bloquear preparação offline |
| M4 — Entrega compreensível aos pods | Fichas conferidas, próximos passos e destinatários definidos | Catálogo/avisos com links reais; decisões, responsáveis e prazos realmente combinados; reduz trabalho invisível | Pod3 já tem recibos #181/#183/#184. Demais publicação/avisos não realizados nesta rodada; reconferir objetos antes de qualquer envio |
| M5 — Evolução posterior por valor e capacidade | Estudos #42/#106–#109/#112/#114, N01/N05/N06; distribuição, onboarding e propostas externas | Adotar, experimentar, adiar ou rejeitar com razão e gatilho de reavaliação; evita inflar a v1 | Grafo depende de schema #106; PyPI depende de contrato de artefato/release, não automaticamente do Ask. Estudos externos não viram compromisso do APEX |

Uma v1 madura é uma meta a definir pelo time. A proposta é exigir clareza de contratos e evidência do perfil que será entregue, sem transformar todo estudo, integração externa, deploy alternativo ou ideia futura em gate universal. Um documento aceito não encerra teste de produto. Um item histórico não é tarefa nova só porque seu status antigo diz ready.

## Caminhos críticos distintos

- MCP: revisão #157 → escolha da integração da pilha → #163 e prova da árvore efetiva. Gate stdio N16 é recorte próprio; não basta substituir 7 por 8.
- Ask: decisão #122 → contrato/consumidor escolhido → implementação pequena e controles próprios → integração Serve/Front. A API existe, mas não certifica o fluxo Ask completo.
- Exposição compartilhada: decisão do perfil #171 → configuração correspondente → matriz rota × autenticação → nginx/navegador #172 no ambiente escolhido.
- Verify: decisões #117 → produtor/escrita/leitura e semântica escolhidos → controle discriminante de magnitude/atribuição → prova integrada. Paridade entre duas cópias de SQL não ratifica a política.
- Governança: reconciliar status, implementação e aceite → decidir regra N09 → housekeeping proporcional. Três YAML têm proposta de correção na #184; a publicação não prova merge nem aceite.

## Decisões e adiamentos

Cada ID de decisão possui alternativas, impacto, entrada e saída na ficha ligada pelo inventário, inclusive DEC-*, DEC-N*, propostas locais e decisões de produto. As demais fichas também conservam suas dependências humanas; não se presume que só os IDs com prefixo DEC exigem conversa.

Nas primeiras conversas: escolher fronteira do Ask; perfis e tokens; unidade/validade/igualdade do piso e atribuição; primeiro consumidor de execução; cinco precondições do ADR-004; regra para aceite de Task-Specs; required checks e tratamento de exceções. Antes de encaminhar, conferir se a decisão já foi registrada fora das fontes acessadas. Ausência de registro aqui não prova ausência de decisão em reunião.

## Comunicação e publicação

Para issue: problema → público afetado → comportamento existente → alternativa recomendada e exclusões → prova/limite → pergunta ao time → próximo resultado verificável.

Para PR: trigger concreto e antes/depois → escopo focado → issue/Task-Spec → base/head e dependência da pilha → validação daquele SHA → limite → pedido de review. Rotular separadamente bloqueio fundamentado, decisão necessária, prova pendente e sugestão.

Para o canal do pod: “Consolidei minha leitura de [tema] em [link]. Já existe [entrega]; resta [decisão/review/prova]. Afeta [fluxo]. Proponho [próximo passo], com responsável e prazo a combinar.” Nenhum aviso foi enviado nesta rodada.

## Limites de encerramento

Fechar a auditoria documental significa classificar e explicar todos os IDs no recorte declarado. Não significa implementar backlog, aprovar PRs, certificar produção, ratificar ADRs ou preservar todos os arquivos privados apenas em links GitHub. A cadeia local de fontes e a custódia continuam necessárias; antes de eliminar qualquer arquivo é preciso conferir um backup recuperável e a completude da preservação.
