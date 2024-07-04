#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>

#include <libmnl/libmnl.h>
#include <libnetfilter_conntrack/libnetfilter_conntrack.h>

static int _data_cb(const struct nlmsghdr *nlh, void *data);
int _get_bytes(struct mnl_socket *nl, bool debug);
struct mnl_socket * _set_up(bool debug);
void _tear_down(struct mnl_socket * nl);
