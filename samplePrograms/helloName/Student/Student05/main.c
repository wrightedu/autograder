#include <stdio.h>
#include <stdlib.h>

#define MAX_NAME_LENGTH 1024

int main() {
    char *name = (char *)malloc(20);
    printf("Hello, please enter your name: ");
    fflush(stdout);
    scanf("%s", name);
    printf("Hello %s! It's good to meet you.\n", name);
    free(name);
    return 0;
}