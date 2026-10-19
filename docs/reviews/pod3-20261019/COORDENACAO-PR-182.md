# Coordenação com a nova PR #182

Consulta pública de 19/10/2026. [PR #182](https://github.com/luanmorenommaciel/apex/pull/182), autor `agmarcastro`, head `74fdb0791825aa89c419694ec71f2aa3e6ea4d74`, base `main`. A main consultada continua `c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874`. O inventário da API retornou 65 arquivos alterados nessa PR.

## Relevância para a discussão

O autor propõe Console somente via API, remove o acesso ClickHouse do browser, mantém `http` e `fixtures` como perfis e move consultas/contrato para o Serve. O texto da PR registra decisões da branch, mudanças de nginx, gate de paridade e provas executadas pelo autor. Essas decisões e provas são **relatadas na PR**; não foram ratificadas ou reproduzidas nesta complementação. A proposta não substitui silenciosamente o estado integrado nem resolve automaticamente Ask #122, política #171 ou todos os critérios #172.

## Sobreposição de arquivos confirmada pela API

| PR do recorte | Caminhos também alterados na #182 |
|---|---|
| #157 | Nenhum caminho comum na lista consultada |
| #158 | `serve/tests/test_console_reads.py` |
| #159 | `serve/RUNBOOK.md`; `serve/tests/test_console_parity_gate.py`; `serve/tools/console_parity_gate.py` |
| #163 | Nenhum caminho comum na lista consultada |
| #164 | Nenhum caminho comum na lista consultada |

Sobreposição de caminho não prova conflito textual ou incompatibilidade semântica. Ausência de caminho comum também não prova independência funcional.

## Encaminhamento proposto

1. Front e Serve combinarem ordem/base de integração de #182, #158 e #159. Conferir diferenças de contrato e destino das consultas antes de transportar patches.
2. Preservar as regressões úteis de ordenação e paridade; se a porta SQL da Console for removida, adaptar o controle para o contrato escolhido com justificativa, sem apagar cobertura apenas para facilitar merge.
3. Mapear as provas relatadas de #182 aos critérios #172 e #156: imagem/curl, fixtures, HTTP com store real e renderização de navegador são alcances distintos. Não repetir prova suficiente nem aceitar lacuna por associação.
4. Registrar efeitos nas decisões #171 e #122. “Console somente API” e “nova fachada Ask” são decisões diferentes; a política do token ainda precisa ser explícita no perfil escolhido.
5. Atualizar matriz e guias depois de integrar a árvore escolhida. Até lá os documentos descrevem a main atual e rotulam a proposta #182 separadamente.

Responsáveis, revisores e prazo: **a confirmar**. Este registro é triagem documental de corpo e lista de arquivos, não code review completa dos 65 arquivos, aprovação, consulta de checks/reviews por head ou validação de runtime.
