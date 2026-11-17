// Barrot Go server: minimal, standard library only.
//
//	GET /health  200 {"status":"ok"}
//	GET /status  200 service, uptime, platform
//	else         404 JSON
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"runtime"
	"time"
)

var started = time.Now()

type healthResponse struct {
	Status string `json:"status"`
	Time   string `json:"time"`
}

type statusResponse struct {
	Service  string  `json:"service"`
	Version  string  `json:"version"`
	Platform string  `json:"platform"`
	Uptime   float64 `json:"uptime_seconds"`
}

func writeJSON(w http.ResponseWriter, code int, payload any) {
	body, err := json.MarshalIndent(payload, "", "  ")
	if err != nil {
		http.Error(w, `{"error":"encode failed"}`, http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	_, _ = w.Write(body)
}

func handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			writeJSON(w, http.StatusMethodNotAllowed, map[string]string{"error": "method not allowed"})
			return
		}
		writeJSON(w, http.StatusOK, healthResponse{Status: "ok", Time: time.Now().UTC().Format(time.RFC3339)})
	})
	mux.HandleFunc("/status", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, statusResponse{
			Service:  "barrot-go",
			Version:  "1",
			Platform: runtime.GOOS + "/" + runtime.GOARCH,
			Uptime:   time.Since(started).Seconds(),
		})
	})
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusNotFound, map[string]string{"error": "not found", "path": r.URL.Path})
	})
	return mux
}

func main() {
	host := flag.String("host", "127.0.0.1", "bind address")
	port := flag.Int("port", 8135, "listen port")
	flag.Parse()

	addr := fmt.Sprintf("%s:%d", *host, *port)
	srv := &http.Server{
		Addr:              addr,
		Handler:           handler(),
		ReadHeaderTimeout: 5 * time.Second,
	}
	fmt.Printf("BARROT GO SERVER listening on http://%s\n", addr)
	log.Fatal(srv.ListenAndServe())
}
