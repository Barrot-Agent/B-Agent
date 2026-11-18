/*
 * Fuzz target — bug class 6: integer/length field leading to a buffer overflow.
 *
 * Format: "FUZZ" + uint16 length + payload.
 * The length is taken from the file and used as the copy size without being
 * compared to the destination. This is the shape behind an entire family of
 * real overflows: a length that is trusted because it came from a struct.
 *
 * Build:
 *   gcc -O0 -g -fstack-protector-strong -o target_overflow target_overflow.c
 *
 * Deliberately vulnerable. Sandbox only. Not built into anything.
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

    char buf[DEST_SIZE];
    memset(buf, 0, sizeof(buf));
    /* The bug: len is compared to nothing. */
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
