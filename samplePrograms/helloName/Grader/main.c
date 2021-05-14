#include <stdio.h>

#define MAX_NAME_LENGTH 1024

int main() {
    char name[MAX_NAME_LENGTH];
    printf("Hello, please enter your name: ");
    scanf("%s", name);
    printf("Hello %s! It's good to meet you.\n", name);
    return 0;
}