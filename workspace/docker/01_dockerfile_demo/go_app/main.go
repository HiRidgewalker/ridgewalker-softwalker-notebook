// 最小 Go HTTP 服务，用于演示多阶段构建
package main

import (
	"fmt"
	"net/http"
	"os"
	"time"
)

func main() {
	startedAt := time.Now().Format(time.RFC3339)
	addr := ":8080"
	if a := os.Getenv("ADDR"); a != "" {
		addr = a
	}

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "hello from go container\nstarted=%s\naddr=%s\n", startedAt, r.URL.Path)
	})

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		fmt.Fprintln(w, "ok")
	})

	fmt.Printf("listening on %s\n", addr)
	if err := http.ListenAndServe(addr, nil); err != nil {
		panic(err)
	}
}
