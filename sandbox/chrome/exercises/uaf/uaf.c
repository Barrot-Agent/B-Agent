/*
 * Exercise 1 — use-after-free, modelled with a quarantine allocator.
 *
 * AddressSanitizer does not run in this environment:
 *   AddressSanitizer: CHECK failed: sanitizer_allocator_primary64.h:131
 * so this exercise replaces ASAN's shadow memory with the smallest honest
 * equivalent: a header per block that records FREE or LIVE, a poison byte
 * written on free, and blocks that are never reused. A write after free is
 * therefore visible as a poison byte that changed while the header still says
 * the block is free.
 *
 * This is a model of ASAN, not ASAN. It catches the exercise; it would not
 * catch every real UAF, because it only inspects the blocks the program tells
 * it about.
 *
 * Build and run:
 *   gcc -O0 -g -o uaf uaf.c
 *   ./uaf          # vulnerable: detector fires, exit 1
 *   ./uaf --fixed  # repaired: exit 0
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define POISON 0xDD
#define MAGIC 0xB16B00B5u

typedef struct {
    unsigned int magic;
    size_t size;
    int state; /* 0 = LIVE, 1 = FREE */
} header_t;

static size_t g_live = 0;
static size_t g_free = 0;
static size_t g_uaf_hits = 0;

static void *q_alloc(size_t size) {
    header_t *h = (header_t *)malloc(sizeof(header_t) + size);
    if (!h) {
        return NULL;
    }
    h->magic = MAGIC;
    h->size = size;
    h->state = 0;
    memset((char *)h + sizeof(header_t), 0, size);
    g_live++;
    return (char *)h + sizeof(header_t);
}

static header_t *hdr(void *ptr) {
    header_t *h = (header_t *)((char *)ptr - sizeof(header_t));
    if (h->magic != MAGIC) {
        fprintf(stderr, "  [detector] bad header: not a q_alloc block\n");
        return NULL;
    }
    return h;
}

static void q_free(void *ptr) {
    header_t *h = hdr(ptr);
    if (!h) {
        return;
    }
    if (h->state == 1) {
        fprintf(stderr, "  [detector] DOUBLE-FREE of %p\n", ptr);
        g_uaf_hits++;
        return;
    }
    /* Quarantine: poison and mark free, but never hand the block back. */
    memset(ptr, POISON, h->size);
    h->state = 1;
    g_live--;
    g_free++;
}

/* Call after touching a block. Reports the use, it does not prevent it. */
static void q_check(void *ptr, const char *what) {
    header_t *h = hdr(ptr);
    if (!h) {
        return;
    }
    if (h->state != 1) {
        return;
    }
    unsigned char *bytes = (unsigned char *)ptr;
    size_t changed = 0;
    for (size_t i = 0; i < h->size; i++) {
        if (bytes[i] != POISON) {
            changed++;
        }
    }
    if (changed == 0) {
        printf("  [detector] use-after-free READ of %p (%s), %zu bytes\n",
               ptr, what, h->size);
    } else {
        printf("  [detector] use-after-free WRITE of %p (%s), %zu of %zu bytes clobbered\n",
               ptr, what, changed, h->size);
    }
    g_uaf_hits++;
}

/*
 * The vulnerable shape: the pointer is freed, then reused through the stale
 * reference because nothing cleared it. This is the whole bug class — ownership
 * ends, the reference does not.
 */
static int vulnerable(void) {
    char *buf = (char *)q_alloc(32);
    if (!buf) {
        return 1;
    }
    strcpy(buf, "session-token-A");
    printf("  session: %s\n", buf);
    q_free(buf);
    /* Stale reference. A real target would have this in another object. */
    strcpy(buf, "attacker-controlled");
    q_check(buf, "stale reference after q_free");
    return 0;
}

/* The repair: end the reference at the same time as the ownership. */
static int repaired(void) {
    char *buf = (char *)q_alloc(32);
    if (!buf) {
        return 1;
    }
    strcpy(buf, "session-token-A");
    printf("  session: %s\n", buf);
    q_free(buf);
    buf = NULL;
    if (buf != NULL) {
        strcpy(buf, "unreachable");
    }
    /* Nothing to check: no reference outlived the free. */
    return 0;
}

int main(int argc, char **argv) {
    int fixed = (argc > 1 && strcmp(argv[1], "--fixed") == 0);
    printf("exercise 1: use-after-free (%s)\n", fixed ? "repaired" : "vulnerable");
    int rc = fixed ? repaired() : vulnerable();
    printf("  live=%zu quarantined=%zu uaf_hits=%zu\n", g_live, g_free, g_uaf_hits);
    if (g_uaf_hits > 0) {
        printf("  RESULT: BUG DETECTED\n");
        return 1;
    }
    printf("  RESULT: clean\n");
    return rc;
}
