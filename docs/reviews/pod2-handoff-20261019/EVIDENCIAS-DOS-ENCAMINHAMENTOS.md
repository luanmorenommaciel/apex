# Evidências dos três encaminhamentos

Corte preservado da Parte 10: fontes de 19/10/2026. Os links de código abaixo usam SHA; não são consulta a uma branch mutável. Ler um teste não equivale a executá-lo. Resultados de runtime citados como relato permanecem relatos.

## 1. Revisar a guarda de consistência do Engine

- **Direto, metadados:** [#155](https://github.com/luanmorenommaciel/apex/pull/155); [recibo](https://api.github.com/repos/luanmorenommaciel/apex/pulls/155). Head `561b27e7d1914dddf4989bf04834a33da726a45f`, autor `gustocezar`.
- **Direto, estado/texto público:** [#154](https://github.com/luanmorenommaciel/apex/issues/154); [recibo da coleção](https://api.github.com/repos/luanmorenommaciel/apex/issues?state=open&per_page=100).
- **Direto, CI do head:** [recibo de checks155](https://api.github.com/repos/luanmorenommaciel/apex/commits/561b27e7d1914dddf4989bf04834a33da726a45f/check-runs?per_page=100): 11 failure no corte. Sem novo diagnóstico de causa atual de billing; decidir a prova da árvore escolhida.

## 2. Confrontar a interface R9D com a contribuição do Pod 3

- **Direto, metadados:** [#167](https://github.com/luanmorenommaciel/apex/issues/167); [recibo](https://api.github.com/repos/luanmorenommaciel/apex/issues/167).
- **Direto, metadados:** [#185](https://github.com/luanmorenommaciel/apex/pull/185); [recibo](https://api.github.com/repos/luanmorenommaciel/apex/pulls/185). Head `a5c2ca45bda8e0898dc20460901fe2e83ab7ae8b`, autor `agmarcastro`.
- **Estático, main:** [argv do harness](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/dev/scripts/r9d_overhead_ab.py) e [assinatura do runner](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/dev/scripts/e2e_canonical.ps1). Comparar com o head a5c2ca45 da #185; não é benchmark reproduzido.

## 3. Desenhar um controle seguro do dispatcher PowerShell

- **Direto, metadados:** [#124](https://github.com/luanmorenommaciel/apex/issues/124); [recibo](https://api.github.com/repos/luanmorenommaciel/apex/issues/124).
- **Direto, metadados:** [#128](https://github.com/luanmorenommaciel/apex/pull/128); [recibo](https://api.github.com/repos/luanmorenommaciel/apex/pulls/128). Head `2b84c7a14fbcc5c009a3366536ccb80ebe316ca0`, autor `gustocezar`.
- **Estático, main:** [scripts/apex.ps1](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/scripts/apex.ps1) e [testes do pacote](https://github.com/luanmorenommaciel/apex/blob/c3c3ea3b7b8ac13751b6c9790a57ee39dbaec874/tests/test_apex_initial_package.py). DryRun retorna antes de Command; stubs/controle são proposta, não execução.

