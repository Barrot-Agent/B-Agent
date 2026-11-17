package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func get(t *testing.T, path string) *httptest.ResponseRecorder {
	t.Helper()
	req := httptest.NewRequest(http.MethodGet, path, nil)
	rec := httptest.NewRecorder()
	handler().ServeHTTP(rec, req)
	return rec
}

func TestHealthReturns200(t *testing.T) {
	rec := get(t, "/health")
	if rec.Code != http.StatusOK {
		t.Fatalf("health status = %d, want 200", rec.Code)
	}
	var body map[string]string
	if err := json.Unmarshal(rec.Body.Bytes(), &body); err != nil {
		t.Fatalf("health body is not json: %v", err)
	}
	if body["status"] != "ok" {
		t.Fatalf("health status field = %q, want ok", body["status"])
	}
}

func TestStatusReturns200(t *testing.T) {
	rec := get(t, "/status")
	if rec.Code != http.StatusOK {
		t.Fatalf("status code = %d, want 200", rec.Code)
	}
	var body statusResponse
	if err := json.Unmarshal(rec.Body.Bytes(), &body); err != nil {
		t.Fatalf("status body is not json: %v", err)
	}
	if body.Service != "barrot-go" {
		t.Fatalf("service = %q", body.Service)
	}
}

func TestUnknownPathReturns404(t *testing.T) {
	rec := get(t, "/nope")
	if rec.Code != http.StatusNotFound {
		t.Fatalf("unknown path status = %d, want 404", rec.Code)
	}
}
