package clickhouse

import (
	"fmt"
	"strconv"
)

// ═══════════════════════════════════════════════════════════
// Helpers de conversão de resultado genérico para tipos Go
// ═══════════════════════════════════════════════════════════

// ToString converte um valor interface{} para string.
func ToString(v interface{}) string {
	if v == nil {
		return ""
	}
	if s, ok := v.(string); ok {
		return s
	}
	return fmt.Sprintf("%v", v)
}

// ToInt64 converte um valor interface{} para int64.
func ToInt64(v interface{}) int64 {
	if v == nil {
		return 0
	}
	switch val := v.(type) {
	case int64:
		return val
	case int:
		return int64(val)
	case int32:
		return int64(val)
	case float64:
		return int64(val)
	case string:
		if i, err := strconv.ParseInt(val, 10, 64); err == nil {
			return i
		}
		return 0
	default:
		return 0
	}
}

// ToFloat64 converte um valor interface{} para float64.
func ToFloat64(v interface{}) float64 {
	if v == nil {
		return 0
	}
	switch val := v.(type) {
	case float64:
		return val
	case int64:
		return float64(val)
	case int:
		return float64(val)
	case string:
		if f, err := strconv.ParseFloat(val, 64); err == nil {
			return f
		}
		return 0
	default:
		return 0
	}
}

// ToStringSlice converte um valor interface{} (slice) para []string.
func ToStringSlice(v interface{}) []string {
	if v == nil {
		return nil
	}
	if arr, ok := v.([]interface{}); ok {
		result := make([]string, len(arr))
		for i, item := range arr {
			result[i] = ToString(item)
		}
		return result
	}
	return nil
}

// GetColumnIndex retorna o índice de uma coluna pelo nome (case-insensitive).
func GetColumnIndex(columns []string, name string) int {
	for i, col := range columns {
		if col == name {
			return i
		}
	}
	return -1
}

// GetValue retorna o valor de uma coluna em uma linha, dado o nome da coluna.
func GetValue(row []interface{}, columns []string, name string) interface{} {
	idx := GetColumnIndex(columns, name)
	if idx >= 0 && idx < len(row) {
		return row[idx]
	}
	return nil
}

// GetString retorna o valor string de uma coluna em uma linha.
func GetString(row []interface{}, columns []string, name string) string {
	return ToString(GetValue(row, columns, name))
}

// GetInt64 retorna o valor int64 de uma coluna em uma linha.
func GetInt64(row []interface{}, columns []string, name string) int64 {
	return ToInt64(GetValue(row, columns, name))
}

// GetFloat64 retorna o valor float64 de uma coluna em uma linha.
func GetFloat64(row []interface{}, columns []string, name string) float64 {
	return ToFloat64(GetValue(row, columns, name))
}

// GetStringSlice retorna o valor []string de uma coluna em uma linha.
func GetStringSlice(row []interface{}, columns []string, name string) []string {
	return ToStringSlice(GetValue(row, columns, name))
}

// JSONMapString converte um JSONResult.Data row para map[string]string.
func JSONMapString(row map[string]interface{}) map[string]string {
	result := make(map[string]string, len(row))
	for k, v := range row {
		result[k] = ToString(v)
	}
	return result
}

// JSONMapInt64 converte um JSONResult.Data row para map[string]int64.
func JSONMapInt64(row map[string]interface{}) map[string]int64 {
	result := make(map[string]int64, len(row))
	for k, v := range row {
		result[k] = ToInt64(v)
	}
	return result
}

// JSONMapFloat64 converte um JSONResult.Data row para map[string]float64.
func JSONMapFloat64(row map[string]interface{}) map[string]float64 {
	result := make(map[string]float64, len(row))
	for k, v := range row {
		result[k] = ToFloat64(v)
	}
	return result
}
