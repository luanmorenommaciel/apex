# contracts/apex-event-source — a interface da fonte de eventos

## O problema que esta interface resolve

Hoje os eventos vêm de um **Listener dentro do cluster**. Mais pra frente, alguns ambientes
(serverless, DLT) não deixam rodar um Listener — lá os eventos virão de um **leitor do log de
eventos** que o Spark grava no storage. São dois jeitos diferentes de obter a mesma coisa.

Se os Watchers dependessem direto do Listener, trocar pra o leitor de log obrigaria a reescrever
todos os Watchers. Ruim. A solução é colocar uma **interface** no meio: os Watchers dependem da
interface, não de quem a implementa. Trocar a fonte vira trocar uma peça, sem tocar nos Watchers.

> Isto é o "construct que fica intacto mesmo quando a arquitetura muda" na prática.

## O contrato (em pseudocódigo Go)

```go
// ApexEventSource e a unica coisa que um Watcher precisa conhecer pra receber eventos.
// Nao importa SE os eventos vem do Listener ou do leitor de log — o Watcher nao sabe e nao liga.
type ApexEventSource interface {
    // Subscribe devolve um canal por onde os ApexEvent chegam, em streaming.
    // O ctx permite cancelar/encerrar a assinatura de forma limpa.
    Subscribe(ctx context.Context) (<-chan ApexEvent, error)
}

// Duas implementacoes que respeitam o MESMO contrato:
//   ListenerSource    -> recebe do Listener in-cluster (Day 1)
//   EventLogTailSource -> le o log de eventos do storage (Sprint 2)
// Trocar uma pela outra nao muda NENHUMA linha de Watcher.
```

## Por que isso te dá a "garantia de conexão"

Um Watcher escrito hoje contra `ApexEventSource` continua funcionando quando, daqui a um mês,
a fonte mudar. O pod do Watcher e o pod da fonte trabalham em paralelo, cada um do seu lado da
interface, e se encontram exatamente nesse aperto de mão.
