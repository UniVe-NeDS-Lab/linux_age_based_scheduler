#include "threshold_update.h"

int main(void){

	uint64_t data = 0 ;
	bool debug = 1;
	struct mnl_socket *nl;
	nl = set_up(1);

	if (debug){
		printf("Socket opened, starting to catch events\n");
        }

	while (1) {
		data = get_bytes(nl, debug);
		if (data != 0){
			if (debug){
				printf("==== total bytes = %lu\n", data);
			}
		}
	}
	tear_down(nl);
}
