#include <stdio.h>
#include <stdlib.h>

#define MAX_NAME_LENGTH 1024

int main() {
    char *name = NULL;
    size_t len = 0;
    printf("Hello, please enter your name: ");
    getline(&name, &len, stdin);
    printf("Hello %s! It's good to meet you.\n", name + 2);
    free(name);
    return 0;
}