#include <stdio.h>

// http://chris35wills.github.io/parabola_python/

int main(int argc, char **argv) // (int argc, char *argv[])
{
    for (int i = 1; i < argc; i++)
    {
        printf("Argument %d: [%s]\n", i, argv[i]); 
    }
    return 0;
}