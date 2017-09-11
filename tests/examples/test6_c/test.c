#ifndef HEADER_SSL_LOCL_
#define IMPLEMENT_ssl3_meth_func(func_name) \
const int *func_name(void) { return 0; }

#define IMPLEMENT_tls_meth_func(func_name) \
const int *func_name(void) { return 0; }
#endif

#ifndef OPENSSL_NO_TLS1_METHOD
IMPLEMENT_tls_meth_func(tlsv1_server_method)
#endif
#ifndef OPENSSL_NO_SSL3_METHOD
IMPLEMENT_ssl3_meth_func(sslv3_server_method)
#endif
