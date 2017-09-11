#if defined(A) && defined(D)
char character = 'a';
#endif

int main(int argc, char **argv) {

    int a = 0;

#if defined(B)
    a = 1;
    #if defined(C)
    a = 2;
    #endif
#endif

    return a;
}