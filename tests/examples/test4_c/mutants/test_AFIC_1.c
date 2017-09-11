#if defined(A) && defined(B)
int sum(int a, int b) {
    return a + b;
}
#endif

int main(int argc, char **argv) {

    int a = 0;
    int b = 1;

#if defined(A)
    a = sum(a, b);
#endif

    return 0;
}