int main(int argc, char **argv) {

    int a = 0;

#if defined(A)
    #if defined(D)
    a = 1;
    #endif
#endif

#if defined(C)
    a++;
#endif

    return a;
}