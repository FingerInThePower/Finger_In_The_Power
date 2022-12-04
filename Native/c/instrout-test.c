
#include <stdio.h>
#include <stdint.h>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/signal.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/wait.h>
#if defined(__x86_64__)
#include <x86intrin.h>
#endif

#define WRITERFAILSTRING "WRITER DIED"
#define QUIET 1

#include "profile.h"

/* out-of-band signaling */
volatile struct sharestruct *sharestruct;

/* which signal do we use to make the child exit cleanly? */
#define SIGENDCHILD SIGTERM

/* How many samples? */
#define MAXTIME 100000

#include "tvlb.h"


extern uint64_t readlabels, writelabels;
extern uint64_t readlabels_number, writelabels_number;
extern uint64_t readstringlabels, readstringlabels_number;
extern uint64_t writestringlabels, writestringlabels_number;


int main(int argc, char *argv[])
{
        uint64_t *r, *str;
        typedef uint32_t (*func)(void);
        uint64_t *functable_readers = (uint64_t *) &readlabels;
        uint64_t *stringtable = (uint64_t *) &readstringlabels;

        uint64_t *functable_writing = (uint64_t *) &writelabels;

        static unsigned int measurements_data[MAXTIME];

        uint64_t tablesize = readlabels_number;
        assert(tablesize == writestringlabels_number);
        assert(tablesize == writelabels_number);
        assert(tablesize == readstringlabels_number);
        assert(tablesize == readlabels_number);

        assert((uint64_t *) functable_readers[0] == NULL);

        int *z = NULL;

        if(argc == 2 && !strcmp(argv[1], "available")) {

                int i;
                printf("{ 'writerfailstring': '%s', 'available': [ ", WRITERFAILSTRING);
                for(i = 0; i < tablesize; i++) {
                        if(functable_readers[i]) printf("%d,", i);
                 }
                printf("] }\n");
                return 0;
        }

        if(argc < 5) {
                fprintf(stderr,
                    "usage:\n"
                    "  %s available\n"
                    "  %s parent/readcpu child/writecpu writeload measurements warmup [..]\n", argv[0], argv[0]);
                return 1;
        }

        int parentcpu = atoi(argv[1]);
        int childcpu = atoi(argv[2]);
        int writefunction = atoi(argv[3]);
        int measurements = atoi(argv[4]);
        int warmup = atoi(argv[5]);

        assert(parentcpu >= 0);
        assert(childcpu >= 0);
        assert(writefunction >= 0);
        assert(writefunction < tablesize);

        memset((char *) measurements_data, 0, sizeof(measurements_data));
        memset((char *) measurements_data, 0, sizeof(measurements_data));

    /*fprintf(stderr,"pinning parent to CPU %x", parentcpu);*/
	pin_cpu(parentcpu);

        int idx = writefunction;
        printf("This is idx: %d\n",idx);
        assert(idx >= 0);
        assert(idx < tablesize);
        assert(functable_readers[idx]);
        func thisfunc = (func) functable_readers[idx];
        assert(thisfunc);
        char *readstring = (char *) stringtable[idx];
        printf("\"%d\",\"%s\"", idx, readstring);
        fflush(stdout);
        int rep;
        for(rep = 0; rep < measurements; rep++) {
                thisfunc();
        }

        return 0;
}


