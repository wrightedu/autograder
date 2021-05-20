#include <stdio.h>
#include <stdlib.h>

int main() {
    char *name = NULL;
    size_t l = 0;
    printf("Hello, please enter your name: ");
    getline(&name, &l, stdin);
    printf("Hello %s! It's good to meet you.\n", name);
    free(name);
    return 0;
}