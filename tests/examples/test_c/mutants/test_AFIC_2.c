#if defined(A)
char character = 'a';
#endif

int main(int argc, char **argv) {

    int a = 0;

#if defined(B) && defined(D)
    a = 1;
    #if defined(C)
    a = 2;
    #endif
#endif

    return a;
}