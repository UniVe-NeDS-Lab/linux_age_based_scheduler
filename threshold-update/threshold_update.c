#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>

#include <libmnl/libmnl.h>
#include <libnetfilter_conntrack/libnetfilter_conntrack.h>

static int data_cb(const struct nlmsghdr *nlh, void *data)
{
	struct nf_conntrack *ct;
	uint32_t type = NFCT_T_UNKNOWN;
	uint64_t *data_int = data;
	char buf[4096];
	switch(nlh->nlmsg_type & 0xFF) {
	case IPCTNL_MSG_CT_NEW:
		if (nlh->nlmsg_flags & (NLM_F_CREATE|NLM_F_EXCL))
			type = NFCT_T_NEW;
		else
			type = NFCT_T_UPDATE;
		break;
	case IPCTNL_MSG_CT_DELETE:
		type = NFCT_T_DESTROY;
		break;
	}

	ct = nfct_new();
	if (ct == NULL)
		return MNL_CB_OK;

	nfct_nlmsg_parse(nlh, ct);

	const uint64_t *recv_bytes = nfct_get_attr(ct, ATTR_ORIG_COUNTER_BYTES);
	const uint64_t *sent_bytes = nfct_get_attr(ct, ATTR_REPL_COUNTER_BYTES);

	nfct_snprintf(buf, sizeof(buf), ct,
			type, NFCT_O_DEFAULT, 0);
	printf("%s\n", buf);

	if (recv_bytes != NULL || sent_bytes != NULL){
		*data_int = (int)(*recv_bytes + *sent_bytes);
	} else {
		return 0;
	}
	nfct_destroy(ct);

	return MNL_CB_OK;
}


int get_bytes(struct mnl_socket *nl, bool debug){

	int ret;
	char buf[MNL_SOCKET_BUFFER_SIZE];
	uint64_t data = 0 ;

	ret = mnl_socket_recvfrom(nl, buf, sizeof(buf));
	if (ret == -1) {
		perror("mnl_socket_recvfrom");
		exit(EXIT_FAILURE);
	}

	ret = mnl_cb_run(buf, ret, 0, 0, data_cb, &data);
	if (ret == -1) {
		perror("mnl_cb_run");
		exit(EXIT_FAILURE);
	}
	
	return data;
}


struct mnl_socket * set_up(bool debug)
{
	struct mnl_socket *nl;
	struct nfct_filter *ft;
	int fd;

	nl = mnl_socket_open(NETLINK_NETFILTER);
	
	if (nl == NULL) {
		perror("mnl_socket_open");
		exit(EXIT_FAILURE);
	}
	
	fd = mnl_socket_get_fd(nl);
	ft = nfct_filter_create();
        nfct_filter_add_attr_u32(ft, NFCT_FILTER_L4PROTO, IPPROTO_TCP);
        nfct_filter_set_logic(ft,
                              NFCT_FILTER_SRC_IPV4,
                              NFCT_FILTER_LOGIC_POSITIVE);

        if (nfct_filter_attach(fd, ft) == -1) {
                perror("nfct_filter_attach");
                return 0;
        }


	if (mnl_socket_bind(nl, NF_NETLINK_CONNTRACK_DESTROY,
				MNL_SOCKET_AUTOPID) < 0) {
		perror("mnl_socket_bind");
		exit(EXIT_FAILURE);
	}

	/* 
	 * this will catch some more events 
        
	if (mnl_socket_bind(nl, NF_NETLINK_CONNTRACK_NEW |
                                NF_NETLINK_CONNTRACK_UPDATE |
                                NF_NETLINK_CONNTRACK_DESTROY,
                                MNL_SOCKET_AUTOPID) < 0) {
                perror("mnl_socket_bind");
                exit(EXIT_FAILURE);
        }
	*/


	return nl;
}


void tear_down(struct mnl_socket * nl){
	mnl_socket_close(nl);
}


