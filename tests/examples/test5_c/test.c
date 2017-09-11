int main(int argc, char **argv) {

    int a = 0;

#if defined(A) && defined(B)
    #define E(x) (x * x)
    #if defined(D)
    #define F(x) (x + x)
    #endif
#endif

#if defined(C)
    a++;
#endif

#if defined(E)
    a = E(2);
#endif

    return a;
}