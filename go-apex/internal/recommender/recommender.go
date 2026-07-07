package recommender

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/apex/go-apex/internal/models"
	"github.com/apex/go-apex/internal/runbook"
)

// Recommender gera recomendações de correção para anomalias Spark.
type Recommender struct {
	RunbookManager *runbook.Manager
	OpenAIAPIKey   string
	Model          string
	CREIURL        string
}

// NewRecommender cria um novo Recommender.
func NewRecommender(runbooksDir string) *Recommender {
	return &Recommender{
		RunbookManager: runbook.NewManager(runbooksDir),
		OpenAIAPIKey:   os.Getenv("OPENAI_API_KEY"),
		Model:          "gpt-4o-mini",
		CREIURL:        os.Getenv("CREI_URL"),
	}
}

// NewRecommenderWithCREI cria um Recommender com URL do CREI.
func NewRecommenderWithCREI(runbooksDir, creiURL string) *Recommender {
	if creiURL == "" {
		creiURL = os.Getenv("CREI_URL")
	}
	if creiURL == "" {
		creiURL = "http://localhost:8000"
	}
	return &Recommender{
		RunbookManager: runbook.NewManager(runbooksDir),
		OpenAIAPIKey:   os.Getenv("OPENAI_API_KEY"),
		Model:          "gpt-4o-mini",
		CREIURL:        creiURL,
	}
}

// Recommend gera uma Recommendation para um AnomalyReport.
func (r *Recommender) Recommend(report models.AnomalyReport) models.Recommendation {
	rb, err := r.RunbookManager.Load(report.AnomalyType)
	if err == nil && rb != nil {
		return r.fromRunbook(report, rb)
	}
	// Se não houver runbook, tenta fallback por LLM
	return r.fromLLM(report)
}

// RecommendAll gera recomendações para todos os AnomalyReports.
func (r *Recommender) RecommendAll(reports []models.AnomalyReport) []models.Recommendation {
	var out []models.Recommendation
	for _, rep := range reports {
		out = append(out, r.Recommend(rep))
	}
	return out
}

// fromRunbook constrói recomendação a partir de runbook estruturado.
func (r *Recommender) fromRunbook(report models.AnomalyReport, rb *runbook.Runbook) models.Recommendation {
	steps := make([]models.StepAction, len(rb.Steps))
	for i, s := range rb.Steps {
		steps[i] = models.StepAction{
			Action:  s.Action,
			Details: s.Details,
		}
	}

	codeFix := rb.CodeTemplate
	if report.Evidence != nil {
		if stageID, ok := report.Evidence["stage_id"]; ok {
			codeFix = strings.ReplaceAll(codeFix, "{{stage_id}}", fmt.Sprintf("%v", stageID))
		}
	}

	confidence := report.Confidence * 0.95
	if confidence < 0 {
		confidence = 0.5
	}

	expectedImpact := rb.Summary
	if rb.ExpectedImpact != nil {
		expectedImpact = rb.ExpectedImpact.Summary
	}

	return models.Recommendation{
		AnomalyType:    report.AnomalyType,
		Confidence:     confidence,
		Summary:        rb.Summary,
		Steps:          steps,
		CodeFix:        codeFix,
		ExpectedImpact: expectedImpact,
		RunbookID:      rb.ID,
	}
}

// fromLLM gera recomendação via LLM quando não há runbook.
func (r *Recommender) fromLLM(report models.AnomalyReport) models.Recommendation {
	if r.OpenAIAPIKey == "" {
		return models.Recommendation{
			AnomalyType:    report.AnomalyType,
			Confidence:     0.3,
			Summary:        "Nenhum runbook T1 disponível e LLM não configurado. Revisão manual necessária.",
			Steps:          []models.StepAction{{Action: "Revisar métricas manualmente", Details: report.Description}},
			ExpectedImpact: "Indeterminado.",
		}
	}

	payload := map[string]interface{}{
		"model":       r.Model,
		"temperature": 0.2,
		"messages": []map[string]string{
			{
				"role":    "system",
				"content": "Você é um especialista em otimização de Apache Spark. Responda APENAS com JSON válido.",
			},
			{
				"role": "user",
				"content": fmt.Sprintf(
					"Anomalia detectada:\n- Tipo: %s\n- Severidade: %s\n- Descrição: %s\n- Evidência: %s\n\nGere uma recomendação de correção em formato JSON com:\n- summary: string explicando o problema e a solução\n- steps: lista de objetos com 'action' e 'details'\n- code_fix: snippet PySpark se aplicável\n- expected_impact: string descrevendo ganho esperado",
					report.AnomalyType, report.Severity, report.Description, toJSON(report.Evidence),
				),
			},
		},
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return fallbackError(report, err)
	}

	req, err := http.NewRequest("POST", "https://api.openai.com/v1/chat/completions", bytes.NewReader(body))
	if err != nil {
		return fallbackError(report, err)
	}
	req.Header.Set("Authorization", "Bearer "+r.OpenAIAPIKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return fallbackError(report, err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return fallbackError(report, err)
	}

	var data map[string]interface{}
	if err := json.Unmarshal(respBody, &data); err != nil {
		return fallbackError(report, err)
	}

	choices, ok := data["choices"].([]interface{})
	if !ok || len(choices) == 0 {
		return fallbackError(report, fmt.Errorf("resposta LLM sem choices"))
	}

	choice, ok := choices[0].(map[string]interface{})
	if !ok {
		return fallbackError(report, fmt.Errorf("formato de choice inválido"))
	}

	message, ok := choice["message"].(map[string]interface{})
	if !ok {
		return fallbackError(report, fmt.Errorf("formato de message inválido"))
	}

	content, _ := message["content"].(string)
	if content == "" {
		return fallbackError(report, fmt.Errorf("content vazio"))
	}

	// Tenta extrair JSON da resposta
	llmData, err := extractJSON(content)
	if err != nil {
		return fallbackError(report, err)
	}

	var steps []models.StepAction
	if rawSteps, ok := llmData["steps"].([]interface{}); ok {
		for _, rs := range rawSteps {
			if stepMap, ok := rs.(map[string]interface{}); ok {
				action, _ := stepMap["action"].(string)
				details, _ := stepMap["details"].(string)
				steps = append(steps, models.StepAction{Action: action, Details: details})
			}
		}
	}

	codeFix, _ := llmData["code_fix"].(string)
	summary, _ := llmData["summary"].(string)
	expectedImpact, _ := llmData["expected_impact"].(string)

	if summary == "" {
		summary = "Recomendação gerada por LLM."
	}
	if expectedImpact == "" {
		expectedImpact = "Revisar em ambiente de teste."
	}

	return models.Recommendation{
		AnomalyType:    report.AnomalyType,
		Confidence:     0.6,
		Summary:        summary,
		Steps:          steps,
		CodeFix:        codeFix,
		ExpectedImpact: expectedImpact,
	}
}

// fallbackError retorna uma recomendação de erro quando o LLM falha.
func fallbackError(report models.AnomalyReport, err error) models.Recommendation {
	return models.Recommendation{
		AnomalyType:    report.AnomalyType,
		Confidence:     0.2,
		Summary:        fmt.Sprintf("Falha ao consultar LLM: %v. Revisão manual necessária.", err),
		Steps:          []models.StepAction{{Action: "Revisar métricas manualmente", Details: err.Error()}},
		ExpectedImpact: "Indeterminado.",
	}
}

// toJSON converte um valor para string JSON.
func toJSON(v interface{}) string {
	b, err := json.Marshal(v)
	if err != nil {
		return "{}"
	}
	return string(b)
}

// extractJSON tenta extrair um objeto JSON de uma string.
func extractJSON(content string) (map[string]interface{}, error) {
	// Tenta parsear diretamente
	var data map[string]interface{}
	if err := json.Unmarshal([]byte(content), &data); err == nil {
		return data, nil
	}

	// Tenta extrair bloco JSON com regex
	re := regexp.MustCompile(`(?s)\{.*\}`)
	match := re.FindString(content)
	if match == "" {
		return nil, fmt.Errorf("não foi possível extrair JSON da resposta")
	}

	if err := json.Unmarshal([]byte(match), &data); err != nil {
		return nil, fmt.Errorf("JSON extraído é inválido: %w", err)
	}
	return data, nil
}

// GetRecommendations consulta o CREI (se disponível) ou usa fallback T1.
func (r *Recommender) GetRecommendations(appID string, jobData map[string]interface{}) models.RecommendationSet {
	creiResp := r.callCREI(appID, jobData)
	if creiResp != nil {
		return *creiResp
	}
	return r.buildFallbackDiagnosis(appID, jobData)
}

// callCREI chama o serviço CREI via HTTP.
func (r *Recommender) callCREI(appID string, jobData map[string]interface{}) *models.RecommendationSet {
	if r.CREIURL == "" {
		return nil
	}

	payload := map[string]interface{}{
		"app_id":       appID,
		"job_data":     jobData,
		"request_type": "diagnosis",
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return nil
	}

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Post(r.CREIURL+"/analyze", "application/json", bytes.NewReader(body))
	if err != nil {
		return nil
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil
	}

	var data map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return nil
	}

	stages, _ := jobData["stages"].([]interface{})
	tasks, _ := jobData["tasks"].([]interface{})
	anomalies, _ := jobData["anomalies"].([]interface{})

	return &models.RecommendationSet{
		AppID:  appID,
		Source: "crei",
		Diagnosis: getString(data, "diagnosis", "N/A"),
		RootCauses: toStringSlice(data["root_cause"]),
		Recommendations: toStringSlice(data["recommendations"]),
		Runbook: &models.RunbookResult{
			Steps:      toStringSlice(data["runbook_steps"]),
			CodeFix:    getString(data, "code_fix", ""),
			Validation: getString(data, "validation", ""),
		},
		Confidence: getFloat(data, "confidence", 0.0),
		JobDataSummary: models.JobDataSummary{
			TotalEvents:    getInt(jobData, "total_events", 0),
			StagesCount:    len(stages),
			TasksCount:     len(tasks),
			AnomaliesCount: len(anomalies),
		},
	}
}

// buildFallbackDiagnosis constrói diagnóstico local baseado em regras T1.
func (r *Recommender) buildFallbackDiagnosis(appID string, jobData map[string]interface{}) models.RecommendationSet {
	anomalies, _ := jobData["anomalies"].([]interface{})
	stages, _ := jobData["stages"].([]interface{})
	tasks, _ := jobData["tasks"].([]interface{})
	metrics, _ := jobData["metrics_summary"].([]interface{})

	var diagnosisParts []string
	var rootCauses []string
	var recommendations []string
	runbookResult := &models.RunbookResult{
		Steps:      []string{},
		CodeFix:    "",
		Validation: "",
	}
	severity := "low"

	if len(anomalies) > 0 {
		severity = "high"
		for _, a := range anomalies {
			if anomalyMap, ok := a.(map[string]interface{}); ok {
				detail, _ := anomalyMap["detail"].(string)
				typ, _ := anomalyMap["type"].(string)
				suggestion, _ := anomalyMap["suggestion"].(string)
				if detail != "" {
					diagnosisParts = append(diagnosisParts, detail)
				}
				if typ != "" {
					rootCauses = append(rootCauses, typ)
				}
				if suggestion != "" {
					recommendations = append(recommendations, suggestion)
				}

				// Runbook específico por tipo de anomalia
				if typ == "data_skew" {
					runbookResult.Steps = []string{
						"1. Verificar distribuição da chave de join via countByKey",
						"2. Aplicar salting na chave: key + '_' + rand(0, N)",
						"3. Re-executar job e comparar duração das tasks",
						"4. Se persistir, avaliar broadcast join para smaller dataset",
					}
					runbookResult.CodeFix = `# Exemplo de salting na chave de join
from pyspark.sql.functions import rand, concat, lit

salt_count = 10
orders = orders.withColumn(
    "salted_key",
    concat("customer_id", lit("_"), (rand(42) * salt_count).cast("int"))
)
customers = customers.withColumn(
    "salted_key",
    explode(array([lit(f"_{i}") for i in range(salt_count)]))
).withColumn("salted_key", concat("customer_id", "salted_key"))

result = orders.join(customers, "salted_key", "inner")
`
					runbookResult.Validation = "Comparar max/median task duration antes e depois; skew ratio < 3x é aceitável"
				} else if typ == "spill" {
					runbookResult.Steps = []string{
						"1. Verificar spark.executor.memory e memory.fraction",
						"2. Aumentar spark.memory.fraction para 0.8 se executor tiver > 8GB",
						"3. Considerar broadcast join para datasets < 10MB",
						"4. Monitorar 'spill (memory)' no Spark UI",
					}
					runbookResult.CodeFix = `# Exemplo de broadcast join para smaller dataset
from pyspark.sql.functions import broadcast

result = large_df.join(broadcast(small_df), "join_key", "inner")
`
					runbookResult.Validation = "Verificar no Spark UI que 'Spill (Memory)' = 0 após correção"
				}
			}
		}
	} else {
		diagnosisParts = append(diagnosisParts, "Nenhuma anomalia detectada pelas regras T1.")
		rootCauses = append(rootCauses, "no_anomaly")
		recommendations = append(recommendations, "Monitorar métricas de baseline")
	}

	if len(stages) > 0 {
		var totalDur int64
		for _, s := range stages {
			if stageMap, ok := s.(map[string]interface{}); ok {
				if dur, ok := stageMap["duration_ms"].(float64); ok {
					totalDur += int64(dur)
				}
			}
		}
		diagnosisParts = append(diagnosisParts, fmt.Sprintf("Job executou %d stage(s) em %dms total.", len(stages), totalDur))
	}

	confidence := 0.95
	if len(anomalies) > 0 {
		confidence = 0.75
	}

	return models.RecommendationSet{
		AppID:           appID,
		Source:          "t1_fallback",
		Diagnosis:       strings.Join(diagnosisParts, " | "),
		RootCauses:      uniqueStrings(rootCauses),
		Recommendations: uniqueStrings(recommendations),
		Runbook:         runbookResult,
		Confidence:      confidence,
		JobDataSummary: models.JobDataSummary{
			TotalEvents:    getInt(jobData, "total_events", 0),
			StagesCount:    len(stages),
			TasksCount:     len(tasks),
			AnomaliesCount: len(anomalies),
			MetricsSample:  sliceFirstN(metrics, 5),
		},
	}
}

// Helpers para extração de dados genéricos
func getString(m map[string]interface{}, key, def string) string {
	if v, ok := m[key].(string); ok {
		return v
	}
	return def
}

func getFloat(m map[string]interface{}, key string, def float64) float64 {
	if v, ok := m[key].(float64); ok {
		return v
	}
	return def
}

func getInt(m map[string]interface{}, key string, def int) int {
	if v, ok := m[key].(float64); ok {
		return int(v)
	}
	if v, ok := m[key].(int); ok {
		return v
	}
	return def
}

func toStringSlice(v interface{}) []string {
	if arr, ok := v.([]interface{}); ok {
		var out []string
		for _, item := range arr {
			if s, ok := item.(string); ok {
				out = append(out, s)
			}
		}
		return out
	}
	return []string{}
}

func uniqueStrings(in []string) []string {
	seen := make(map[string]bool)
	var out []string
	for _, s := range in {
		if !seen[s] {
			seen[s] = true
			out = append(out, s)
		}
	}
	return out
}

func sliceFirstN(in []interface{}, n int) []interface{} {
	if len(in) <= n {
		return in
	}
	return in[:n]
}
