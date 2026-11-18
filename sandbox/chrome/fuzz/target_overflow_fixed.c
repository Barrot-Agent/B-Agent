/*
 * Fuzz target, repaired — bug class 6.
 *
 * Change from target_overflow.c: the declared length is validated against the
 * destination size AND against the bytes actually present before any copy. The
 * repair is two conditions, not one, because a length can pass the size check
 * and still describe data that is not there (the 6-byte SIGSEGV case).
 *
 * Build:
 *   gcc -O0 -g -fstack-protector-strong -o target_overflow_fixed target_overflow_fixed.c
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEST_SIZE 16

int parse(const uint8_t *data, size_t size) {
    if (size < 6) {
        return 0;
    }
    char magic[4];
    memcpy(magic, data, 4);
    if (memcmp(magic, "FUZZ", 4) != 0) {
        return 0;
    }
    uint16_t len = 0;
    memcpy(&len, data + 4, sizeof(len));

    /* Repair 1: the declared length must fit the destination. */
    if (len > DEST_SIZE) {
        return 0;
    }
    /* Repair 2: the declared length must be backed by real bytes. */
    if ((size_t)len > size - 6) {
        return 0;
    }

    char buf[DEST_SIZE];
    memset(buf, 0, sizeof(buf));
    memcpy(buf, data + 6, len);
    return (int)buf[0];
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s FILE\n", argv[0]);
        return 2;
    }
    FILE *fp = fopen(argv[1], "rb");
    if (!fp) {
        return 2;
    }
    uint8_t data[4096];
    size_t n = fread(data, 1, sizeof(data), fp);
    fclose(fp);
    return parse(data, n);
}
