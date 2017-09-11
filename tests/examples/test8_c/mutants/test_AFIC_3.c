#ifdef UNIX
#define A
#define B
#define C
#endif

#ifdef A
#if defined(WIN_32)
void a_win_function() {

}
#endif

#ifdef UNIX && POSIX
void a_function() {

}
#endif
#endif

#ifdef B
void b_function(){

}
#endif

#ifdef C
void c_function() {

}
#endif